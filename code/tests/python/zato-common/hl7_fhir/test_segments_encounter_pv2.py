# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, one_resource, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every PV2 test builds on.
MSH = 'MSH|^~\\&|EHR|GENHOSP|CARE|GENHOSP|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1'
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'
PV1 = 'PV1|1|I|ICU^101^A'

# ################################################################################################################################
# ################################################################################################################################

class TestPV2:
    """ PV2 fills in the visit details on an existing Encounter.
    """

    def test_prior_pending_location_is_planned(self) -> 'None':
        pv2 = segment('PV2', {1: 'WARD3^302^B'})

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        # The pending location joins the PV1 one with the planned status -
        # the PV1 location entry carries no status of its own.
        locations = encounter['location']

        planned = []

        for item in locations:
            if 'status' in item:
                planned.append(item)

        assert len(planned) == 1

        first_planned = planned[0]
        assert first_planned['status'] == 'planned'

        # The referenced Location spells out the pending bed.
        beds = []

        for item in resources_of_type(bundle, 'Location'):
            if item['name'] == 'B':
                beds.append(item)

        assert len(beds) == 1

# ################################################################################################################################

    def test_planned_start_and_end_dates(self) -> 'None':
        pv2 = segment('PV2', {8: '20260316080000', 9: '20260320120000'})

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        extensions = encounter['extension']

        assert {
            'url': 'http://hl7.org/fhir/5.0/StructureDefinition/extension-Encounter.plannedStartDate',
            'valueDateTime': '2026-03-16T08:00:00+00:00',
        } in extensions

        assert {
            'url': 'http://hl7.org/fhir/5.0/StructureDefinition/extension-Encounter.plannedEndDate',
            'valueDateTime': '2026-03-20T12:00:00+00:00',
        } in extensions

# ################################################################################################################################

    def test_estimated_and_actual_lengths_of_stay(self) -> 'None':
        pv2 = segment('PV2', {10: '4', 11: '5'})

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        # The estimate has no FHIR element and keeps its own extension ..
        assert {
            'url': 'urn:zato:hl7v2:extension/encounter/estimated-length-of-stay',
            'valueDuration': {'value': 4, 'unit': 'd', 'system': 'http://unitsofmeasure.org', 'code': 'd'},
        } in encounter['extension']

        # .. while the actual stay is the encounter's length.
        assert encounter['length'] == {'value': 5, 'unit': 'd', 'system': 'http://unitsofmeasure.org', 'code': 'd'}

# ################################################################################################################################

    def test_non_numeric_lengths_are_preserved(self) -> 'None':
        pv2 = segment('PV2', {10: 'about a week'})

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        assert 'length' not in encounter

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/PV2-10',
            'valueString': 'about a week',
        } in encounter['extension']

# ################################################################################################################################

    def test_referral_source_is_a_referrer_participant(self) -> 'None':
        pv2 = segment('PV2', {13: '4001^Jones^Anna'})

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        participants = encounter['participant']
        assert len(participants) == 1

        participant = participants[0]

        assert participant['type'] == [{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/v3-ParticipationType',
                'code': 'REF',
            }],
        }]

        practitioner = one_resource(bundle, 'Practitioner')
        assert practitioner['name'] == [{'family': 'Jones', 'given': ['Anna']}]

# ################################################################################################################################

    def test_priority_and_mode_of_arrival(self) -> 'None':
        pv2 = segment('PV2', {25: 'UR^Urgent^L', 38: 'AMB^Ambulance^L'})

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        assert encounter['priority'] == {
            'coding': [{'code': 'UR', 'display': 'Urgent'}],
            'text': 'Urgent',
        }

        assert {
            'url': 'http://hl7.org/fhir/StructureDefinition/encounter-modeOfArrival',
            'valueCodeableConcept': {
                'coding': [{'code': 'AMB', 'display': 'Ambulance'}],
                'text': 'Ambulance',
            },
        } in encounter['extension']

# ################################################################################################################################
# ################################################################################################################################
