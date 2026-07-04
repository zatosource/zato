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

    outgoing_hl7_mllp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

Outgoing_Optional_Fields = [
    'should_log_messages',
    'logging_level',
    'start_seq',
    'end_seq',
    'recv_timeout',
    'max_msg_size',
    'read_buffer_size',
    'max_wait_time',
    'max_retries',
    'backoff_base_seconds',
    'backoff_cap_seconds',
    'backoff_jitter_percent',
    'circuit_breaker_threshold_percent',
    'circuit_breaker_window_seconds',
    'circuit_breaker_reset_seconds',
]

# ################################################################################################################################
# ################################################################################################################################

class OutgoingHL7MLLPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'outgoing_hl7_mllp_def_list':
        """ Exports outgoing HL7 MLLP connection definitions.
        """
        logger.info('Exporting outgoing HL7 MLLP definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP)

        if not db_items:
            logger.info('No outgoing HL7 MLLP definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)

        connection_count = len(connections)
        noun = 'definition' if connection_count == 1 else 'definitions'
        logger.debug('Processing %d outgoing HL7 MLLP %s', connection_count, noun)

        exported = []

        for row in connections:

            # Merge opaque attributes into the row so all fields are accessible at the top level ..
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # .. build the export item with the connection name, its address and any non-empty optional fields ..
            item = {
                'name': row['name'],
                'address': row['address'],
            }

            for field in Outgoing_Optional_Fields:
                if value := row.get(field):
                    item[field] = value

            # .. and add it to the output.
            exported.append(item)

        exported_count = len(exported)
        noun = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d outgoing HL7 MLLP %s for export', exported_count, noun)
        return exported

# ################################################################################################################################
# ################################################################################################################################
