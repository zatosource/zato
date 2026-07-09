# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import AS2, GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

class AS2Importer(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_AS2

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_AS2,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': AS2.Default.Pool_Size,
    }

    connection_extra_field_defaults = {

        # The partner's EDI addressing.
        'isa_qualifier': '',
        'isa_id': '',
        'gs_id': '',
        'unb_id': '',

        # How outgoing messages travel.
        'sign_algorithm': '',
        'encryption_algorithm': '',
        'mdn_mode': '',
        'async_mdn_url': '',
        'subject': '',
        'content_type': '',
        'as2_version': '',
        'content_transfer_encoding': '',
        'http_transfer_mode': '',
        'inbound_topic': '',
        'inbound_service': '',

        # The security toggles, with the same defaults the partnership itself has.
        'sign': True,
        'encrypt': True,
        'compress': False,
        'compress_before_signing': True,
        'mdn_signed': True,
        'preserve_filename': False,
        'verify_tls': True,
        'force_base64': False,
        'prevent_canonicalization': False,
        'warn_on_duplicate_filename': False,

        # A zero means the partnership's own numeric default stays in place.
        'http_timeout_seconds': 0,
        'chunked_threshold_bytes': 0,
        'ack_overdue_after': 0,
        'resend_max_retries': 0,

        # The partner's certificate rotation fields, pasted as PEM.
        'as2_partner_cert': '',
        'as2_partner_next_cert': '',
        'as2_partner_next_cert_from': '',

        # Our own keystore material, pasted as PEM.
        'as2_signing_key': '',
        'as2_signing_cert_chain': '',
        'as2_decryption_key': '',
        'as2_peer_signing_cert': '',
        'as2_peer_encryption_cert': '',
        'as2_trust_anchors': '',
    }

    connection_secret_keys = []
    connection_required_attrs = ['name', 'as2_from', 'as2_to', 'endpoint_url']

# ################################################################################################################################
# ################################################################################################################################
