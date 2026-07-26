# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strtuple

    anydict = anydict
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

class MLLPField(NamedTuple):
    """ One configuration field of an MLLP channel or outgoing connection.
    """

    # The key the field is stored, imported and exported under
    name: 'str'

    # The value in force when neither the Dashboard nor enmasse supplies one
    default: 'any_'

    # Whether the field has a column of its own in generic_conn - everything else lives in the opaque blob
    is_column: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

mllp_field_list = list[MLLPField]

# ################################################################################################################################
# ################################################################################################################################

# How many bytes each unit the channel form offers stands for
Max_Msg_Size_Multipliers = {
    'kb': 1024,
    'mb': 1024 * 1024,
}

# ################################################################################################################################

def resolve_max_msg_size(value:'int', unit:'str') -> 'int':
    """ Turns a size and the unit it was entered in into bytes, which is what every bound the
    listener holds a channel to is expressed in.
    """

    # The multiplier map is keyed lower-case and a stored unit may carry either casing
    multiplier = Max_Msg_Size_Multipliers[unit.lower()]

    out = value * multiplier
    return out

# ################################################################################################################################
# ################################################################################################################################

# Every field an MLLP channel carries, in the order the Dashboard and enmasse present them.
# Name is not here because it is required rather than defaulted.
Channel_Fields:'mllp_field_list' = [

    MLLPField('is_active', True, is_column=True),
    MLLPField('hl7_version', HL7.Const.Version.v2.id),
    MLLPField('service', ''),

    # How this channel's own messages are framed and read. Each is capped at the listener's
    # matching bound rather than able to exceed it.
    MLLPField('start_seq', HL7.Default.start_seq),
    MLLPField('end_seq', HL7.Default.end_seq),
    MLLPField('recv_timeout', HL7.Default.recv_timeout),
    MLLPField('max_msg_size', HL7.Default.max_msg_size_value),
    MLLPField('max_msg_size_unit', HL7.Default.max_msg_size_unit),
    MLLPField('idle_timeout', HL7.Default.idle_timeout),
    MLLPField('keepalive_idle', HL7.Default.keepalive_idle),
    MLLPField('keepalive_interval', HL7.Default.keepalive_interval),
    MLLPField('keepalive_probe_count', HL7.Default.keepalive_probe_count),

    # Who this channel accepts a message from
    MLLPField('security_id', 0),
    MLLPField('allowed_networks', ''),

    # Parsing
    MLLPField('should_parse_on_input', True),
    MLLPField('should_validate', False),

    # Logging and audit
    MLLPField('should_log_messages', False),
    MLLPField('should_return_errors', False),
    MLLPField('is_audit_log_active', False),

    # Routing
    MLLPField('msh3_sending_app', ''),
    MLLPField('msh4_sending_facility', ''),
    MLLPField('msh5_receiving_app', ''),
    MLLPField('msh6_receiving_facility', ''),
    MLLPField('msh9_message_type', ''),
    MLLPField('msh9_trigger_event', ''),
    MLLPField('msh11_processing_id', ''),
    MLLPField('msh12_version_id', ''),
    MLLPField('is_default', False),

    # Deduplication - a TTL of zero means every message is delivered
    MLLPField('dedup_ttl_value', HL7.Default.dedup_ttl_value),
    MLLPField('dedup_ttl_unit', HL7.Default.dedup_ttl_unit),

    # Encoding, used when MSH-18 is absent or its toggle is off
    MLLPField('default_character_encoding', HL7.Default.data_encoding),

    # Message tolerance toggles
    MLLPField('normalize_line_endings', True),
    MLLPField('force_standard_delimiters', True),
    MLLPField('repair_truncated_msh', True),
    MLLPField('split_concatenated_messages', True),
    MLLPField('use_msh18_encoding', True),

    # Parser tolerance toggles
    MLLPField('normalize_obx2_value_type', True),
    MLLPField('replace_invalid_obx2_value_type', True),
    MLLPField('normalize_invalid_escape_sequences', True),
    MLLPField('normalize_obx8_abnormal_flags', True),
    MLLPField('normalize_quadruple_quoted_empty', True),
    MLLPField('allow_short_encoding_characters', True),
    MLLPField('fix_off_by_one_field_index', False),

    # REST bridge
    MLLPField('use_rest', False),
    MLLPField('rest_only', False),
    MLLPField('rest_channel_id', 0),
]

# ################################################################################################################################
# ################################################################################################################################

# Every field an MLLP outgoing connection carries. Name and address are not here
# because they are required rather than defaulted.
Outconn_Fields:'mllp_field_list' = [

    MLLPField('is_active', True, is_column=True),
    MLLPField('pool_size', HL7.Default.pool_size, is_column=True),

    # Framing and I/O
    MLLPField('start_seq', HL7.Default.start_seq),
    MLLPField('end_seq', HL7.Default.end_seq),
    MLLPField('recv_timeout', HL7.Default.recv_timeout),
    MLLPField('max_msg_size', HL7.Default.max_msg_size),
    MLLPField('read_buffer_size', HL7.Default.read_buffer_size),
    MLLPField('max_wait_time', HL7.Default.max_wait_time),

    # Logging and audit
    MLLPField('should_log_messages', False),
    MLLPField('logging_level', HL7.Default.logging_level),
    MLLPField('is_audit_log_active', False),

    # Retry engine
    MLLPField('max_retries', HL7.Default.max_retries),
    MLLPField('backoff_base_seconds', HL7.Default.backoff_base_seconds),
    MLLPField('backoff_cap_seconds', HL7.Default.backoff_cap_seconds),
    MLLPField('backoff_jitter_percent', HL7.Default.backoff_jitter_percent),

    # Circuit breaker
    MLLPField('circuit_breaker_threshold_percent', HL7.Default.circuit_breaker_threshold_percent),
    MLLPField('circuit_breaker_window_seconds', HL7.Default.circuit_breaker_window_seconds),
    MLLPField('circuit_breaker_reset_seconds', HL7.Default.circuit_breaker_reset_seconds),

    # TLS turns on once a CA bundle is configured
    MLLPField('tls_ca_path', ''),
    MLLPField('tls_cert_path', ''),
    MLLPField('tls_key_path', ''),
]

# ################################################################################################################################
# ################################################################################################################################

def get_column_defaults(fields:'mllp_field_list') -> 'anydict':
    """ The defaults of the fields that generic_conn stores in a column of their own.
    """
    out:'anydict' = {}

    for field in fields:
        if field.is_column:
            out[field.name] = field.default

    return out

# ################################################################################################################################

def get_opaque_defaults(fields:'mllp_field_list') -> 'anydict':
    """ The defaults of the fields that generic_conn stores in its opaque blob.
    """
    out:'anydict' = {}

    for field in fields:
        if not field.is_column:
            out[field.name] = field.default

    return out

# ################################################################################################################################

def get_defaults(fields:'mllp_field_list') -> 'anydict':
    """ The defaults of every field, no matter where it is stored.
    """
    out:'anydict' = {}

    for field in fields:
        out[field.name] = field.default

    return out

# ################################################################################################################################

def get_int_names(fields:'mllp_field_list') -> 'strtuple':
    """ The names of the fields holding a whole number, which the Dashboard and opaque storage
    may both hand over as text.
    """
    names = []

    for field in fields:
        is_bool = isinstance(field.default, bool)
        if isinstance(field.default, int):
            if not is_bool:
                names.append(field.name)

    out = tuple(names)
    return out

# ################################################################################################################################

def get_names(fields:'mllp_field_list') -> 'strtuple':
    """ The names of every field, in declaration order.
    """
    names = []

    for field in fields:
        names.append(field.name)

    out = tuple(names)
    return out

# ################################################################################################################################
# ################################################################################################################################

# The toggles the Rust parser's tolerance configuration is built from, named here rather than
# in each of the places that build one.
Tolerance_Names = (
    'normalize_obx2_value_type',
    'replace_invalid_obx2_value_type',
    'normalize_invalid_escape_sequences',
    'normalize_obx8_abnormal_flags',
    'normalize_quadruple_quoted_empty',
    'allow_short_encoding_characters',
    'fix_off_by_one_field_index',
)

# ################################################################################################################################
# ################################################################################################################################

Channel_Column_Defaults = get_column_defaults(Channel_Fields)
Channel_Opaque_Defaults = get_opaque_defaults(Channel_Fields)
Channel_Defaults        = get_defaults(Channel_Fields)
Channel_Int_Names       = get_int_names(Channel_Fields)
Channel_Names           = get_names(Channel_Fields)

Outconn_Column_Defaults = get_column_defaults(Outconn_Fields)
Outconn_Opaque_Defaults = get_opaque_defaults(Outconn_Fields)
Outconn_Defaults        = get_defaults(Outconn_Fields)
Outconn_Int_Names       = get_int_names(Outconn_Fields)
Outconn_Names           = get_names(Outconn_Fields)

# ################################################################################################################################
# ################################################################################################################################
