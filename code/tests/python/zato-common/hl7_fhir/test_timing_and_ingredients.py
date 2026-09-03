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
MSH_RDE = 'MSH|^~\\&|EHR|EHRFAC|PHARM|PHARMFAC|20240517143055||RDE^O11|MSG00004|P|2.5'
MSH_VXU = 'MSH|^~\\&|EHR|EHRFAC|IIS|IISFAC|20240517143055||VXU^V04|MSG00006|P|2.5.1'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

ORC = 'ORC|NW|ORD-1^EHR'
OBR = 'OBR|1|ORD-1^EHR||24331-1^Lipid panel^LN'

Unmapped = 'urn:zato:hl7v2:extension/unmapped'

# ################################################################################################################################
# ################################################################################################################################

def _service_request_for(tq1:'str') -> 'tuple':
    """ Converts one order with the given TQ1 and returns the ServiceRequest with the bundle's warnings.
    """
    bundle = convert(MSH_ORM, PID, ORC, OBR, tq1)
    service_request = one_resource(bundle, 'ServiceRequest')

    return service_request, get_conversion_warnings(bundle)

# ################################################################################################################################
# ################################################################################################################################

class TestTQ1Timing:
    """ TQ1 becomes the occurrence of a ServiceRequest - a bare start and end as a period, anything richer as a Timing.
    """

    def test_full_timing(self) -> 'None':
        tq1 = segment('TQ1', {
            1: '1', 2: '2^TAB', 3: 'BID^Twice a day^HL70335', 4: '0800~2000', 5: '30^min&minute&UCUM',
            7: '20240517', 8: '20240524', 9: 'R^Routine^HL70485', 11: 'Take with food',
        })
        service_request, warnings = _service_request_for(tq1)

        assert service_request['occurrenceTiming'] == {
            'repeat': {
                'boundsPeriod': {'start': '2024-05-17', 'end': '2024-05-24'},
                'frequency': 2,
                'period': 1,
                'periodUnit': 'd',
                'timeOfDay': ['08:00:00', '20:00:00'],
                'offset': 30,
            },
            'code': {'text': 'Take with food'},
        }

        assert service_request['priority'] == 'routine'
        assert service_request['quantityQuantity'] == {'value': 2.0, 'unit': 'TAB'}

        assert 'extension' not in service_request
        assert warnings == []

# ################################################################################################################################

    def test_bounds_alone_are_a_period(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 7: '20240517', 8: '20240524'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['occurrencePeriod'] == {'start': '2024-05-17', 'end': '2024-05-24'}
        assert 'occurrenceTiming' not in service_request
        assert warnings == []

# ################################################################################################################################

    def test_start_alone_is_a_datetime(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 7: '20240517080000'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['occurrenceDateTime'] == '2024-05-17T08:00:00+00:00'
        assert warnings == []

# ################################################################################################################################

    def test_interval_pattern_with_count(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 3: 'Q6H', 14: '4'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['occurrenceTiming'] == {
            'repeat': {'frequency': 1, 'period': 6, 'periodUnit': 'h', 'count': 4},
        }
        assert warnings == []

# ################################################################################################################################

    def test_service_duration_bounds_the_timing(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 3: 'QD', 6: '7^d&day&UCUM'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['occurrenceTiming'] == {
            'repeat': {
                'boundsDuration': {'value': 7.0, 'unit': 'd', 'system': 'http://unitsofmeasure.org', 'code': 'd'},
                'frequency': 1,
                'period': 1,
                'periodUnit': 'd',
            },
        }
        assert warnings == []

# ################################################################################################################################

    def test_condition_is_the_as_needed_reason(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 3: 'PRN', 10: 'for pain'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['asNeededCodeableConcept'] == {'text': 'for pain'}
        assert 'occurrenceTiming' not in service_request
        assert warnings == []

# ################################################################################################################################

    def test_once_with_stat_priority(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 3: 'ONCE', 9: 'S'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['occurrenceTiming'] == {'repeat': {'count': 1}}
        assert service_request['priority'] == 'stat'
        assert warnings == []

# ################################################################################################################################

    def test_unknown_pattern_is_preserved(self) -> 'None':
        tq1 = segment('TQ1', {1: '1', 3: 'QXYZ'})
        service_request, warnings = _service_request_for(tq1)

        assert service_request['extension'] == [{'url': f'{Unmapped}/TQ1-3', 'valueString': 'QXYZ'}]
        assert warnings == []

# ################################################################################################################################
# ################################################################################################################################

class TestTQ1Dosage:
    """ In pharmacy messages TQ1 is the timing of the dosage instruction.
    """

    def test_dosage_timing_and_text(self) -> 'None':
        rxe = 'RXE||AMOX500^Amoxicillin 500 mg^L|500||mg'
        tq1 = segment('TQ1', {1: '1', 3: 'Q8H^Every 8 hours^HL70335', 7: '20240517', 9: 'S', 11: 'With water'})

        bundle = convert(MSH_RDE, PID, ORC, rxe, tq1)
        request = one_resource(bundle, 'MedicationRequest')

        dosage = request['dosageInstruction'][0]

        assert dosage['timing'] == {
            'repeat': {'boundsPeriod': {'start': '2024-05-17'}, 'frequency': 1, 'period': 8, 'periodUnit': 'h'},
        }
        assert dosage['text'] == 'With water'
        assert request['priority'] == 'stat'

        assert 'extension' not in request
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestRXCIngredients:
    """ RXC components make the compound Medication a pharmacy order is about.
    """

    def test_components_become_ingredients(self) -> 'None':
        rxe = 'RXE||TPN001^TPN Solution^L|1000||mL'
        base = segment('RXC', {1: 'B', 2: 'DEXTROSE^Dextrose 10%^L', 3: '500', 4: 'mL'})
        additive = segment('RXC', {1: 'A', 2: 'AMINO^Amino Acids^L', 3: '50', 4: 'g', 8: '1000', 9: 'mL'})

        bundle = convert(MSH_RDE, PID, ORC, rxe, base, additive)

        request = one_resource(bundle, 'MedicationRequest')
        medication = one_resource(bundle, 'Medication')

        # The request points at the compound instead of naming a code ..
        assert 'medicationCodeableConcept' not in request

        medication_url = None
        for entry in bundle.to_dict()['entry']:
            if entry['resource'] == medication:
                medication_url = entry['fullUrl']

        assert request['medicationReference'] == {'reference': medication_url}

        # .. the compound keeps the order's code ..
        assert medication['code']['coding'][0]['code'] == 'TPN001'

        # .. and each component is an ingredient, the base inactive, the additive active,
        # .. with the amount per unit of the compound or per the volume the RXC names.
        first, second = medication['ingredient']

        assert first['itemCodeableConcept']['coding'][0]['code'] == 'DEXTROSE'
        assert first['isActive'] is False
        assert first['strength'] == {'numerator': {'value': 500.0, 'unit': 'mL'}, 'denominator': {'value': 1}}

        assert second['itemCodeableConcept']['coding'][0]['code'] == 'AMINO'
        assert second['isActive'] is True
        assert second['strength'] == {
            'numerator': {'value': 50.0, 'unit': 'g'},
            'denominator': {'value': 1000.0, 'unit': 'mL'},
        }

        assert 'extension' not in medication
        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_components_of_a_vaccine_stay_on_the_immunization(self) -> 'None':
        rxa = segment('RXA', {1: '0', 2: '1', 3: '20240517', 5: '08^Hep B^CVX', 6: '0.5', 7: 'mL^^UCUM'})
        rxc = segment('RXC', {1: 'A', 2: 'HEPB^Hep B antigen^L', 3: '10', 4: 'ug'})

        bundle = convert(MSH_VXU, PID, 'ORC|RE', rxa, rxc)
        immunization = one_resource(bundle, 'Immunization')

        assert resources_of_type(bundle, 'Medication') == []
        assert resources_of_type(bundle, 'Basic') == []

        assert {'url': f'{Unmapped}/RXC-2', 'valueString': 'HEPB^Hep B antigen^L'} in immunization['extension']
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
