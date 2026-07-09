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
from cryptography.x509.oid import NameOID

# httpx
import httpx

# lxml
from lxml import etree

# Zato
from zato.common.api import AS4
from zato.common.as4.common import AS4Exception, AS4ProtocolException, Default, EbMSError, Peppol_Not_Serviced
from zato.common.as4.config import build_keystore, build_pmode, build_pmodes
from zato.common.as4.discovery import lookup_endpoint, SML_Domain_Production
from zato.common.as4.inbound import handle as inbound_handle
from zato.common.as4.outbound import new_part, pull as outbound_pull, send as outbound_send
from zato.common.as4.presets import get_document_type_preset
from zato.common.as4.profiles import Peppol_Participant_ID_Type
from zato.common.as4.sbdh import build_sbdh, parse_sbdh
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.ebms import UserMessageInfo
    from zato.common.as4.inbound import InboundResult, pmode_list
    from zato.common.as4.outbound import PullResult, SendResult
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, stranydict, strbytes, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import part_list
    from zato.server.base.parallel import ParallelServer
    PullResult = PullResult
    SendResult = SendResult
    UserMessageInfo = UserMessageInfo

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

def build_routed_message(profile:'str', user_message:'UserMessageInfo', payload:'any_') -> 'stranydict':
    """ Builds the dictionary that one accepted payload is routed with - the ebMS metadata
    plus, for Peppol, the SBDH metadata, so subscribers route without re-parsing anything.
    """

    # All the keys are always present, no matter the profile.
    out = {
        'message_id': user_message.message_id,
        'conversation_id': user_message.conversation_id,
        'from_party': user_message.from_party,
        'to_party': user_message.to_party,
        'service': user_message.service,
        'action': user_message.action,
        'mime_type': payload.mime_type,
        'data': payload.data.decode('utf8', 'replace'),
        'sbdh_sender': '',
        'sbdh_receiver': '',
        'sbdh_document_type': '',
        'sbdh_process_id': '',
        'sbdh_instance_identifier': '',
    }

    # Peppol payloads carry an SBDH whose identifiers subscribers route by.
    if profile == AS4.Profile.Peppol:
        info, _ = parse_sbdh(payload.data)
        out['sbdh_sender'] = info.sender_id
        out['sbdh_receiver'] = info.receiver_id
        out['sbdh_document_type'] = info.document_type
        out['sbdh_process_id'] = info.process_id
        out['sbdh_instance_identifier'] = info.instance_identifier

    return out

# ################################################################################################################################
# ################################################################################################################################

class AS4Wrapper:
    """ The runtime representation of one outgoing AS4 connection - it builds, signs,
    optionally encrypts and posts AS4 messages, verifying the synchronous receipts.
    """

    def __init__(self, server:'ParallelServer', config:'stranydict') -> 'None':
        self.server = server
        self.config = config
        self.address = '{}{}'.format(config['address_host'], config['address_url_path'])

        # The runtime P-Mode and keystore are built lazily, on first use,
        # so that incomplete configuration does not break config propagation.
        self._lock = RLock()
        self._pmode:'PMode | None' = None
        self._keystore:'Keystore | None' = None

        # One HTTP client is shared by all exchanges over this connection.
        verify_tls = config['validate_tls']
        timeout = config['timeout']
        self.session = httpx.Client(verify=verify_tls, timeout=timeout)

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

    def _check_send_result(self, result:'SendResult') -> 'None':
        """ Raises a descriptive exception if a send did not produce a valid receipt.
        """
        if result.is_ok:
            return

        name = self.config['name']

        # Collect all the error signals the responder returned ..
        errors = []
        for error in result.errors:
            errors.append(f'{error.error_code} {error.detail}')

        # .. and raise an exception with everything that is known about the failure.
        if errors:
            details = '; '.join(errors)
            raise AS4Exception(f'AS4 send failed over `{name}` (HTTP {result.http_status}) -> {details}')
        else:
            raise AS4Exception(f'AS4 send failed over `{name}` (HTTP {result.http_status}) - no receipt was returned')

# ################################################################################################################################

    def send(
        self,
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

        parts = [new_part(data, mime_type)]

        logger.info('AS4 out -> %s; name:%s', pmode.endpoint_url, self.config['name'])

        out = outbound_send(pmode, keystore, parts, conversation_id, client=self.session)
        self._check_send_result(out)

        return out

# ################################################################################################################################

    def send_to(
        self,
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

        # Find where the receiver's documents of this type are to be delivered ..
        sml_domain = self.config['as4_sml_domain'] or SML_Domain_Production
        endpoint_info = lookup_endpoint(Peppol_Participant_ID_Type, participant_id, preset.document_type, sml_domain)

        # .. the receiving access point's certificate names that access point ..
        receiver_certificate = load_der_x509_certificate(endpoint_info.certificate_der)
        receiver_common_names = receiver_certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        receiver_party_id = receiver_common_names[0].value

        # .. wrap the business document in an SBDH, the way the network requires ..
        business_document = etree.fromstring(data)
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
        pmode = deepcopy(self._get_pmode())
        pmode.endpoint_url = endpoint_info.url
        pmode.responder.party_id = receiver_party_id
        pmode.service = preset.process_id
        pmode.action = preset.document_type
        pmode.original_sender = from_participant
        pmode.final_recipient = participant_id

        # .. the receiver's certificate is also what receipts are verified against
        # and what any message-level encryption is performed to - a shallow copy
        # is used because private key objects cannot be deep-copied ..
        keystore = self._get_keystore()
        send_keystore = copy(keystore)
        send_keystore.peer_signing_certificate = receiver_certificate
        send_keystore.peer_encryption_certificate = receiver_certificate

        parts = [new_part(sbdh)]

        logger.info('AS4 out -> %s; name:%s; to:%s; document:%s',
            pmode.endpoint_url, self.config['name'], participant_id, document_type)

        # .. and post the message, verifying the receipt.
        out = outbound_send(pmode, send_keystore, parts, conversation_id, client=self.session)
        self._check_send_result(out)

        return out

# ################################################################################################################################

    def pull(self, mpc:'strnone'=None) -> 'PullResult':
        """ Sends one pull request to the configured endpoint - the generic
        One-Way/Pull exchange - and processes whatever comes back.
        """
        self._enforce_is_active()

        pmode = self._get_pmode()
        keystore = self._get_keystore()

        logger.info('AS4 pull -> %s; name:%s; mpc:%s', pmode.endpoint_url, self.config['name'], mpc or pmode.mpc)

        out = outbound_pull(pmode, keystore, mpc, client=self.session)

        if not out.is_ok:

            # Collect all the error signals the responder returned ..
            errors = []
            for error in out.errors:
                errors.append(f'{error.error_code} {error.detail}')

            # .. and raise an exception with everything that is known about the failure.
            name = self.config['name']
            details = '; '.join(errors)
            raise AS4Exception(f'AS4 pull failed over `{name}` (HTTP {out.http_status}) -> {details}')

        return out

# ################################################################################################################################

    def ping(self, cid:'str', ping_path:'any_'=None) -> 'str':
        """ Performs a signed ping exchange with the configured endpoint,
        using the test service and action the ebMS specification defines.
        """
        _ = ping_path

        pmode = deepcopy(self._get_pmode())
        pmode.service = Default.Test_Service
        pmode.action = Default.Test_Action

        keystore = self._get_keystore()
        parts = [new_part(_ping_payload)]

        result = outbound_send(pmode, keystore, parts, client=self.session)
        self._check_send_result(result)

        out = f'AS4 ping ok, cid:`{cid}`, message id:`{result.message_id}`'
        return out

# ################################################################################################################################
# ################################################################################################################################

class AS4ChannelRuntime:
    """ The runtime representation of one AS4 channel - its P-Modes, keystore,
    serviced participants and routing target, built from the channel's configuration.
    """

    def __init__(self, server:'ParallelServer', config:'stranydict') -> 'None':
        self.server = server
        self.config = config
        self.name = config['name']

        # The runtime P-Modes and keystore are built lazily, on first use,
        # so that incomplete configuration does not break config propagation.
        self._lock = RLock()
        self._pmodes:'pmode_list | None' = None
        self._keystore:'Keystore | None' = None

        # The participants this channel accepts documents for - one per line,
        # an empty list means every participant is accepted. The opaque column
        # genuinely stores a null when the channel was saved without any.
        serviced_participants = config['as4_serviced_participants']
        if serviced_participants is None:
            serviced_participants = ''

        participants = set()

        for line in serviced_participants.splitlines():
            line = line.strip()
            if line:
                participants.add(line)

        self.serviced_participants = participants

        # Where accepted messages go - the channel's service when one is configured,
        # its pub/sub topic otherwise.
        self.service_name = config['service_name']

        topic_name = config['as4_inbound_topic']
        if not topic_name:
            topic_name = AS4.Default.Inbound_Topic
        self.inbound_topic = topic_name

# ################################################################################################################################

    def _get_pmodes(self) -> 'pmode_list':
        """ Returns this channel's P-Modes, building them on first use.
        """
        with self._lock:
            if self._pmodes is None:
                self._pmodes = build_pmodes(self.config)

            out = self._pmodes

        return out

# ################################################################################################################################

    def _get_keystore(self) -> 'Keystore':
        """ Returns this channel's keystore, building it on first use -
        the private keys are decrypted only at this point.
        """
        with self._lock:
            if self._keystore is None:
                self._keystore = build_keystore(self.config, self.server.decrypt)

            out = self._keystore

        return out

# ################################################################################################################################

    def _is_duplicate(self, message_id:'str') -> 'bool':
        """ Returns True if this eb:MessageId was already processed - the server-wide cache
        remembers each accepted one for the duplicate detection window.
        """
        cache = self.server.config_manager.cache_api
        key = AS4.Default.Duplicate_Cache_Prefix + message_id

        # A message seen before is a duplicate ..
        if cache.exists(key):
            return True

        # .. an unseen one is remembered for the length of the detection window.
        cache.set(key, True, expiry=AS4.Default.Duplicate_Detection_TTL)

        return False

# ################################################################################################################################

    def _validate(self, user_message:'UserMessageInfo', payloads:'part_list') -> 'None':
        """ Rejects Peppol documents addressed to a participant this channel does not serve,
        the way the Peppol AS4 profile requires.
        """
        _ = user_message

        # Only the Peppol profile carries SBDH-wrapped documents to check.
        if self.config['as4_profile'] != AS4.Profile.Peppol:
            return

        # No configured participants means every participant is accepted.
        if not self.serviced_participants:
            return

        for payload in payloads:
            info, _ignored = parse_sbdh(payload.data)

            # A receiver outside the serviced list is answered with the error signal
            # and detail the Peppol profile defines for this case.
            if info.receiver_id not in self.serviced_participants:
                raise AS4ProtocolException(EbMSError.Other, Peppol_Not_Serviced)

# ################################################################################################################################

    def _build_routed_message(self, user_message:'UserMessageInfo', payload:'any_') -> 'stranydict':
        """ Builds the dictionary that one accepted payload is routed with.
        """
        out = build_routed_message(self.config['as4_profile'], user_message, payload)
        return out

# ################################################################################################################################

    def _route(self, cid:'str', result:'InboundResult') -> 'None':
        """ Hands each accepted payload over to the channel's routing target.
        """
        user_message = result.user_message

        for payload in result.payloads:

            message = self._build_routed_message(user_message, payload)

            # A configured service receives the message directly ..
            if self.service_name:
                _ = self.server.invoke(self.service_name, message)

            # .. without one, the message goes to the channel's topic, which is where
            # reliability lives - redelivery and retries are pub/sub's built-in behavior.
            else:
                _ = self.server.pubsub_redis.publish(self.inbound_topic, message, cid=cid, correl_id=cid)

# ################################################################################################################################

    def handle(self, cid:'str', body:'bytes', content_type:'str') -> 'InboundResult':
        """ Runs one incoming request through the AS4 inbound pipeline
        and routes whatever payloads it accepted.
        """
        out = inbound_handle(
            body,
            content_type,
            self._get_pmodes(),
            self._get_keystore(),
            is_duplicate=self._is_duplicate,
            validate=self._validate,
        )

        # Only messages that were accepted and are not replays carry payloads to route.
        if out.user_message:
            self._route(cid, out)

            logger.info('AS4 message `%s` accepted on channel `%s`, %d payload(s) routed',
                out.user_message.message_id, self.name, len(out.payloads))

        elif out.is_error:
            logger.warning('AS4 request rejected with `%s` on channel `%s`; cid:%s', out.error_code, self.name, cid)

        return out

# ################################################################################################################################
# ################################################################################################################################
