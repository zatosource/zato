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
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

Financial_Class = 'http://terminology.hl7.org/CodeSystem/v2-0064'
Financial_Class_Extension = 'urn:zato:hl7v2:extension/financial-class'

# ################################################################################################################################
# ################################################################################################################################

class TestSubscriber:
    """ IN1-16 to IN1-19 and IN1-43 describe the insured, who is the subscriber.
    """

    def test_insured_other_than_the_patient_is_a_related_person(self) -> 'None':
        in1 = segment('IN1', {
            1: '1', 2: 'PLAN01', 3: 'INS001', 4: 'Acme Insurance', 16: 'Smith^Jane', 17: 'SPO', 18: '19800315',
            19: '123 Main St^^Springfield^IL^62701', 36: 'POL-777', 43: 'F',
        })

        bundle = convert(MSH, PID, in1)

        coverage = one_resource(bundle, 'Coverage')
        subscriber = one_resource(bundle, 'RelatedPerson')

        assert subscriber['name'] == [{'family': 'Smith', 'given': ['Jane']}]
        assert subscriber['birthDate'] == '1980-03-15'
        assert subscriber['gender'] == 'female'
        assert subscriber['address'] == [{
            'line': ['123 Main St'], 'city': 'Springfield', 'state': 'IL', 'postalCode': '62701',
        }]
        assert subscriber['relationship'] == [{
            'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0063', 'code': 'SPO'}],
        }]

        patient = one_resource(bundle, 'Patient')

        subscriber_url = None
        patient_url = None

        for entry in bundle.to_dict()['entry']:
            if entry['resource'] == subscriber:
                subscriber_url = entry['fullUrl']
            if entry['resource'] == patient:
                patient_url = entry['fullUrl']

        assert subscriber['patient'] == {'reference': patient_url}
        assert coverage['subscriber'] == {'reference': subscriber_url}
        assert coverage['relationship']['coding'][0]['code'] == 'spouse'

        assert 'extension' not in coverage
        assert 'extension' not in subscriber
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_patient_is_their_own_subscriber(self) -> 'None':
        in1 = segment('IN1', {
            1: '1', 2: 'PLAN01', 3: 'INS001', 4: 'Acme Insurance', 16: 'Smith^John', 17: 'SEL', 18: '19700101',
            19: '1 Elm St^^Springfield^IL^62701', 43: 'M',
        })

        bundle = convert(MSH, PID, in1)
        coverage = one_resource(bundle, 'Coverage')

        patient = one_resource(bundle, 'Patient')
        patient_url = None

        for entry in bundle.to_dict()['entry']:
            if entry['resource'] == patient:
                patient_url = entry['fullUrl']

        assert coverage['subscriber'] == {'reference': patient_url}

        # The insured's details repeat the patient's, so there is no one else to build.
        assert resources_of_type(bundle, 'RelatedPerson') == []
        assert 'extension' not in coverage
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestFinancialClass:
    """ PV1-20 is the visit's financial class, which types the Coverages of the message.
    """

    def test_financial_class_is_the_coverage_type(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 20: 'PPO'})
        in1 = segment('IN1', {1: '1', 2: 'PLAN01', 3: 'INS001', 4: 'Acme Insurance', 17: 'SEL'})

        bundle = convert(MSH, PID, pv1, in1)
        coverage = one_resource(bundle, 'Coverage')

        assert coverage['type'] == {'coding': [{'system': Financial_Class, 'code': 'PPO'}]}

        encounter = one_resource(bundle, 'Encounter')
        assert 'extension' not in encounter
        assert 'extension' not in coverage

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_plan_type_keeps_the_type_and_the_class_becomes_an_extension(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 20: 'PPO'})
        in1 = segment('IN1', {1: '1', 2: 'PLAN01', 3: 'INS001', 4: 'Acme Insurance', 15: 'HMO^Health Maintenance^HL70086', 17: 'SEL'})

        bundle = convert(MSH, PID, pv1, in1)
        coverage = one_resource(bundle, 'Coverage')

        assert coverage['type']['coding'][0]['code'] == 'HMO'
        assert coverage['extension'] == [{
            'url': Financial_Class_Extension,
            'valueCodeableConcept': {'coding': [{'system': Financial_Class, 'code': 'PPO'}]},
        }]

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_without_coverage_the_class_stays_with_the_encounter(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 20: 'PPO'})

        bundle = convert(MSH, PID, pv1)
        encounter = one_resource(bundle, 'Encounter')

        assert encounter['extension'] == [{
            'url': Financial_Class_Extension,
            'valueCodeableConcept': {'coding': [{'system': Financial_Class, 'code': 'PPO'}]},
        }]

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
