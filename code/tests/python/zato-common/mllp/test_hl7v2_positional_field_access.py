# -*- coding: utf-8 -*-

from __future__ import annotations

from zato.hl7v2.v2_9.segments import MSH, ORC, PID
from zato.hl7v2.v2_9.datatypes import CX, XPN

# ################################################################################################################################
# ################################################################################################################################

class TestPositionalSetAndSerialize:
    """ Verify that positional attribute access serializes retired fields correctly.
    """

    def test_pid_retired_phone_field(self) -> 'None':

        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_13 = '0221-4523890'

        er7 = pid.serialize()

        assert '0221-4523890' in er7

        # PID-13 is at pipe index 13 in the ER7 ..
        fields = er7.split('|')
        field_value = fields[13]

        assert field_value == '0221-4523890'

# ################################################################################################################################

    def test_pid_two_retired_phone_fields(self) -> 'None':

        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_13 = '0221-4523890'
        pid.pid_14 = '0221-4523891'

        er7 = pid.serialize()
        fields = er7.split('|')

        assert fields[13] == '0221-4523890'
        assert fields[14] == '0221-4523891'

# ################################################################################################################################

    def test_orc_retired_fields(self) -> 'None':

        orc = ORC()
        orc.order_control = 'NW'
        orc.orc_7 = '1^^^20250312091500^^R'
        orc.orc_10 = '34567890^FERNANDEZ^CARLOS^^^DR'
        orc.orc_11 = ''
        orc.orc_12 = '34567890^FERNANDEZ^CARLOS^^^DR'

        er7 = orc.serialize()
        fields = er7.split('|')

        assert fields[7] == '1^^^20250312091500^^R'
        assert fields[10] == '34567890^FERNANDEZ^CARLOS^^^DR'
        assert fields[11] == ''
        assert fields[12] == '34567890^FERNANDEZ^CARLOS^^^DR'

# ################################################################################################################################
# ################################################################################################################################

class TestPositionalReadBack:
    """ Verify that positional attributes can be read back after being set.
    """

    def test_read_back(self) -> 'None':

        pid = PID()
        pid.pid_13 = '0221-4523890'

        out = pid.pid_13

        assert out == '0221-4523890'

# ################################################################################################################################

    def test_read_back_missing_raises(self) -> 'None':

        pid = PID()

        raised = False

        try:
            _ = pid.pid_99
        except AttributeError:
            raised = True

        assert raised

# ################################################################################################################################
# ################################################################################################################################

class TestDescriptorPriority:
    """ Verify that HL7Field descriptor values take priority over positional values at the same position.
    """

    def test_descriptor_wins(self) -> 'None':

        pid = PID()
        pid.set_id_pid = '1'

        # PID-5 is patient_name (HL7Field descriptor) ..
        patient_name = XPN()
        patient_name.xpn_1 = 'SMITH'
        patient_name.xpn_2 = 'JOHN'
        pid.patient_name = patient_name

        # .. set the same position via positional access ..
        pid.pid_5 = 'OVERRIDE^VALUE'

        # .. the descriptor value must win.
        er7 = pid.serialize()
        fields = er7.split('|')

        assert fields[5] == 'SMITH^JOHN'

# ################################################################################################################################
# ################################################################################################################################

class TestPositionalPadding:
    """ Verify that positional fields produce correct empty-field padding.
    """

    def test_gap_between_descriptor_and_positional(self) -> 'None':

        pid = PID()
        pid.set_id_pid = '1'
        pid.pid_13 = '0221-4523890'

        er7 = pid.serialize()
        fields = er7.split('|')

        # Positions 2 through 12 must all be empty ..
        for position in range(2, 13):
            assert fields[position] == ''

        # .. and position 13 has the phone number.
        assert fields[13] == '0221-4523890'

# ################################################################################################################################

    def test_positional_beyond_last_descriptor(self) -> 'None':

        pid = PID()
        pid.set_id_pid = '1'
        pid.patient_account_number = 'ACCT001'
        pid.pid_42 = 'EXTRA_VALUE'

        er7 = pid.serialize()
        fields = er7.split('|')

        # patient_account_number is at position 18 ..
        assert fields[18] == 'ACCT001'

        # .. and position 42 has the extra value.
        assert fields[42] == 'EXTRA_VALUE'

# ################################################################################################################################

    def test_mixed_descriptor_and_positional(self) -> 'None':

        pid = PID()
        pid.set_id_pid = '1'

        patient_id = CX()
        patient_id.cx_1 = '28456712'
        patient_id.cx_4 = 'RENAPER'
        patient_id.cx_5 = 'NI'
        pid.patient_identifier_list = patient_id

        pid.pid_13 = '0221-4523890'
        pid.patient_account_number = '28456712'

        er7 = pid.serialize()
        fields = er7.split('|')

        assert fields[1] == '1'
        assert fields[3] == '28456712^^^RENAPER^NI'
        assert fields[13] == '0221-4523890'
        assert fields[18] == '28456712'

# ################################################################################################################################
# ################################################################################################################################
