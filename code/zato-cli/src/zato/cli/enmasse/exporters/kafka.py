# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.common.api import GENERIC, KAFKA
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr
from zato.cli.enmasse.util.delivery import export_delivery_fields
from zato.cli.enmasse.util.invocation import Retry_Field_Defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import any_, anydict, anylist, list_, strlist

    any_ = any_
    anylist = anylist
    strlist = strlist

    kafka_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_consumer = KAFKA.Consumer
_producer = KAFKA.Producer

# The key the importer reads the security definition's name from.
_security_name_field = 'security_name'
_security_export_key = 'security'

# The fields both kinds of connection carry, each with the default it is not exported at
_common_field_defaults:'anydict' = {
    'sasl_mechanism': '',
    'ssl': False,
    'ssl_ca_file': None,
    'ssl_cert_file': None,
    'ssl_key_file': None,
}

# A channel's fields, the topics and the routing rules excluded
Channel_Field_Defaults:'anydict' = dict(_common_field_defaults)
Channel_Field_Defaults.update({
    'group_id': '',
    'service': '',
    'is_audit_log_active': True,
    'is_audit_export_payload_active': False,
})

for _name, _default in _consumer.Defaults.items():
    if _name not in (_consumer.Field_Topics, _consumer.Field_Routing):
        Channel_Field_Defaults[_name] = _default

Channel_Field_Defaults.update(Retry_Field_Defaults)

# An outgoing connection's fields
Outgoing_Field_Defaults:'anydict' = dict(_common_field_defaults)
Outgoing_Field_Defaults.update({
    'topic': '',
    'is_audit_log_active': True,
    'is_audit_export_payload_active': False,
})
Outgoing_Field_Defaults.update(_producer.Defaults)
Outgoing_Field_Defaults.update(Retry_Field_Defaults)

# ################################################################################################################################
# ################################################################################################################################

def export_fields(item:'anydict', row:'anydict', field_defaults:'anydict') -> 'None':
    """ Copies to the exported definition each field whose value is not its default.
    """
    for name, default in field_defaults.items():

        value = row.get(name)

        if value is None:
            continue

        if value == default:
            continue

        item[name] = value

# ################################################################################################################################

def topics_to_list(row:'anydict') -> 'strlist':
    """ A channel's topics as a list, out of the stored one-per-line text.
    """
    text = row.get(_consumer.Field_Topics)

    # A row stored before the list has `topic` alone.
    if not text:
        text = row['topic']

    out:'strlist' = []

    for line in text.replace(',', '\n').splitlines():
        line = line.strip()
        if line:
            out.append(line)

    return out

# ################################################################################################################################

def routing_to_list(row:'anydict') -> 'anylist':
    """ A channel's routing rules as a list of mappings, out of the stored JSON text, each mapping carrying
    only the keys the rule sets.
    """
    value = row.get(_consumer.Field_Routing)

    if not value:
        return []

    rules = loads(value)
    out:'anylist' = []

    for rule in rules:
        item = {}

        for key in KAFKA.Routing.KeyList:
            if rule[key]:
                item[key] = rule[key]

        out.append(item)

    return out

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

            opaque = {}

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
            }

            if row.get('is_active') is False:
                item['is_active'] = False

            if address := row.get('address'):
                item['address'] = address

            # The topics are exported as a list ..
            if topics := topics_to_list(row):
                item[_consumer.Field_Topics] = topics

            export_fields(item, row, Channel_Field_Defaults)

            # .. and so are the routing rules.
            if routing := routing_to_list(row):
                item[_consumer.Field_Routing] = routing

            export_delivery_fields(item, opaque)

            if security_name := row.get(_security_name_field):
                item[_security_export_key] = security_name

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

            opaque = {}

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
            }

            if row.get('is_active') is False:
                item['is_active'] = False

            if address := row.get('address'):
                item['address'] = address

            export_fields(item, row, Outgoing_Field_Defaults)
            export_delivery_fields(item, opaque)

            if security_name := row.get(_security_name_field):
                item[_security_export_key] = security_name

            exported.append(item)

        logger.info('Successfully prepared %d Kafka outgoing definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
