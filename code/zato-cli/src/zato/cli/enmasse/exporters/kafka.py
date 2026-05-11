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

    kafka_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

CHANNEL_OPTIONAL_FIELDS = [
    'topic', 'group_id', 'service', 'ssl',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
]

CHANNEL_OPAQUE_FIELDS = [
    'topic', 'group_id', 'service', 'ssl',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
]

OUTGOING_OPTIONAL_FIELDS = [
    'topic', 'ssl',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
]

OUTGOING_OPAQUE_FIELDS = [
    'topic', 'ssl',
    'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file',
]

# ################################################################################################################################
# ################################################################################################################################

class ChannelKafkaExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'kafka_def_list':
        """ Exports Kafka channel definitions.
        """
        logger.info('Exporting Kafka channel definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA)

        if not db_items:
            logger.info('No Kafka channel definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d Kafka channel definitions', len(connections))

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

        logger.info('Successfully prepared %d Kafka channel definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################

class OutgoingKafkaExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'kafka_def_list':
        """ Exports Kafka outgoing definitions.
        """
        logger.info('Exporting Kafka outgoing definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA)

        if not db_items:
            logger.info('No Kafka outgoing definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d Kafka outgoing definitions', len(connections))

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

        logger.info('Successfully prepared %d Kafka outgoing definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
