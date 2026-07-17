# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import AMQP, AMQP_Subtype
from zato.common.odb.model import to_json
from zato.common.odb.query import channel_amqp_list, out_amqp_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    amqp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The ODB stores delivery modes as AMQP integers, the YAML configuration uses these string names
_delivery_mode_by_id = {
    1: 'non_persistent',
    2: 'persistent',
}

_default_delivery_mode = 'persistent'

_channel_optional_fields = ['username', 'consumer_tag_prefix', 'data_format']
_outgoing_optional_fields = ['username', 'content_type', 'content_encoding', 'expiration', 'user_id', 'app_id']

# ################################################################################################################################
# ################################################################################################################################

class ChannelAMQPExporter:
    """ One exporter serves every subtype of the AMQP implementation - the exporter is registered
    once per subtype, e.g. under the channel_amqp key and under the channel_azure_service_bus key.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter', subtype:'str') -> 'None':
        self.exporter = exporter
        self.subtype_key = subtype
        self.subtype = AMQP_Subtype[subtype]

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'amqp_def_list':
        """ Exports channel definitions of this exporter's subtype.
        """
        label = self.subtype['label']
        logger.info('Exporting %s channel definitions', label)

        # Only channels of this exporter's subtype are taken into account
        db_items = channel_amqp_list(session, cluster_id, self.subtype_key, False)
        channels = to_json(db_items, return_as_dict=True)

        exported = []

        for row in channels:

            item = {
                'name': row['name'],
                'address': row['address'],
                'queue': row['queue'],
                'service': row['service_name'],
            }

            for field in _channel_optional_fields:
                if value := row[field]:
                    item[field] = value

            # Only non-default values are exported ..
            if row['pool_size'] != AMQP.DEFAULT.POOL_SIZE:
                item['pool_size'] = row['pool_size']

            if row['prefetch_count'] != AMQP.DEFAULT.PREFETCH_COUNT:
                item['prefetch_count'] = row['prefetch_count']

            # .. and the same goes for the acknowledgement mode.
            if row['ack_mode'] != AMQP.ACK_MODE.ACK.id:
                item['ack_mode'] = row['ack_mode']

            exported.append(item)

        logger.info('Successfully prepared %d %s channel definitions for export', len(exported), label)
        return exported

# ################################################################################################################################
# ################################################################################################################################

class OutgoingAMQPExporter:
    """ One exporter serves every subtype of the AMQP implementation - the exporter is registered
    once per subtype, e.g. under the outgoing_amqp key and under the outgoing_azure_service_bus key.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter', subtype:'str') -> 'None':
        self.exporter = exporter
        self.subtype_key = subtype
        self.subtype = AMQP_Subtype[subtype]

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'amqp_def_list':
        """ Exports outgoing connection definitions of this exporter's subtype.
        """
        label = self.subtype['label']
        logger.info('Exporting outgoing %s connection definitions', label)

        # Only connections of this exporter's subtype are taken into account
        db_items = out_amqp_list(session, cluster_id, self.subtype_key, False)
        connections = to_json(db_items, return_as_dict=True)

        exported = []

        for row in connections:

            item = {
                'name': row['name'],
                'address': row['address'],
            }

            for field in _outgoing_optional_fields:
                if value := row[field]:
                    item[field] = value

            # The ODB stores an integer, the YAML configuration uses a string name ..
            delivery_mode = _delivery_mode_by_id[row['delivery_mode']]

            # .. and only non-default values are exported.
            if delivery_mode != _default_delivery_mode:
                item['delivery_mode'] = delivery_mode

            if row['priority'] != AMQP.DEFAULT.PRIORITY:
                item['priority'] = row['priority']

            if row['pool_size'] != AMQP.DEFAULT.POOL_SIZE:
                item['pool_size'] = row['pool_size']

            exported.append(item)

        logger.info('Successfully prepared %d outgoing %s connection definitions for export', len(exported), label)
        return exported

# ################################################################################################################################
# ################################################################################################################################
