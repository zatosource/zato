# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

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

    ibm_mq_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

CHANNEL_OPTIONAL_FIELDS = [
    'queue_manager', 'mq_channel_name', 'queue', 'service', 'username',
    'remove_jms_headers', 'ssl', 'cipher_spec',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
]

OUTGOING_OPTIONAL_FIELDS = [
    'queue_manager', 'mq_channel_name', 'queue', 'username',
    'ssl', 'cipher_spec',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
]

# ################################################################################################################################
# ################################################################################################################################

class ChannelIBMMQExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'ibm_mq_def_list':
        """ Exports IBM MQ channel definitions.
        """
        logger.info('Exporting IBM MQ channel definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ)

        if not db_items:
            logger.info('No IBM MQ channel definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d IBM MQ channel definitions', len(connections))

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

            for field in CHANNEL_OPTIONAL_FIELDS:
                if value := row.get(field):
                    item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d IBM MQ channel definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################

class OutgoingIBMMQExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'ibm_mq_def_list':
        """ Exports IBM MQ outgoing definitions.
        """
        logger.info('Exporting IBM MQ outgoing definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ)

        if not db_items:
            logger.info('No IBM MQ outgoing definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d IBM MQ outgoing definitions', len(connections))

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

            for field in OUTGOING_OPTIONAL_FIELDS:
                if value := row.get(field):
                    item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d IBM MQ outgoing definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
