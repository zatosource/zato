# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, HL7
from zato.common.hl7.fhir.fields import Outgoing_Defaults as FHIR_Outgoing_Defaults
from zato.common.hl7.mllp.fields import Channel_Defaults, Max_Message_Size_Multipliers, Outgoing_Defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    # Add dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionTypeConstants:
    """ The MLLP connection type constants.
    """

# ################################################################################################################################

    def test_channel_type_value(self:'any_') -> 'None':

        assert GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP == 'channel-hl7-mllp'

# ################################################################################################################################

    def test_outconn_type_value(self:'any_') -> 'None':

        assert GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP == 'outconn-hl7-mllp'

# ################################################################################################################################
# ################################################################################################################################

class TestHL7DefaultValues:
    """ The HL7 defaults.
    """

# ################################################################################################################################

    def test_retry_defaults(self:'any_') -> 'None':

        assert HL7.Default.max_retries == 5
        assert HL7.Default.backoff_base_seconds == 1
        assert HL7.Default.backoff_cap_seconds == 300
        assert HL7.Default.backoff_jitter_percent == 10

# ################################################################################################################################

    def test_circuit_breaker_defaults(self:'any_') -> 'None':

        assert HL7.Default.circuit_breaker_threshold_percent == 50
        assert HL7.Default.circuit_breaker_window_seconds == 60
        assert HL7.Default.circuit_breaker_reset_seconds == 60

# ################################################################################################################################

    def test_deduplication_defaults(self:'any_') -> 'None':

        assert HL7.Default.dedup_ttl_value == 0
        assert HL7.Default.dedup_ttl_unit == 'days'

# ################################################################################################################################

    def test_tls_default(self:'any_') -> 'None':

        assert HL7.Default.tls_version_min == 'TLSv1.2'

# ################################################################################################################################

    def test_framing_defaults(self:'any_') -> 'None':

        assert HL7.Default.recv_timeout == 250
        assert HL7.Default.start_seq == '0b'

# ################################################################################################################################

    def test_max_msg_size_defaults(self:'any_') -> 'None':
        """ The value plus unit a channel is configured with and the byte count an outgoing
        connection is configured with must describe the same size.
        """
        unit = HL7.Default.max_msg_size_unit
        multiplier = Max_Message_Size_Multipliers[unit]
        channel_bytes = HL7.Default.max_msg_size_value * multiplier

        assert channel_bytes == HL7.Default.max_msg_size

# ################################################################################################################################

    def test_the_audit_log_is_on_by_default(self:'any_') -> 'None':
        """ The audit log is on by default.
        """
        assert Channel_Defaults['is_audit_log_active'] is True
        assert Outgoing_Defaults['is_audit_log_active'] is True
        assert FHIR_Outgoing_Defaults['is_audit_log_active'] is True

# ################################################################################################################################
# ################################################################################################################################
