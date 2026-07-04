# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, HL7
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

class OutgoingHL7MLLPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'pool_size': HL7.Default.pool_size,
    }

    connection_extra_field_defaults = {

        'should_log_messages': False,
        'logging_level': 'INFO',

        # Framing and I/O
        'start_seq': HL7.Default.start_seq,
        'end_seq': HL7.Default.end_seq,
        'recv_timeout': HL7.Default.recv_timeout,
        'max_msg_size': HL7.Default.max_msg_size,
        'read_buffer_size': HL7.Default.read_buffer_size,
        'max_wait_time': HL7.Default.max_wait_time,

        # Retry engine
        'max_retries': HL7.Default.max_retries,
        'backoff_base_seconds': HL7.Default.backoff_base_seconds,
        'backoff_cap_seconds': HL7.Default.backoff_cap_seconds,
        'backoff_jitter_percent': HL7.Default.backoff_jitter_percent,

        # Circuit breaker
        'circuit_breaker_threshold_percent': HL7.Default.circuit_breaker_threshold_percent,
        'circuit_breaker_window_seconds': HL7.Default.circuit_breaker_window_seconds,
        'circuit_breaker_reset_seconds': HL7.Default.circuit_breaker_reset_seconds,

        # TLS is off by default - it turns on when a CA bundle is configured
        'tls_ca_path': '',
        'tls_cert_path': '',
        'tls_key_path': '',
    }

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name', 'address']

# ################################################################################################################################
# ################################################################################################################################
