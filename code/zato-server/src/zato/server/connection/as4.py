# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import deepcopy
from threading import RLock

# cryptography
from cryptography.x509 import load_der_x509_certificate
from cryptography.x509.oid import NameOID

# httpx
import httpx

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import AS4Exception, Default
from zato.common.as4.config import build_keystore, build_pmode
from zato.common.as4.discovery import lookup_endpoint, SML_Domain_Production
from zato.common.as4.outbound import new_part, pull as outbound_pull, send as outbound_send
from zato.common.as4.presets import get_document_type_preset
from zato.common.as4.profiles import Peppol_Participant_ID_Type
from zato.common.as4.sbdh import build_sbdh
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.outbound import PullResult, SendResult
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, stranydict, strbytes, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.server.base.parallel import ParallelServer
    PullResult = PullResult
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
        mime_type:'str'='application/xml',
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
        # and what any message-level encryption is performed to ..
        keystore = self._get_keystore()
        send_keystore = deepcopy(keystore)
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
