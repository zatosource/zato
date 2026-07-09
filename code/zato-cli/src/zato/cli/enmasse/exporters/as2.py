# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    as2_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# String fields exported when they carry a value - an empty one means
# the partnership's own default is in place and there is nothing to say.
_string_fields = ('isa_qualifier', 'isa_id', 'gs_id', 'unb_id', 'sign_algorithm', 'encryption_algorithm',
    'mdn_mode', 'async_mdn_url', 'subject', 'content_type', 'as2_version', 'content_transfer_encoding',
    'http_transfer_mode', 'inbound_topic', 'inbound_service', 'as2_partner_cert', 'as2_partner_next_cert',
    'as2_partner_next_cert_from', 'as2_signing_cert_chain', 'as2_next_decryption_cert', 'as2_peer_signing_cert',
    'as2_peer_encryption_cert', 'as2_trust_anchors')

# Integer fields exported when they are not zero - a zero means the default stays in place.
_int_fields = ('http_timeout_seconds', 'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries')

# Boolean fields exported when they differ from the partnership's own defaults.
_bool_field_defaults = {
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
}

# The private keys are encrypted at rest, so they are never exported.
_secret_fields = ('as2_signing_key', 'as2_decryption_key', 'as2_next_decryption_key')

# ################################################################################################################################
# ################################################################################################################################

class AS2Exporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'as2_def_list':
        """ Exports outgoing AS2 connection definitions.
        """
        logger.info('Exporting outgoing AS2 connection definitions')

        # Get AS2 connections from database using the generic connection query
        db_as2 = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_AS2)

        if not db_as2:
            logger.info('No outgoing AS2 connection definitions found in DB')
            return []

        as2_connections = to_json(db_as2, return_as_dict=True)
        logger.debug('Processing %d outgoing AS2 connection definitions', len(as2_connections))

        exported_as2 = []

        for row in as2_connections:

            # Unpack the opaque attributes into top-level keys - this is where all the AS2 fields live.
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # The identities and the endpoint are what makes the connection, they always travel ..
            item = {
                'name': row['name'],
                'as2_from': row['as2_from'],
                'as2_to': row['as2_to'],
                'endpoint_url': row['endpoint_url'],
            }

            # .. an inactive connection says so explicitly ..
            if not row['is_active']:
                item['is_active'] = False

            # .. string fields travel only when they carry a value ..
            for field in _string_fields:
                if value := row.get(field):
                    item[field] = value

            # .. integer fields travel only when they are not zero ..
            for field in _int_fields:
                if value := row.get(field):
                    item[field] = value

            # .. and boolean fields travel only when they differ from the defaults.
            for field, default in _bool_field_defaults.items():
                value = row.get(field)
                if value is not None:
                    if value != default:
                        item[field] = value

            exported_as2.append(item)

        logger.info('Successfully prepared %d outgoing AS2 connection definitions for export', len(exported_as2))
        return exported_as2

# ################################################################################################################################
# ################################################################################################################################
