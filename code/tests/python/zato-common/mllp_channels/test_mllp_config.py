# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, HL7
from zato.common.hl7.fhir.fields import Outgoing_Defaults as FHIR_Outgoing_Defaults
from zato.common.hl7.mllp.fields import Channel_Defaults, Channel_Names, Channel_Text_Names, Max_Message_Size_Multipliers, \
    Outgoing_Defaults
from zato.common.util.api import parse_simple_type
from zato.server.service.internal.generic.connection import ensure_ints, skip_simple_type

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

# What the wizard posts under a text field and what zato.generic.connection.create would otherwise make of it -
# a bool, an integer, a float
_text_spellings = ['0', '1', 'on', 'yes', 'no', '007', '0123', '0x0b', '1e3', 'True']

def _store_as_the_service_does(name:'str', posted:'str') -> 'any_':
    """ What the generic connection service stores for one posted key - the simple-type parser for every key not
    in its skip set, then the integer fields made integers.
    """
    if name in skip_simple_type:
        value = posted
    else:
        value = parse_simple_type(posted)
    data = {name: value}
    ensure_ints(data)
    return data[name]

# ################################################################################################################################
# ################################################################################################################################

class TestTheWizardRoundTrip:
    """ A channel's fields as they travel from the wizard's save through the generic connection service.
    """

# ################################################################################################################################

    def test_the_text_fields_are_channel_fields_the_service_leaves_as_text(self:'any_') -> 'None':
        for name in Channel_Text_Names:
            assert name in Channel_Names
            assert name in skip_simple_type

# ################################################################################################################################

    def test_a_text_field_stays_the_text_it_was_posted_as(self:'any_') -> 'None':
        """ A sending application named 007 is stored as the text 007, a start sequence of 01 as the text 01 -
        whatever a text field is spelled like, the edit page reopens showing it.
        """
        for name in Channel_Text_Names:
            for posted in _text_spellings:
                stored = _store_as_the_service_does(name, posted)
                assert stored == posted, (name, posted, stored)

# ################################################################################################################################
# ################################################################################################################################
