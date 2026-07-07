# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from threading import RLock

# Zato
from zato.common.as4.inbound import handle as as4_handle
from zato.common.as4.keystore import load_certificates_pem, load_private_key_pem, new_keystore
from zato.common.as4.profiles import new_edelivery1_pmode, new_edelivery2_pmode, new_ics2_pmode, new_peppol_pmode
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.inbound import pmode_list
    from zato.common.as4.keystore import Keystore
    from zato.common.typing_ import any_, anytuple
    any_ = any_
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The user config file that configures this endpoint is called as4.conf,
# which makes it available under this key in self.server.user_config.
_user_config_name = 'as4'

# The pub/sub topic that received messages are published to unless configured otherwise -
# reliability, including redelivery to consumers, is entirely pub/sub's responsibility.
_default_inbound_topic = '/zato/as4/inbound'

# Maps the profile names accepted in as4.conf to their P-Mode presets.
_profile_presets = {
    'edelivery1': new_edelivery1_pmode,
    'edelivery2': new_edelivery2_pmode,
    'peppol':     new_peppol_pmode,
    'ics2':       new_ics2_pmode,
}

# P-Mode fields settable directly from the [pmode] section of as4.conf.
_pmode_string_fields = ('service', 'action', 'agreement', 'endpoint_url', 'mpc',
    'original_sender', 'final_recipient')

# The configuration built from as4.conf is cached here after the first request.
_config_lock = RLock()
_config_cache:'anytuple | None' = None

# ################################################################################################################################
# ################################################################################################################################

def _load_keystore(keystore_config:'any_') -> 'Keystore':
    """ Builds a keystore out of the [keystore] section of as4.conf - each entry
    is a path to a PEM file and only signing material is strictly required.
    """

    # Our response to produce
    out = new_keystore()

    with open(keystore_config['signing_key'], 'rb') as f:
        out.signing_key = load_private_key_pem(f.read())

    with open(keystore_config['signing_cert_chain'], 'rb') as f:
        out.signing_certificate_chain = load_certificates_pem(f.read())

    if path := keystore_config.get('decryption_key'):
        with open(path, 'rb') as f:
            out.decryption_key = load_private_key_pem(f.read())

    if path := keystore_config.get('peer_signing_cert'):
        with open(path, 'rb') as f:
            out.peer_signing_certificate = load_certificates_pem(f.read())[0]

    if path := keystore_config.get('peer_encryption_cert'):
        with open(path, 'rb') as f:
            out.peer_encryption_certificate = load_certificates_pem(f.read())[0]

    if path := keystore_config.get('trust_anchors'):
        with open(path, 'rb') as f:
            out.trust_anchors = load_certificates_pem(f.read())

    return out

# ################################################################################################################################

def _load_pmode(pmode_config:'any_') -> 'any_':
    """ Builds one P-Mode out of a [pmode] section of as4.conf, starting from
    the preset matching the configured profile.
    """
    profile = pmode_config.get('profile') or 'edelivery1'
    preset = _profile_presets[profile]

    # Our response to produce
    out = preset()

    for name in _pmode_string_fields:
        if value := pmode_config.get(name):
            setattr(out, name, value)

    if value := pmode_config.get('from_party'):
        out.initiator.party_id = value

    if value := pmode_config.get('to_party'):
        out.responder.party_id = value

    return out

# ################################################################################################################################

def _build_config(user_config:'any_') -> 'anytuple':
    """ Builds the P-Modes, the keystore and the inbound topic name from as4.conf.
    """
    as4_config = user_config[_user_config_name]

    keystore = _load_keystore(as4_config['keystore'])
    pmodes:'pmode_list' = [_load_pmode(as4_config['pmode'])]

    inbound_topic = _default_inbound_topic
    if 'behavior' in as4_config:
        if topic := as4_config['behavior'].get('inbound_topic'):
            inbound_topic = topic

    out = (pmodes, keystore, inbound_topic)
    return out

# ################################################################################################################################
# ################################################################################################################################

class AS4Endpoint(AdminService):
    """ Built-in service that serves as the AS4 endpoint on the /zato/as4 REST channel.
    Runs incoming requests through the AS4 inbound pipeline - decryption, signature
    verification, decompression - publishes the delivered payloads to a pub/sub topic
    and returns the signed receipt or an ebMS error signal.
    """

    name = 'zato.channel.as4.endpoint'

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes one incoming AS4 request.
        """
        global _config_cache

        # The configuration is built once, on the first request after a server start.
        with _config_lock:
            if _config_cache is None:
                _config_cache = _build_config(self.server.user_config)

        pmodes, keystore, inbound_topic = _config_cache

        # The raw multipart body, exactly as it arrived.
        raw_request = self.request.raw_request

        if isinstance(raw_request, str):
            raw_request = raw_request.encode('utf8')

        content_type = self.request.http.headers['content-type']

        # Run the AS4 inbound pipeline ..
        result = as4_handle(raw_request, content_type, pmodes, keystore)

        # .. hand each delivered payload over to pub/sub, which is where reliability
        # lives - redelivery and retries are its built-in behavior ..
        if result.user_message:

            user_message = result.user_message

            for payload in result.payloads:
                _ = self.publish(inbound_topic, {
                    'message_id': user_message.message_id,
                    'conversation_id': user_message.conversation_id,
                    'from_party': user_message.from_party,
                    'to_party': user_message.to_party,
                    'service': user_message.service,
                    'action': user_message.action,
                    'mime_type': payload.mime_type,
                    'data': payload.data.decode('utf8', 'replace'),
                })

            logger.info('AS4 message `%s` accepted, %d payload(s) published to `%s`',
                user_message.message_id, len(result.payloads), inbound_topic)

        elif result.is_error:
            logger.warning('AS4 request rejected with `%s`', result.error_code)

        # .. and send back what the pipeline produced - a receipt or an error signal.
        self.response.status_code = result.status_code
        self.response.content_type = result.content_type
        self.response.payload = result.body

# ################################################################################################################################
# ################################################################################################################################
