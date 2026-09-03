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

MSH_ORM = 'MSH|^~\\&|EHR|EHRFAC|LAB|LABFAC|20240517143055||ORM^O01|MSG00003|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

Participant_Type = 'http://terminology.hl7.org/CodeSystem/provenance-participant-type'

# ################################################################################################################################
# ################################################################################################################################

def _practitioner_named(bundle:'object', family:'str') -> 'dict':
    """ The only Practitioner with a given family name in a bundle.
    """
    matches = []

    for practitioner in resources_of_type(bundle, 'Practitioner'):
        if practitioner['name'][0]['family'] == family:
            matches.append(practitioner)

    assert len(matches) == 1, f'Expected one Practitioner named {family}, found {len(matches)}'

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

class TestOrderProvenance:
    """ ORC-10, ORC-11 and ORC-13 say who entered and verified an order and where, which is its Provenance.
    """

    def test_enterer_verifier_and_location(self) -> 'None':
        orc = segment('ORC', {
            1: 'NW', 2: 'ORD-1^EHR', 9: '20240517090000', 10: '2001^Jones^Mary', 11: '3001^Brown^Alan', 13: 'WARD1^101',
        })
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN'})

        bundle = convert(MSH_ORM, PID, orc, obr)

        service_request = one_resource(bundle, 'ServiceRequest')
        provenance = one_resource(bundle, 'Provenance')

        # The Provenance is about the ServiceRequest, recorded when the ORC was ..
        assert provenance['target'] == [{'reference': _full_url_of(bundle, service_request)}]
        assert provenance['recorded'] == '2024-05-17T09:00:00+00:00'

        # .. with the enterer and the verifier as its agents ..
        enterer = _practitioner_named(bundle, 'Jones')
        verifier = _practitioner_named(bundle, 'Brown')

        assert provenance['agent'] == [
            {
                'type': {'coding': [{'system': Participant_Type, 'code': 'enterer'}]},
                'who': {'reference': _full_url_of(bundle, enterer)},
            },
            {
                'type': {'coding': [{'system': Participant_Type, 'code': 'verifier'}]},
                'who': {'reference': _full_url_of(bundle, verifier)},
            },
        ]

        # .. and the enterer's location as where it happened.
        room = None
        for location in resources_of_type(bundle, 'Location'):
            if location['name'] == '101':
                room = location

        assert room
        assert provenance['location'] == {'reference': _full_url_of(bundle, room)}

        assert 'extension' not in service_request
        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_no_provenance_fields_means_no_provenance(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-1^EHR', 12: '1234^Welby^Marcus'})
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN'})

        bundle = convert(MSH_ORM, PID, orc, obr)

        assert resources_of_type(bundle, 'Provenance') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_recorded_time_comes_from_the_message_without_orc_9(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-1^EHR', 10: '2001^Jones^Mary'})
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN'})

        bundle = convert(MSH_ORM, PID, orc, obr)
        provenance = one_resource(bundle, 'Provenance')

        assert provenance['recorded'] == '2024-05-17T14:30:55+00:00'
        assert len(provenance['agent']) == 1

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
