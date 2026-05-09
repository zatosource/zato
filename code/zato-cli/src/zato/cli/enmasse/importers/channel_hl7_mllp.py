# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
        'should_validate': True,
        'should_parse_on_input': True,
        'data_format': 'hl7-v2',
        'hl7_version': 'hl7-v2',
    }

    connection_extra_field_defaults = {

        'service': '',
        'should_log_messages': False,
        'should_return_errors': False,
        'logging_level': 'INFO',

        'max_msg_size': 2,
        'max_msg_size_unit': 'MB',
        'read_buffer_size': 32768,
        'recv_timeout': 250,
        'start_seq': '0b',
        'end_seq': '1c 0d',

        # Routing fields
        'msh3_sending_app': '',
        'msh4_sending_facility': '',
        'msh5_receiving_app': '',
        'msh6_receiving_facility': '',
        'msh9_message_type': '',
        'msh9_trigger_event': '',
        'msh11_processing_id': '',
        'msh12_version_id': '',
        'is_default': False,

        # Deduplication
        'dedup_ttl_value': None,
        'dedup_ttl_unit': None,

        # Encoding
        'default_character_encoding': 'utf-8',

        # Tolerance toggles
        'normalize_line_endings': True,
        'force_standard_delimiters': True,
        'repair_truncated_msh': True,
        'split_concatenated_messages': True,
        'use_msh18_encoding': True,
        'normalize_obx2_value_type': True,
        'replace_invalid_obx2_value_type': True,
        'normalize_invalid_escape_sequences': True,
        'normalize_obx8_abnormal_flags': True,
        'normalize_quadruple_quoted_empty': True,
        'allow_short_encoding_characters': True,
        'fix_off_by_one_field_index': False,

        # REST bridge
        'use_rest': False,
        'rest_only': False,
        'rest_channel_id': None,
    }

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name']

# ################################################################################################################################
# ################################################################################################################################
