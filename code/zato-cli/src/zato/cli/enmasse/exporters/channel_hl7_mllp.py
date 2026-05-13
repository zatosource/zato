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

    channel_hl7_mllp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

Channel_Optional_Fields = [
    'service',
    'should_log_messages',
    'should_return_errors',
    'logging_level',
    'max_msg_size',
    'max_msg_size_unit',
    'read_buffer_size',
    'recv_timeout',
    'start_seq',
    'end_seq',
    'msh3_sending_app',
    'msh4_sending_facility',
    'msh5_receiving_app',
    'msh6_receiving_facility',
    'msh9_message_type',
    'msh9_trigger_event',
    'msh11_processing_id',
    'msh12_version_id',
    'is_default',
    'dedup_ttl_value',
    'dedup_ttl_unit',
    'default_character_encoding',
    'normalize_line_endings',
    'force_standard_delimiters',
    'repair_truncated_msh',
    'split_concatenated_messages',
    'use_msh18_encoding',
    'normalize_obx2_value_type',
    'replace_invalid_obx2_value_type',
    'normalize_invalid_escape_sequences',
    'normalize_obx8_abnormal_flags',
    'normalize_quadruple_quoted_empty',
    'allow_short_encoding_characters',
    'fix_off_by_one_field_index',
]

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'channel_hl7_mllp_def_list':
        """ Exports HL7 MLLP channel definitions.
        """
        logger.info('Exporting HL7 MLLP channel definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP)

        if not db_items:
            logger.info('No HL7 MLLP channel definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)

        connection_count = len(connections)
        noun = 'definition' if connection_count == 1 else 'definitions'
        logger.debug('Processing %d HL7 MLLP channel %s', connection_count, noun)

        exported = []

        for row in connections:

            # Merge opaque attributes into the row so all fields are accessible at the top level ..
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # .. build the export item with the channel name and any non-empty optional fields ..
            item = {
                'name': row['name'],
            }

            for field in Channel_Optional_Fields:
                if value := row.get(field):
                    item[field] = value

            # .. and add it to the output.
            exported.append(item)

        exported_count = len(exported)
        noun = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d HL7 MLLP channel %s for export', exported_count, noun)
        return exported

# ################################################################################################################################
# ################################################################################################################################
