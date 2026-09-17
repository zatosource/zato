# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shipped parser is what the channels run, so what its source promises about a required segment the wire
# leaves out is asserted against the binary the tree carries - a sender that skips EVN, as the HAPI quickstart
# does, is still understood as long as the message goes on with a segment the structure knows.

# Zato
from zato.common.typing_ import cast_
from zato.hl7v2 import parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.hl7v2.v2_9.messages import ADT_A01 as adt_a01
    adt_a01 = adt_a01

# ################################################################################################################################
# ################################################################################################################################

_msh = 'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.5\r'
_evn = 'EVN|A01|20260115103000\r'
_pid = 'PID|1||NHS7788990^^^NHS^NH||SMITH^JOHN^A||19850315|M\r'

_mrn = 'NHS7788990'

# ################################################################################################################################
# ################################################################################################################################

class TestParseMissingSegment:

    def test_an_admission_without_evn_parses_and_its_patient_is_read(self) -> 'None':

        message = parse_hl7(_msh + _pid)
        message = cast_('adt_a01', message)

        assert message.pid.patient_identifier_list[0].id_number == _mrn
        assert message.msh.message_control_id == 'MSG000001'

    def test_an_admission_with_evn_reads_the_same(self) -> 'None':

        with_evn = parse_hl7(_msh + _evn + _pid)
        without_evn = parse_hl7(_msh + _pid)

        with_evn = cast_('adt_a01', with_evn)
        without_evn = cast_('adt_a01', without_evn)

        assert with_evn.pid.patient_identifier_list[0].id_number == without_evn.pid.patient_identifier_list[0].id_number
        assert with_evn.evn.recorded_date_time == '20260115103000'

    def test_validation_on_does_not_refuse_the_missing_evn_either(self) -> 'None':

        message = parse_hl7(_msh + _pid, validate=True)
        message = cast_('adt_a01', message)

        assert message.pid.patient_identifier_list[0].id_number == _mrn

# ################################################################################################################################
# ################################################################################################################################
