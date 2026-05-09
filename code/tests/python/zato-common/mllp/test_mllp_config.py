# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, HL7

# ################################################################################################################################
# ################################################################################################################################

class TestConnectionTypeConstants:
    """ Verifies that MLLP connection type constants have the expected string values.
    """

# ################################################################################################################################

    def test_channel_type_value(self) -> 'None':
        """ The channel type string must be 'channel-hl7-mllp'.
        """
        assert GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP == 'channel-hl7-mllp'

# ################################################################################################################################

    def test_outconn_type_value(self) -> 'None':
        """ The outconn type string must be 'outconn-hl7-mllp'.
        """
        assert GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP == 'outconn-hl7-mllp'

# ################################################################################################################################
# ################################################################################################################################

class TestHL7DefaultValues:
    """ Verifies that HL7.Default contains the expected default values
    for retry, circuit breaker, dedup, and TLS configuration.
    """

# ################################################################################################################################

    def test_retry_defaults(self) -> 'None':
        """ Retry engine defaults must match the documented values.
        """
        assert HL7.Default.max_retries == 5
        assert HL7.Default.backoff_base_seconds == 1
        assert HL7.Default.backoff_cap_seconds == 300
        assert HL7.Default.backoff_jitter_percent == 10

# ################################################################################################################################

    def test_circuit_breaker_defaults(self) -> 'None':
        """ Circuit breaker defaults must match the documented values.
        """
        assert HL7.Default.circuit_breaker_threshold_percent == 50
        assert HL7.Default.circuit_breaker_window_seconds == 60
        assert HL7.Default.circuit_breaker_reset_seconds == 60

# ################################################################################################################################

    def test_dedup_defaults(self) -> 'None':
        """ Dedup defaults must match the documented values.
        """
        assert HL7.Default.dedup_ttl_value == 14
        assert HL7.Default.dedup_ttl_unit == 'days'

# ################################################################################################################################

    def test_tls_default(self) -> 'None':
        """ TLS minimum version default must be TLSv1.2.
        """
        assert HL7.Default.tls_version_min == 'TLSv1.2'

# ################################################################################################################################

    def test_framing_defaults(self) -> 'None':
        """ MLLP framing defaults must match the documented values.
        """
        assert HL7.Default.recv_timeout == 250
        assert HL7.Default.start_seq == '0b'

# ################################################################################################################################
# ################################################################################################################################
