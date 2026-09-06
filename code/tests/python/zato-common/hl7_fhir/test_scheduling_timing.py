# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, one_resource, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every scheduling test builds on.
MSH = 'MSH|^~\\&|SCHED|GENHOSP|EHR|GENHOSP|20260320100000||SIU^S12^SIU_S12|MSG00001|P|2.5.1'
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestTQ1AfterSCH:
    """ A TQ1 that follows an SCH is the appointment's timing, not a Basic resource.
    """

    def test_tq1_fills_the_times_sch_left_empty(self) -> 'None':
        sch = segment('SCH', {1: 'APT1^SCHED', 7: 'FOLLOWUP^Follow-up visit^L'})
        tq1 = segment('TQ1', {1: '1', 6: '30^min', 7: '20260401140000', 8: '20260401143000'})

        bundle = convert(MSH, sch, tq1, PID)
        appointment = one_resource(bundle, 'Appointment')

        assert appointment['start'] == '2026-04-01T14:00:00+00:00'
        assert appointment['end'] == '2026-04-01T14:30:00+00:00'
        assert appointment['minutesDuration'] == 30

        # The TQ1 was consumed, so nothing became a Basic resource.
        assert resources_of_type(bundle, 'Basic') == []

# ################################################################################################################################

    def test_tq1_repeating_sch_times_adds_nothing(self) -> 'None':
        sch = segment('SCH', {1: 'APT1^SCHED', 7: 'FOLLOWUP^Follow-up visit^L', 11: '^^^20260401140000^20260401143000'})
        tq1 = segment('TQ1', {1: '1', 7: '20260401140000', 8: '20260401143000'})

        bundle = convert(MSH, sch, tq1, PID)
        appointment = one_resource(bundle, 'Appointment')

        assert appointment['start'] == '2026-04-01T14:00:00+00:00'
        assert appointment['end'] == '2026-04-01T14:30:00+00:00'

        # A repeat of what SCH-11 already said is dropped.
        assert 'extension' not in appointment

# ################################################################################################################################

    def test_tq1_conflicting_with_sch_times_is_preserved(self) -> 'None':
        sch = segment('SCH', {1: 'APT1^SCHED', 7: 'FOLLOWUP^Follow-up visit^L', 11: '^^^20260401140000^20260401143000'})
        tq1 = segment('TQ1', {1: '1', 7: '20260401150000'})

        bundle = convert(MSH, sch, tq1, PID)
        appointment = one_resource(bundle, 'Appointment')

        # SCH-11 keeps the slot and the conflicting TQ1 start stays preserved.
        assert appointment['start'] == '2026-04-01T14:00:00+00:00'

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/TQ1-7',
            'valueString': '20260401150000',
        } in appointment['extension']

# ################################################################################################################################

    def test_tq1_duration_defers_to_sch(self) -> 'None':
        sch = segment('SCH', {1: 'APT1^SCHED', 7: 'FOLLOWUP^Follow-up visit^L', 9: '30', 10: 'min'})
        tq1 = segment('TQ1', {1: '1', 6: '45^min'})

        bundle = convert(MSH, sch, tq1, PID)
        appointment = one_resource(bundle, 'Appointment')

        # SCH-9 and SCH-10 already made the minutes, so the TQ1 duration stays preserved.
        assert appointment['minutesDuration'] == 30

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/TQ1-6',
            'valueString': '45^min',
        } in appointment['extension']

# ################################################################################################################################

    def test_tq1_leftovers_are_preserved(self) -> 'None':
        sch = segment('SCH', {1: 'APT1^SCHED', 7: 'FOLLOWUP^Follow-up visit^L'})
        tq1 = segment('TQ1', {1: '1', 7: '20260401140000', 11: 'Arrive fifteen minutes early'})

        bundle = convert(MSH, sch, tq1, PID)
        appointment = one_resource(bundle, 'Appointment')

        assert appointment['start'] == '2026-04-01T14:00:00+00:00'

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/TQ1-11',
            'valueString': 'Arrive fifteen minutes early',
        } in appointment['extension']

# ################################################################################################################################
# ################################################################################################################################

class TestSCHEnteredBy:
    """ SCH-20 - who entered the appointment - becomes a participant in the enterer role.
    """

    def test_sch_20_is_an_enterer_participant(self) -> 'None':
        sch = segment('SCH', {1: 'APT1^SCHED', 7: 'FOLLOWUP^Follow-up visit^L', 20: '3001^Miller^Thomas'})

        bundle = convert(MSH, sch, PID)
        appointment = one_resource(bundle, 'Appointment')

        # The enterer joins the patient among the participants ..
        participants = appointment['participant']

        enterers = []

        for item in participants:
            if 'type' in item:
                enterers.append(item)

        assert len(enterers) == 1
        enterer = enterers[0]

        assert enterer['status'] == 'accepted'
        assert enterer['type'] == [{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/provenance-participant-type',
                'code': 'enterer',
            }],
        }]

        # .. backed by a Practitioner with the name SCH-20 spelled out ..
        practitioner = one_resource(bundle, 'Practitioner')

        assert practitioner['name'] == [{'family': 'Miller', 'given': ['Thomas']}]
        assert practitioner['identifier'] == [{'value': '3001'}]

        # .. and the field was consumed rather than preserved.
        assert 'extension' not in appointment

# ################################################################################################################################
# ################################################################################################################################
