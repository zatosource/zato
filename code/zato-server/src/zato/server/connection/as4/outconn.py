# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import copy, deepcopy
from threading import RLock

# cryptography
from cryptography.x509 import load_der_x509_certificate

# httpx
import httpx

# Zato
from zato.common.api import AS4
from zato.common.as4.audit import record_pull_result, record_send_result
from zato.common.as4.common import AS4Exception, Default
from zato.common.as4.config import apply_credentials, apply_reception_awareness, build_keystore, build_pmode
from zato.common.as4.discovery import lookup_endpoint, SML_Domain_Production
from zato.common.as4.mpc import queue_message
from zato.common.as4.outbound import new_part, pull as outbound_pull, send as outbound_send
from zato.common.as4.presets import get_document_type_preset
from zato.common.as4.profiles import Peppol_Participant_ID_Type
from zato.common.as4.sbdh import build_sbdh
from zato.common.audit_log.api import AuditLog
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_
from zato.common.util.xml_.core import parse_xml
from zato.common.util.xml_.token import certificate_common_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.as4.outbound import PullResult, SendResult
    from zato.common.as4.pmode import PMode
    from zato.common.as4.presets import DocumentTypePreset
    from zato.common.as4.resend import ResendCandidate
    from zato.common.typing_ import anylist, anytuple, stranydict, strbytes, strlist, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import part_list
    from zato.server.base.parallel import ParallelServer
    anylist = anylist
    anytuple = anytuple
    strlist = strlist
    Certificate = Certificate
    DocumentTypePreset = DocumentTypePreset
    part_list = part_list
    PullResult = PullResult
    ResendCandidate = ResendCandidate
    SendResult = SendResult

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many bits of randomness go into an SBDH instance identifier.
_instance_identifier_bits = 128

# The payload used by ping exchanges - the ebMS test service and action carry it.
_ping_payload = b'<?xml version="1.0" encoding="UTF-8"?><ping/>'

# ################################################################################################################################
# ################################################################################################################################

class AS4Wrapper:
    """ The runtime representation of one outgoing AS4 connection - it builds, signs,
    optionally encrypts and posts AS4 messages, verifying the synchronous receipts.
    """

    def __init__(self, server:'ParallelServer', config:'stranydict') -> 'None':
        self.server = server
        self.config = config

        address_host = config['address_host']
        address_url_path = config['address_url_path']
        self.address = f'{address_host}{address_url_path}'

        # The runtime P-Mode and keystore are built lazily, on first use,
        # so that incomplete configuration does not break config propagation.
        self._lock = RLock()
        self._pmode:'PMode | None' = None
        self._keystore:'Keystore | None' = None

        # One HTTP client is shared by all exchanges over this connection.
        verify_tls = config['validate_tls']
        timeout = config['timeout']
        self.session = httpx.Client(verify=verify_tls, timeout=timeout)

        # A connection whose audit log was turned off writes no events. The flag lives in an opaque
        # attribute, so a connection saved before it existed carries a null, which means it was
        # never turned off.
        is_audit_log_active = config['is_audit_log_active']

        if is_audit_log_active is None:
            is_audit_log_active = True

        self.needs_audit = is_audit_log_active

        if self.needs_audit:
            self.audit_log = AuditLog(self.server.name)

# ################################################################################################################################

    def _enforce_is_active(self) -> 'None':

        # An inactive connection must not be used.
        if not self.config['is_active']:
            name = self.config['name']
            raise AS4Exception(f'AS4 connection `{name}` is not active')

# ################################################################################################################################

    def _get_pmode(self) -> 'PMode':
        """ Returns this connection's P-Mode, building it on first use.
        """
        with self._lock:
            if self._pmode is None:
                pmode = build_pmode(self.config)
                pmode.endpoint_url = self.address
                pmode.http_timeout_seconds = self.config['timeout']
                pmode.verify_tls = self.config['validate_tls']
                apply_reception_awareness(pmode, self.config)
                apply_credentials(pmode, self.config, self.server.decrypt)
                self._pmode = pmode

            out = self._pmode

        return out

# ################################################################################################################################

    def _get_keystore(self) -> 'Keystore':
        """ Returns this connection's keystore, building it on first use -
        the private keys are decrypted only at this point.
        """
        with self._lock:
            if self._keystore is None:
                self._keystore = build_keystore(self.config, self.server.decrypt)

            out = self._keystore

        return out

# ################################################################################################################################

    def _check_send_result(self, cid:'str', result:'SendResult') -> 'None':
        """ Raises a descriptive exception if a send did not produce a valid receipt.
        """
        if result.is_ok:
            return

        name = self.config['name']

        # Collect all the error signals the responder returned ..
        errors:'strlist' = []
        for error in result.errors:
            errors.append(f'{error.error_code} {error.detail}')

        # .. and raise an exception with everything that is known about the failure.
        if errors:
            details = '; '.join(errors)
            raise AS4Exception(f'AS4 send failed over `{name}` (HTTP {result.http_status}); cid:{cid} -> {details}')
        else:
            raise AS4Exception(f'AS4 send failed over `{name}` (HTTP {result.http_status}); cid:{cid} - no receipt was returned')

# ################################################################################################################################

    def _snapshot(self, parts:'part_list') -> 'part_list':
        """ Takes the parts of a message as they are before it is sent. Building a message
        compresses and encrypts the parts in place, so the documents that were submitted are only
        readable through a snapshot taken beforehand - and that is what belongs in the evidence.

        The copies are shallow because the bytes they point at are never mutated, only replaced.
        """

        # Our response to produce
        out:'part_list' = []

        for part in parts:
            out.append(copy(part))

        return out

# ################################################################################################################################

    def _record_send(self, cid:'str', pmode:'PMode', parts:'part_list', result:'SendResult') -> 'None':
        """ Records one push and whatever came back for it, under the pair of the P-Mode it went out
        under - the per-send P-Mode for an access-point send, the connection's own otherwise.
        """
        if not self.needs_audit:
            return

        # The four-corner properties are genuinely absent from an exchange that is not four-corner.
        original_sender = pmode.original_sender
        if original_sender is None:
            original_sender = ''

        final_recipient = pmode.final_recipient
        if final_recipient is None:
            final_recipient = ''

        record_send_result(self.audit_log, pmode.initiator.party_id, pmode.responder.party_id, result,
            payloads=parts, service=pmode.service, action=pmode.action, original_sender=original_sender,
            final_recipient=final_recipient, cid=cid)

# ################################################################################################################################

    def _record_pull(self, cid:'str', pmode:'PMode', result:'PullResult') -> 'None':
        """ Records the message one pull brought back and the acknowledgement posted for it. A pull
        reverses the direction of the exchange, so the responder is who the message came from.
        """
        if not self.needs_audit:
            return

        record_pull_result(self.audit_log, pmode.responder.party_id, pmode.initiator.party_id, result, cid=cid)

# ################################################################################################################################

    def send(
        self,
        cid:'str',
        data:'strbytes',
        mime_type:'str'=AS4.Default.Payload_MIME_Type,
        conversation_id:'strnone'=None,
        ) -> 'SendResult':
        """ Builds, signs, optionally encrypts and posts one AS4 message
        to the configured endpoint, verifying the synchronous receipt.
        """
        self._enforce_is_active()

        if isinstance(data, str):
            data = data.encode('utf8')

        pmode = self._get_pmode()
        keystore = self._get_keystore()

        part = new_part(data, mime_type)
        parts = [part]

        logger.info('AS4 out -> %s; name:%s; cid:%s', pmode.endpoint_url, self.config['name'], cid)

        submitted = self._snapshot(parts)
        out = outbound_send(pmode, keystore, parts, conversation_id, client=self.session)

        # Recorded before the result is judged, so a failed exchange leaves its evidence too.
        self._record_send(cid, pmode, submitted, out)
        self._check_send_result(cid, out)

        return out

# ################################################################################################################################

    def queue_for_pull(
        self,
        cid:'str',
        data:'strbytes',
        mime_type:'str'=AS4.Default.Payload_MIME_Type,
        conversation_id:'strnone'=None,
        mpc:'strnone'=None,
        ) -> 'str':
        """ Puts one message on a message partition channel for the partner to pull, and returns the
        eb:MessageId it will be handed over under. Nothing goes out here - the message waits until a
        pull request from the partner asks for it, and the channel serving that request is what hands
        it over, signed and encrypted as this connection's P-Mode says.

        The channel it waits on is this connection's own unless another one is named, which is what
        a connection serving several sub-channels queues each message on.
        """
        self._enforce_is_active()

        if isinstance(data, str):
            data = data.encode('utf8')

        pmode = self._get_pmode()

        if not mpc:
            mpc = pmode.mpc

        part = new_part(data, mime_type)
        parts = [part]

        out = queue_message(mpc, pmode.initiator.party_id, pmode.responder.party_id, pmode.service,
            pmode.action, parts, conversation_id)

        logger.info('AS4 queued for pull; name:%s; mpc:%s; message id:%s; cid:%s',
            self.config['name'], mpc, out, cid)

        return out

# ################################################################################################################################

    def _discover_receiver(self, participant_id:'str', preset:'DocumentTypePreset', keystore:'Keystore') -> 'anytuple':
        """ Looks one participant up through SML and SMP and returns the endpoint their documents
        of this type go to along with the certificate of the access point serving it. The connection's
        trust anchors are the network's, so they are what the SMP metadata signature is checked against.
        """
        sml_domain = self.config['as4_sml_domain']
        if not sml_domain:
            sml_domain = SML_Domain_Production

        endpoint_details = lookup_endpoint(
            Peppol_Participant_ID_Type,
            participant_id,
            preset.document_type,
            keystore.trust_anchors,
            sml_domain,
        )

        certificate = load_der_x509_certificate(endpoint_details.certificate_der)

        out = (endpoint_details.url, certificate)
        return out

# ################################################################################################################################

    def send_to(
        self,
        cid:'str',
        participant_id:'str',
        document_type:'str',
        data:'strbytes',
        from_participant:'strnone'=None,
        conversation_id:'strnone'=None,
        ) -> 'SendResult':
        """ The access-point one-liner - looks the receiver up through SML and SMP,
        wraps the business document in an SBDH and delivers it to the discovered endpoint.
        """
        self._enforce_is_active()

        if isinstance(data, str):
            data = data.encode('utf8')

        preset = get_document_type_preset(document_type)

        # The sending participant defaults to the one configured on the connection.
        if not from_participant:
            from_participant = self.config['as4_original_sender']

        if not from_participant:
            name = self.config['name']
            raise AS4Exception(f'No sender participant id was given and none is configured on `{name}`')

        keystore = self._get_keystore()
        base_pmode = self._get_pmode()

        # Where the receiver's documents of this type are to be delivered, and the certificate of the
        # access point they are delivered to, either as discovery reports them or as configured.
        if self.config['as4_use_discovery']:
            endpoint_url, receiver_certificate = self._discover_receiver(participant_id, preset, keystore)
        else:
            endpoint_url = base_pmode.endpoint_url
            receiver_certificate = cast_('Certificate', keystore.peer_signing_certificate)

        # The receiving access point's certificate names that access point.
        receiver_party_id = certificate_common_name(receiver_certificate)

        # .. wrap the business document in an SBDH, the way the network requires ..
        business_document = parse_xml(data)
        instance_identifier = CryptoManager.generate_hex_string(_instance_identifier_bits)

        sbdh = build_sbdh(
            Peppol_Participant_ID_Type,
            from_participant,
            Peppol_Participant_ID_Type,
            participant_id,
            preset.document_type,
            preset.process_id,
            preset.process_scheme,
            preset.document_standard,
            preset.document_type_version,
            instance_identifier,
            business_document,
        )

        # .. build a per-send P-Mode carrying everything discovery and the preset supplied ..
        pmode = deepcopy(base_pmode)
        pmode.endpoint_url = endpoint_url
        pmode.responder.party_id = receiver_party_id
        pmode.service = preset.process_id
        pmode.action = preset.document_type
        pmode.original_sender = from_participant
        pmode.final_recipient = participant_id

        # .. the receiver's certificate is also what receipts are verified against
        # and what any message-level encryption is performed to - a shallow copy
        # is used because private key objects cannot be deep-copied ..
        send_keystore = copy(keystore)
        send_keystore.peer_signing_certificate = receiver_certificate
        send_keystore.peer_encryption_certificate = receiver_certificate

        part = new_part(sbdh)
        parts = [part]

        logger.info('AS4 out -> %s; name:%s; to:%s; document:%s; cid:%s',
            pmode.endpoint_url, self.config['name'], participant_id, document_type, cid)

        # .. and post the message, verifying the receipt.
        submitted = self._snapshot(parts)
        out = outbound_send(pmode, send_keystore, parts, conversation_id, client=self.session)

        self._record_send(cid, pmode, submitted, out)
        self._check_send_result(cid, out)

        return out

# ################################################################################################################################

    def _resend_parts(self, documents:'anylist') -> 'part_list':
        """ Rebuilds the payload parts of a repeat delivery out of what the first attempt was
        recorded with, each part keeping the Content-ID the message referenced it by.
        """

        # Our response to produce
        out:'part_list' = []

        for data, content_type, content_id in documents:
            part = new_part(data, content_type)
            part.content_id = content_id
            out.append(part)

        return out

# ################################################################################################################################

    def _resend_pmode(self, candidate:'ResendCandidate', keystore:'Keystore') -> 'anytuple':
        """ Builds the P-Mode and keystore one repeat delivery goes out under - the business
        information and the four-corner addressing of the attempt it repeats, and the endpoint that
        addressing resolves to now, which a connection using discovery looks up all over again
        because the receiver may have moved access point since.
        """
        base_pmode = self._get_pmode()

        pmode = deepcopy(base_pmode)
        pmode.service = candidate.service
        pmode.action = candidate.action

        # An exchange that was not four-corner recorded no endpoints, and the P-Mode of one that was
        # names them the way the first attempt did.
        if candidate.original_sender:
            pmode.original_sender = candidate.original_sender

        if candidate.final_recipient:
            pmode.final_recipient = candidate.final_recipient

        # A connection not using discovery delivers to its configured endpoint, and the peer
        # certificates it has configured are what the exchange is secured with.
        needs_discovery = self.config['as4_use_discovery'] and candidate.final_recipient

        if not needs_discovery:
            out = pmode, keystore
            return out

        preset = get_document_type_preset(candidate.action)
        endpoint_url, receiver_certificate = self._discover_receiver(candidate.final_recipient, preset, keystore)

        pmode.endpoint_url = endpoint_url
        pmode.responder.party_id = certificate_common_name(receiver_certificate)

        # A shallow copy is used because private key objects cannot be deep-copied.
        send_keystore = copy(keystore)
        send_keystore.peer_signing_certificate = receiver_certificate
        send_keystore.peer_encryption_certificate = receiver_certificate

        out = pmode, send_keystore
        return out

# ################################################################################################################################

    def _deliver_candidate(self, cid:'str', candidate:'ResendCandidate', needs_record:'bool') -> 'SendResult':
        """ Delivers the payloads of one stored message under the addressing the attempt they come
        from used. An eb:MessageId carried by the candidate makes this a repeat of that attempt,
        and no id at all makes it a message of its own.
        """
        self._enforce_is_active()

        keystore = self._get_keystore()
        pmode, send_keystore = self._resend_pmode(candidate, keystore)
        parts = self._resend_parts(candidate.documents)

        # The endpoint is logged as it resolved, which a connection using discovery looks up per delivery.
        if candidate.message_id:
            logger.info('AS4 resend -> %s; name:%s; message id:%s; attempt:%d; cid:%s',
                pmode.endpoint_url, self.config['name'], candidate.message_id, candidate.attempt_count + 1, cid)
        else:
            logger.info('AS4 resubmit -> %s; name:%s; cid:%s', pmode.endpoint_url, self.config['name'], cid)

        submitted = self._snapshot(parts)

        out = outbound_send(pmode, send_keystore, parts, candidate.conversation_id, client=self.session,
            message_id=candidate.message_id)

        if needs_record:
            self._record_send(cid, pmode, submitted, out)

        return out

# ################################################################################################################################

    def resend(self, cid:'str', candidate:'ResendCandidate') -> 'SendResult':
        """ Delivers one message again under the eb:MessageId of the attempt it repeats, which is
        what lets the receiving side recognize it as a message it may already hold.

        The repeat is recorded like any other send, so the attempt is counted and the exchange
        closes as soon as a receipt for it arrives, whichever attempt earned it.
        """
        out = self._deliver_candidate(cid, candidate, True)
        return out

# ################################################################################################################################

    def resubmit(self, cid:'str', candidate:'ResendCandidate') -> 'SendResult':
        """ Delivers the payloads of a stored message as a message of its own, with an eb:MessageId
        of its own - the operator action, distinct from the repeat delivery that reuses the id of the
        attempt it repeats. The caller records the attempt, because what makes it readable as a
        resubmit is the link to the message it was made from, which only the caller knows.
        """
        out = self._deliver_candidate(cid, candidate, False)
        return out

# ################################################################################################################################

    def pull(self, cid:'str', mpc:'strnone'=None) -> 'PullResult':
        """ Sends one pull request to the configured endpoint - the generic
        One-Way/Pull exchange - and processes whatever comes back.
        """
        self._enforce_is_active()

        pmode = self._get_pmode()
        keystore = self._get_keystore()

        # The log shows the channel the pull actually goes to.
        log_mpc = mpc
        if log_mpc is None:
            log_mpc = pmode.mpc

        logger.info('AS4 pull -> %s; name:%s; mpc:%s; cid:%s', pmode.endpoint_url, self.config['name'], log_mpc, cid)

        out = outbound_pull(pmode, keystore, mpc, client=self.session)

        self._record_pull(cid, pmode, out)

        if not out.is_ok:

            # Collect all the error signals the responder returned ..
            errors:'strlist' = []
            for error in out.errors:
                errors.append(f'{error.error_code} {error.detail}')

            # .. and raise an exception with everything that is known about the failure.
            name = self.config['name']
            details = '; '.join(errors)
            raise AS4Exception(f'AS4 pull failed over `{name}` (HTTP {out.http_status}); cid:{cid} -> {details}')

        return out

# ################################################################################################################################

    def ping(self, cid:'str', ping_path:'strnone'=None) -> 'str':
        """ Performs a signed ping exchange, using the test service and action the ebMS specification
        defines. The exchange goes to the configured endpoint unless a path is given, in which case
        it goes to that path on the same host.
        """
        base_pmode = self._get_pmode()
        pmode = deepcopy(base_pmode)
        pmode.service = Default.Test_Service
        pmode.action = Default.Test_Action

        if ping_path:
            address_host = self.config['address_host']
            pmode.endpoint_url = f'{address_host}{ping_path}'

        keystore = self._get_keystore()

        part = new_part(_ping_payload)
        parts = [part]

        result = outbound_send(pmode, keystore, parts, client=self.session)
        self._check_send_result(cid, result)

        out = f'AS4 ping ok, cid:`{cid}`, message id:`{result.message_id}`'
        return out

# ################################################################################################################################
# ################################################################################################################################
