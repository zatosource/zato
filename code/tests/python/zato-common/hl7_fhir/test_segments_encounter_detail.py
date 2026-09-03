# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

MSH = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q|||M'

Unmapped = 'urn:zato:hl7v2:extension/unmapped'

# ################################################################################################################################
# ################################################################################################################################

def _location_named(bundle:'object', name:'str') -> 'dict':
    """ The only Location with a given name in a bundle.
    """
    matches = []

    for location in resources_of_type(bundle, 'Location'):
        if location['name'] == name:
            matches.append(location)

    assert len(matches) == 1, f'Expected one Location named {name}, found {len(matches)}'

    out = matches[0]
    return out

# ################################################################################################################################

def _full_url_of(bundle:'object', resource:'dict') -> 'str':
    """ The bundle-internal URL a resource dict was entered under.
    """
    for entry in bundle.to_dict()['entry']:
        if entry['resource'] == resource:
            return entry['fullUrl']

    raise AssertionError('Resource not found in bundle')

# ################################################################################################################################
# ################################################################################################################################

class TestPV1Hospitalization:
    """ The hospitalization details of PV1 end up under Encounter.hospitalization.
    """

    def test_coded_hospitalization_fields(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 13: 'R', 15: 'A2~B6', 16: 'VIP', 18: 'INP', 38: 'LOWSALT'})

        bundle = convert(MSH, PID, pv1)
        encounter = one_resource(bundle, 'Encounter')

        hospitalization = encounter['hospitalization']

        # The re-admission indicator keeps its HL7 table ..
        assert hospitalization['reAdmission'] == {
            'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0092', 'code': 'R'}],
        }

        # .. an ambulatory status with a FHIR counterpart translates, one without keeps its table ..
        assert hospitalization['specialArrangement'] == [
            {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/encounter-special-arrangements', 'code': 'wheel'}]},
            {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0009', 'code': 'B6'}]},
        ]

        # .. the VIP indicator is a special courtesy ..
        assert hospitalization['specialCourtesy'] == [
            {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v3-EncounterSpecialCourtesy', 'code': 'VIP'}]},
        ]

        # .. the diet type a diet preference ..
        assert hospitalization['dietPreference'] == [{'coding': [{'code': 'LOWSALT'}], 'text': 'LOWSALT'}]

        # .. and the patient type is the encounter type.
        assert encounter['type'] == [{'coding': [{'code': 'INP'}], 'text': 'INP'}]

        assert 'extension' not in encounter
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_discharge_location(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 37: 'HOME'})

        bundle = convert(MSH, PID, pv1)
        encounter = one_resource(bundle, 'Encounter')

        destination = _location_named(bundle, 'HOME')
        destination_url = _full_url_of(bundle, destination)

        assert encounter['hospitalization']['destination'] == {'reference': destination_url}

        assert 'extension' not in encounter
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestPV1Locations:
    """ The bed status and the pending and prior locations of PV1.
    """

    def test_bed_status_is_the_beds_operational_status(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 3: 'WARD1^101^A^GENHOSP', 40: 'O'})

        bundle = convert(MSH, PID, pv1)

        bed = _location_named(bundle, 'A')
        assert bed['operationalStatus'] == {'system': 'http://terminology.hl7.org/CodeSystem/v2-0116', 'code': 'O'}

        # The status belongs to the bed alone.
        room = _location_named(bundle, '101')
        assert 'operationalStatus' not in room

        encounter = one_resource(bundle, 'Encounter')
        assert 'extension' not in encounter
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_pending_and_prior_temporary_locations(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 3: 'WARD1^101^A^GENHOSP', 42: 'WARD2^202^B', 43: 'ICU^1^C'})

        bundle = convert(MSH, PID, pv1)
        encounter = one_resource(bundle, 'Encounter')

        current, pending, prior = encounter['location']

        # The assigned location has no status of its own, the pending one is planned
        # and the one the patient left is completed.
        assert 'status' not in current
        assert pending['status'] == 'planned'
        assert prior['status'] == 'completed'

        pending_bed = _location_named(bundle, 'B')
        prior_bed = _location_named(bundle, 'C')

        assert pending['location'] == {'reference': _full_url_of(bundle, pending_bed)}
        assert prior['location'] == {'reference': _full_url_of(bundle, prior_bed)}

        assert 'extension' not in encounter
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
