# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timezone
from http.client import OK

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import AS4ProtocolException, AS4SecurityException, EbMSError, Limits, serves_channel, Severity
from zato.common.as4.ebms import build_envelope, build_error, build_receipt, parse_messaging
from zato.common.as4.mime_ import parse_multipart, restore_payloads
from zato.common.as4.security.sign import sign_envelope
from zato.common.as4.security.verify import decrypt_parts, verify_envelope
from zato.common.util.xml_.core import from_timestamp, parse_xml, XMLException, XMLSecurityException
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.token import certificate_common_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import signal_details_list, UserMessageDetails
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, anylist, callnone, strnone, strset
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anylist = anylist
    callnone = callnone
    Keystore = Keystore
    PMode = PMode
    signal_details_list = signal_details_list
    strnone = strnone
    strset = strset
    UserMessageDetails = UserMessageDetails

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
pmode_list = list['PMode']

# ################################################################################################################################
# ################################################################################################################################

_soap_content_type = 'application/soap+xml; charset=UTF-8'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PullServed:
    """ The message one pull request is answered with - what goes on the response of the request
    that asked for it, built by whoever holds the messages of the channel it asked about.
    """
    body:         bytes = b''
    content_type: str = _soap_content_type
    message_id:   str = ''

    # The payloads as they were submitted for pulling, which is what the evidence of the hand-over
    # is written from.
    payloads: 'part_list'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundResult:
    """ What the transport should send back and what the application receives.
    """
    # The HTTP response - a signed receipt on success, an ebMS error signal otherwise.
    status_code:  int = OK
    content_type: str = _soap_content_type
    body:         bytes = b''

    # The parsed user message and its decrypted, decompressed payloads.
    user_message: 'UserMessageDetails | None' = None
    payloads: 'part_list'

    # Whatever the validate callback read out of each payload, one entry per payload, so that
    # a caller that routes the payloads afterwards does not read the same thing again.
    payload_details: 'anylist'

    # Signals delivered to us - asynchronous receipts or errors from a previous exchange.
    signals: 'signal_details_list'

    # For a pull request - the message partition channel it asked about and the message that was
    # handed over on the response, if the channel had one waiting.
    pull_mpc: str = ''
    pulled: 'PullServed | None' = None

    # Whether the message was recognized as a duplicate - the receipt is still returned
    # but the payloads must not be processed a second time.
    is_duplicate: bool = False

    # Whether this message failed and the body is an error signal.
    is_error: bool = False
    error_code: 'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

def _match_pmode(pmodes:'pmode_list', user_message:'UserMessageDetails') -> 'PMode':
    """ Finds the P-Mode that governs an incoming user message by its service and action. A message
    that matches none of the configured P-Modes has no agreed terms to be processed under, which is
    what EBMS:0010 says.
    """
    for pmode in pmodes:
        if pmode.service == user_message.service:
            if pmode.action == user_message.action:
                out = pmode
                break
    else:
        raise AS4ProtocolException(
            EbMSError.Processing_Mode_Mismatch,
            f'No P-Mode is configured for service `{user_message.service}` and action `{user_message.action}`')

    return out

# ################################################################################################################################

def _serialize(envelope:'any_') -> 'bytes':
    """ Serializes a response envelope for the wire.
    """
    out = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def build_error_response(
    ref_to_message_id:'strnone',
    error_code:'str',
    detail:'str',
    keystore:'Keystore | None',
    pmode:'PMode | None',
    severity:'str'=Severity.Failure,
    ) -> 'bytes':
    """ Builds the ebMS error signal that goes back on the HTTP response,
    signing it when the P-Mode calls for signed signals and signing is possible.
    """
    envelope = build_envelope()
    _ = build_error(envelope, ref_to_message_id, error_code, error_code, detail, severity)

    if pmode:
        if keystore:
            if pmode.security.sign_receipts:
                if keystore.signing_key:
                    _ = sign_envelope(envelope, [], keystore, pmode.security)

    out = _serialize(envelope)
    return out

# ################################################################################################################################

def _require_fresh_timestamp(user_message:'UserMessageDetails') -> 'None':
    """ Requires the eb:Timestamp of an incoming message to be within the window around the current
    time. The timestamp is covered by the signature, so a message replayed later than the window
    allows cannot be given a new one.
    """
    try:
        timestamp = from_timestamp(user_message.timestamp)
    except XMLException as e:
        raise AS4ProtocolException(EbMSError.Invalid_Header, f'Could not read eb:Timestamp -> {e.args[0]}')

    now = datetime.now(timezone.utc)
    difference = abs((now - timestamp).total_seconds())

    if difference > Limits.Timestamp_Window_Seconds:
        seconds = int(difference)
        window = Limits.Timestamp_Window_Seconds

        detail = f'eb:Timestamp `{user_message.timestamp}` is {seconds} seconds from now, the window is {window}'
        raise AS4ProtocolException(EbMSError.Value_Inconsistent, detail)

# ################################################################################################################################

def _require_encryption(pmode:'PMode', parts:'part_list', decrypted_content_ids:'strset') -> 'None':
    """ Requires every payload part to have arrived encrypted when the P-Mode says the exchange is
    encrypted. Nothing is required of an exchange whose P-Mode does not encrypt.
    """
    if not pmode.security.encrypt:
        return

    for part in parts:
        if part.content_id not in decrypted_content_ids:
            raise AS4SecurityException(
                EbMSError.Policy_Noncompliance, f'Part `{part.content_id}` did not arrive encrypted')

# ################################################################################################################################

def _require_party_binding(pmode:'PMode', user_message:'UserMessageDetails', certificate:'any_') -> 'None':
    """ Requires the eb:From PartyId to be the common name of the certificate that signed the
    message, for the networks whose P-Mode says the two are the same.
    """
    if not pmode.security.party_id_is_certificate_cn:
        return

    try:
        common_name = certificate_common_name(certificate)
    except XMLSecurityException as e:
        raise AS4SecurityException(EbMSError.Failed_Authentication, e.args[0])

    if common_name != user_message.from_party:
        raise AS4SecurityException(
            EbMSError.Failed_Authentication,
            f'Message claims to be from `{user_message.from_party}` but is signed by `{common_name}`')

# ################################################################################################################################

def _handle_signals(envelope:'any_', messaging:'any_', keystore:'Keystore', out:'InboundResult') -> 'None':
    """ Takes in the signals of a message that carries no user message - receipts and errors that
    arrive on their own, delivered asynchronously after an earlier exchange of ours.
    """

    # A signal says an earlier message of ours was delivered or was refused, so it is required to be
    # signed by the party it claims to come from, exactly as a user message is.
    _ = verify_envelope(envelope, [], keystore)

    for signal in messaging.signals:
        out.signals.append(signal)

# ################################################################################################################################

def _get_pull_request(messaging:'any_') -> 'any_':
    """ Returns the signal asking for a message of one partition channel, or None for a request that
    asks for nothing - a receipt or an error signal delivered on its own.
    """
    for signal in messaging.signals:
        if signal.pull_mpc:
            out = signal
            return out

    return None

# ################################################################################################################################

def _match_pull_pmode(pmodes:'pmode_list', mpc:'str') -> 'PMode':
    """ Finds the P-Mode that governs one message partition channel. A pull request for a channel
    that no P-Mode of this endpoint covers is a request for a channel this endpoint does not have,
    which is as far as it gets - the messages of a channel are only handed over under the terms
    agreed for it.
    """
    for pmode in pmodes:
        if serves_channel(pmode.mpc, mpc):
            out = pmode
            break
    else:
        raise AS4ProtocolException(
            EbMSError.Value_Not_Recognized, f'No P-Mode is configured for message partition channel `{mpc}`')

    return out

# ################################################################################################################################

def _handle_pull_request(
    envelope:'any_',
    signal:'any_',
    pmode:'PMode',
    keystore:'Keystore',
    serve_pull:'callnone',
    out:'InboundResult',
    ) -> 'None':
    """ Answers one pull request with the message that was waiting on the channel it asked about,
    or with the empty channel warning when nothing was.

    A pull request names no party of its own, so its signature is what says who is asking and the
    keystore is what says whether that party is who it claims to be.
    """
    mpc = signal.pull_mpc
    out.pull_mpc = mpc

    # The request is authenticated before anything is looked up, let alone handed over.
    _ = verify_envelope(envelope, [], keystore)

    if serve_pull is None:
        raise AS4ProtocolException(EbMSError.Feature_Not_Supported, 'This endpoint does not serve pull requests')

    served = serve_pull(mpc, pmode)

    # A channel with nothing waiting on it is answered with the warning ebMS 3.0 defines for it,
    # which is what tells the partner to come back later rather than that something went wrong.
    if served is None:
        detail = f'No message is available on `{mpc}`'
        out.body = build_error_response(signal.message_id, EbMSError.Empty_Message_Partition, detail,
            keystore, pmode, Severity.Warning)
        return

    out.pulled = served
    out.content_type = served.content_type
    out.body = served.body

# ################################################################################################################################

# ################################################################################################################################

def handle(
    body:'bytes',
    content_type:'str',
    pmodes:'pmode_list',
    keystore:'Keystore',
    is_duplicate:'callnone'=None,
    validate:'callnone'=None,
    serve_pull:'callnone'=None,
    ) -> 'InboundResult':
    """ The transport-neutral inbound pipeline. Takes the raw HTTP body and content type
    of an incoming AS4 request and returns what to send back plus the delivered payloads.

    The is_duplicate callable, when given, receives an eb:MessageId and returns True
    if that message was already processed - the receipt is then repeated without
    delivering the payloads again.

    The validate callable, when given, receives the user message and the restored payloads
    once their signature is verified - it raises AS4ProtocolException to reject the message,
    which turns into a signed ebMS error signal on the response.

    The serve_pull callable, when given, receives a message partition channel and the P-Mode that
    governs it, and returns the message waiting on that channel, or None when none is - which is
    what makes this endpoint a responder to pull requests rather than one that refuses them.
    """

    # Our response to produce
    out = InboundResult()
    out.payloads = []
    out.payload_details = []
    out.signals = []

    ref_to_message_id:'strnone' = None

    # The P-Mode is looked up mid-pipeline - this keeps it reachable for the error path below.
    matched_pmode:'PMode | None' = None

    try:
        # Take the envelope and attachments apart ..
        envelope_bytes, parts = parse_multipart(body, content_type)

        try:
            envelope = parse_xml(envelope_bytes)
        except XMLException as e:
            raise AS4ProtocolException(EbMSError.Invalid_Header, f'Could not parse the SOAP envelope -> {e}')

        messaging = parse_messaging(envelope)

        # Signals without a user message are receipts or errors delivered to us asynchronously -
        # they are surfaced to the caller and acknowledged with an empty response. One of them asks
        # for a message rather than reporting on one, and that one is answered here and now.
        if not messaging.user_messages:

            pull_request = _get_pull_request(messaging)

            if pull_request:
                ref_to_message_id = pull_request.message_id
                matched_pmode = _match_pull_pmode(pmodes, pull_request.pull_mpc)
                _handle_pull_request(envelope, pull_request, matched_pmode, keystore, serve_pull, out)
            else:
                _handle_signals(envelope, messaging, keystore, out)

            return out

        user_message = messaging.user_messages[0]
        ref_to_message_id = user_message.message_id

        pmode = _match_pmode(pmodes, user_message)
        matched_pmode = pmode

        # Reverse the security processing - decrypt the wire bytes first,
        # then verify the signature that covers the plaintext ..
        decrypted_content_ids = decrypt_parts(envelope, parts, keystore)
        verify_result = verify_envelope(envelope, parts, keystore)

        # .. hold the message to the P-Mode's own policy, which the message itself cannot state ..
        _require_encryption(pmode, parts, decrypted_content_ids)
        _require_party_binding(pmode, user_message, verify_result.signer_certificate)

        # .. the timestamp is only worth checking once it is known to be the signed one ..
        _require_fresh_timestamp(user_message)

        # .. restore the payloads to what the sender submitted ..
        payloads = restore_payloads(user_message, parts)

        # .. give the caller a chance to reject the message on business grounds,
        # .. e.g. a receiver that this endpoint does not serve ..
        payload_details:'anylist' = []

        if validate:
            payload_details = validate(user_message, payloads)

        # .. and only deliver them if this is not a replay of a message we already have.
        if is_duplicate:
            out.is_duplicate = is_duplicate(user_message.message_id)

        if not out.is_duplicate:
            out.user_message = user_message
            out.payloads = payloads
            out.payload_details = payload_details

        # The receipt echoes the verified references - that is the non-repudiation proof.
        receipt_envelope = build_envelope()
        _ = build_receipt(receipt_envelope, user_message.message_id, verify_result.signed_references)

        if pmode.security.sign_receipts:
            _ = sign_envelope(receipt_envelope, [], keystore, pmode.security)

        out.body = _serialize(receipt_envelope)

    except AS4ProtocolException as e:
        out.is_error = True
        out.error_code = e.error_code
        out.body = build_error_response(ref_to_message_id, e.error_code, e.detail, keystore, matched_pmode)

    return out

# ################################################################################################################################
# ################################################################################################################################
