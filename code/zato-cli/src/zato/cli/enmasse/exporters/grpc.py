# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, GRPC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    grpc_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields exported only when they carry a value
OUTGOING_OPTIONAL_FIELDS = [
    'tls_ca_certs_file',
    'proto_path',
    'stub_module',
    'stub_class',
]

# Numeric fields exported only when they differ from the defaults
OUTGOING_NUMERIC_DEFAULTS = {
    'ping_timeout': GRPC.Default.Ping_Timeout,
    'max_send_message_size': GRPC.Default.Max_Message_Size,
    'max_recv_message_size': GRPC.Default.Max_Message_Size,
}

# ################################################################################################################################
# ################################################################################################################################

class OutgoingGRPCExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'grpc_def_list':
        """ Exports gRPC outgoing definitions.
        """
        logger.info('Exporting gRPC outgoing definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_GRPC)

        if not db_items:
            logger.info('No gRPC outgoing definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d gRPC outgoing definitions', len(connections))

        exported = []

        for row in connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
            }

            if address := row.get('address'):
                item['address'] = address

            if security_name := row.get('security_name'):
                item['security'] = security_name

            # TLS is on by default, so only its being off is worth exporting
            is_tls = row.get('is_tls')
            if is_tls is False:
                item['is_tls'] = False

            for field in OUTGOING_OPTIONAL_FIELDS:
                if value := row.get(field):
                    item[field] = value

            for field, default in OUTGOING_NUMERIC_DEFAULTS.items():
                if value := row.get(field):
                    if value != default:
                        item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d gRPC outgoing definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
