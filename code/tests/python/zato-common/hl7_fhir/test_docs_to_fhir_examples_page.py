# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode

# Zato
from zato.hl7.mappings import get_conversion_warnings
from zato.hl7v2 import parse_hl7

# Local
from conftest import one_resource, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The messages the docs/dev/healthcare/hl7/to-fhir/examples page shows, field for field.

PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John^A||19800115|M'
PID_FULL = 'PID|1||12345^^^GENHOSP^MR||Smith^John^A||19800115|M|||123 Main St^^Boston^MA^02101||^PRN^PH^^1^617^5550123'
Doctor = '1234^Jones^Maria^^^^MD'

Unmapped = 'urn:zato:hl7v2:extension/unmapped'

# ################################################################################################################################
# ################################################################################################################################

def convert(*segments:'str') -> 'any_':
    """ Unlike the conftest helper, this one validates the message, the page's messages must be valid HL7 v2.
    """
    joined = '\r'.join(segments)
    raw = joined + '\r'
    msg = parse_hl7(raw)

    out = msg.to_fhir()
    return out

# ################################################################################################################################

def _full_url_of(bundle:'any_', resource:'anydict') -> 'str':
    """ The bundle-internal URL a resource dict was entered under.
    """
    for entry in bundle.to_dict()['entry']:
        if entry['resource'] == resource:
            return entry['fullUrl']

    raise AssertionError('Resource not found in bundle')

# ################################################################################################################################

def _assert_clean(bundle:'any_') -> 'None':
    """ The page shows no preserved-as-is data, so none may appear.
    """
    assert get_conversion_warnings(bundle) == []
    assert resources_of_type(bundle, 'Basic') == []

    for entry in bundle.to_dict()['entry']:
        resource = entry['resource']
        if 'extension' in resource:
            for extension in resource['extension']:
                assert not extension['url'].startswith(Unmapped), extension

# ################################################################################################################################
# ################################################################################################################################

class TestAdmissionsDischargesTransfers:

    def test_adt_a01_admission(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|ADT|GENHOSP|EHR|GENHOSP|20260315101112||ADT^A01^ADT_A01|MSG0001|P|2.5.1',
            'EVN|A01|20260315101000',
            PID_FULL,
            'NK1|1|Smith^Jane|SPO^Spouse^HL70063|||^PRN^PH^^1^617^5550124',
            segment('PV1', {1: '1', 2: 'I', 3: 'WEST^201^B^GENHOSP', 7: Doctor, 10: 'MED', 14: '7', 17: Doctor, 18: 'INP',
                19: 'V2026001^^^GENHOSP', 44: '20260315101000'}),
            'DG1|1||I10^Essential hypertension^I10|||A',
        )

        patient = one_resource(bundle, 'Patient')

        assert patient['identifier'][0]['value'] == '12345'
        assert patient['identifier'][0]['type']['coding'][0]['code'] == 'MR'
        assert patient['name'] == [{'family': 'Smith', 'given': ['John', 'A']}]
        assert patient['birthDate'] == '1980-01-15'
        assert patient['gender'] == 'male'
        assert patient['address'][0]['city'] == 'Boston'
        assert patient['telecom'] == [{'value': '+1 617 5550123', 'use': 'home', 'system': 'phone'}]

        encounter = one_resource(bundle, 'Encounter')
        assert encounter['status'] == 'in-progress'
        assert encounter['type'][0]['coding'][0]['code'] == 'INP'
        assert encounter['hospitalization']['admitSource']['coding'][0]['code'] == '7'
        assert len(encounter['participant']) == 2

        _assert_clean(bundle)

# ################################################################################################################################

    def test_adt_a03_discharge(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|ADT|GENHOSP|EHR|GENHOSP|20260318150000||ADT^A03^ADT_A03|MSG0002|P|2.5.1',
            'EVN|A03|20260318150000',
            PID,
            segment('PV1', {1: '1', 2: 'I', 3: 'WEST^201^B^GENHOSP', 7: Doctor, 10: 'MED', 19: 'V2026001^^^GENHOSP', 36: '01',
                37: 'HOME', 44: '20260315101000', 45: '20260318143000'}),
        )

        encounter = one_resource(bundle, 'Encounter')

        assert encounter['status'] == 'finished'
        assert encounter['period'] == {'start': '2026-03-15T10:10:00+00:00', 'end': '2026-03-18T14:30:00+00:00'}

        hospitalization = encounter['hospitalization']
        assert hospitalization['dischargeDisposition']['coding'][0]['code'] == '01'

        home = None
        for location in resources_of_type(bundle, 'Location'):
            if location['name'] == 'HOME':
                home = location

        assert home
        assert hospitalization['destination'] == {'reference': _full_url_of(bundle, home)}

        _assert_clean(bundle)

# ################################################################################################################################

    def test_adt_a02_transfer(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|ADT|GENHOSP|EHR|GENHOSP|20260316090000||ADT^A02^ADT_A02|MSG0003|P|2.5.1',
            'EVN|A02|20260316090000',
            PID,
            segment('PV1', {1: '1', 2: 'I', 3: 'ICU^3^A^GENHOSP', 6: 'WEST^201^B^GENHOSP', 7: Doctor, 10: 'MED',
                19: 'V2026001^^^GENHOSP'}),
        )

        encounter = one_resource(bundle, 'Encounter')
        current, prior = encounter['location']

        assert 'status' not in current
        assert prior['status'] == 'completed'

        names = []
        for location in resources_of_type(bundle, 'Location'):
            names.append(location['name'])

        assert names == ['GENHOSP', 'ICU', '3', 'A', 'WEST', '201', 'B']

        _assert_clean(bundle)

# ################################################################################################################################

    def test_adt_a08_update_with_insurance(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|ADT|GENHOSP|EHR|GENHOSP|20260316120000||ADT^A08^ADT_A01|MSG0004|P|2.5.1',
            'EVN|A08|20260316120000',
            PID_FULL,
            segment('PV1', {1: '1', 2: 'I', 3: 'WEST^201^B^GENHOSP', 7: Doctor, 10: 'MED', 19: 'V2026001^^^GENHOSP', 20: 'COM'}),
            segment('IN1', {1: '1', 2: 'PPO01^Preferred Plan', 3: 'BCBS001^^^NAIC', 4: 'Blue Cross Blue Shield',
                5: '100 Insurance Way^^Boston^MA^02110', 8: 'GRP2026', 9: 'Acme Corp', 12: '20260101', 13: '20261231',
                16: 'Smith^Jane', 17: 'SPO', 18: '19820420', 19: '123 Main St^^Boston^MA^02101', 36: 'POL998877', 43: 'F'}),
        )

        coverage = one_resource(bundle, 'Coverage')
        subscriber = one_resource(bundle, 'RelatedPerson')

        assert coverage['type']['coding'][0] == {'system': 'http://terminology.hl7.org/CodeSystem/v2-0064', 'code': 'COM'}
        assert coverage['class'][0]['value'] == 'PPO01'
        assert coverage['class'][1] == {
            'type': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/coverage-class', 'code': 'group'}]},
            'value': 'GRP2026',
            'name': 'Acme Corp',
        }
        assert coverage['period'] == {'start': '2026-01-01', 'end': '2026-12-31'}
        assert coverage['relationship']['coding'][0]['code'] == 'spouse'
        assert coverage['subscriberId'] == 'POL998877'
        assert coverage['subscriber'] == {'reference': _full_url_of(bundle, subscriber)}

        assert subscriber['name'] == [{'family': 'Smith', 'given': ['Jane']}]
        assert subscriber['birthDate'] == '1982-04-20'
        assert subscriber['gender'] == 'female'

        _assert_clean(bundle)

# ################################################################################################################################

    def test_adt_a40_merge(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|ADT|GENHOSP|EHR|GENHOSP|20260317080000||ADT^A40^ADT_A39|MSG0005|P|2.5.1',
            'EVN|A40|20260317080000',
            PID,
            'MRG|67890^^^GENHOSP^MR',
        )

        surviving, merged = resources_of_type(bundle, 'Patient')

        assert surviving['link'] == [{'other': {'reference': _full_url_of(bundle, merged)}, 'type': 'replaces'}]
        assert merged['active'] is False
        assert merged['identifier'][0]['value'] == '67890'
        assert 'name' not in merged

        _assert_clean(bundle)

# ################################################################################################################################
# ################################################################################################################################

class TestResultsAndOrders:

    def test_oru_r01_lipid_panel(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|LAB|GENHOSP|EHR|GENHOSP|20260315143000||ORU^R01^ORU_R01|MSG0006|P|2.5.1',
            PID,
            'PV1|1|O|CLINIC^^^GENHOSP',
            segment('ORC', {1: 'RE', 2: 'ORD2001^EHR', 3: 'LAB3001^LAB', 12: Doctor}),
            segment('OBR', {1: '1', 2: 'ORD2001^EHR', 3: 'LAB3001^LAB', 4: '24331-1^Lipid panel^LN', 7: '20260315080000',
                16: Doctor, 22: '20260315140000', 25: 'F'}),
            'OBX|1|NM|2093-3^Cholesterol total^LN||210|mg/dL^^UCUM|<200|H|||F|||20260315080000',
            'OBX|2|NM|2085-9^HDL cholesterol^LN||45|mg/dL^^UCUM|>40|N|||F|||20260315080000',
            'OBX|3|NM|2089-1^LDL cholesterol^LN||140|mg/dL^^UCUM|<100|H|||F|||20260315080000',
            segment('SPM', {1: '1', 2: 'SPM7001^LAB', 4: '119297000^Blood specimen^SCT', 17: '20260315080000', 18: '20260315081500'}),
        )

        observations = resources_of_type(bundle, 'Observation')
        assert len(observations) == 3

        first = observations[0]
        assert first['code']['coding'][0]['code'] == '2093-3'
        assert first['valueQuantity'] == {'value': 210.0, 'system': 'http://unitsofmeasure.org', 'code': 'mg/dL', 'unit': 'mg/dL'}
        assert first['referenceRange'] == [{'text': '<200'}]
        assert first['interpretation'][0]['coding'][0]['code'] == 'H'
        assert first['status'] == 'final'
        assert first['effectiveDateTime'] == '2026-03-15T08:00:00+00:00'

        report = one_resource(bundle, 'DiagnosticReport')
        specimen = one_resource(bundle, 'Specimen')

        assert len(report['result']) == 3
        assert report['specimen'] == [{'reference': _full_url_of(bundle, specimen)}]
        assert report['issued'] == '2026-03-15T14:00:00+00:00'

        assert specimen['type']['coding'][0]['system'] == 'http://snomed.info/sct'
        assert specimen['receivedTime'] == '2026-03-15T08:15:00+00:00'

        _assert_clean(bundle)

# ################################################################################################################################

    def test_oru_r01_pdf_report(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|RAD|GENHOSP|EHR|GENHOSP|20260315160000||ORU^R01^ORU_R01|MSG0007|P|2.5.1',
            PID,
            'ORC|RE|ORD2002^EHR|RAD4001^RAD',
            segment('OBR', {1: '1', 2: 'ORD2002^EHR', 3: 'RAD4001^RAD', 4: '36643-5^Chest X-ray 2 views^LN', 7: '20260315150000',
                22: '20260315155000', 25: 'F'}),
            segment('OBX', {1: '1', 2: 'ED', 3: 'PDF^Radiology report^L', 5: '^application^pdf^Base64^JVBERi0xLjQKJcOkw7zDtsOfCg==',
                11: 'F', 14: '20260315155500', 15: 'RAD01^Radiology Department', 16: '5678^Adams^Robert^^^^MD'}),
        )

        report = one_resource(bundle, 'DiagnosticReport')

        assert report['presentedForm'] == [{
            'contentType': 'application/pdf',
            'data': 'JVBERi0xLjQKJcOkw7zDtsOfCg==',
            'title': 'Radiology report',
            'creation': '2026-03-15T15:55:00+00:00',
        }]
        assert len(report['performer']) == 2

        practitioner = one_resource(bundle, 'Practitioner')
        assert practitioner['name'][0]['family'] == 'Adams'

        _assert_clean(bundle)

# ################################################################################################################################

    def test_orm_o01_order_with_timing(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|EHR|GENHOSP|LAB|GENHOSP|20260315090000||ORM^O01^ORM_O01|MSG0008|P|2.5.1',
            PID,
            'PV1|1|I|WEST^201^B^GENHOSP',
            segment('ORC', {1: 'NW', 2: 'ORD2003^EHR', 9: '20260315090000', 10: '2001^Davis^Karen', 11: '3001^Miller^Thomas',
                12: Doctor, 13: 'WEST^201', 14: '^WPN^PH^^1^617^5550200'}),
            segment('OBR', {1: '1', 2: 'ORD2003^EHR', 4: '1558-6^Fasting glucose^LN', 16: Doctor}),
            segment('TQ1', {1: '1', 3: 'QD^Once a day^HL70335', 4: '0700', 7: '20260316', 8: '20260318', 9: 'R^Routine^HL70485',
                11: 'Fasting for 8 hours before each draw'}),
        )

        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['authoredOn'] == '2026-03-15T09:00:00+00:00'
        assert service_request['priority'] == 'routine'
        assert service_request['occurrenceTiming'] == {
            'repeat': {
                'boundsPeriod': {'start': '2026-03-16', 'end': '2026-03-18'},
                'frequency': 1,
                'period': 1,
                'periodUnit': 'd',
                'timeOfDay': ['07:00:00'],
            },
            'code': {'text': 'Fasting for 8 hours before each draw'},
        }

        provenance = one_resource(bundle, 'Provenance')
        assert provenance['target'] == [{'reference': _full_url_of(bundle, service_request)}]
        assert len(provenance['agent']) == 2
        assert 'location' in provenance

        _assert_clean(bundle)

# ################################################################################################################################

    def test_oml_o21_lab_order(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|EHR|GENHOSP|LAB|GENHOSP|20260315093000||OML^O21^OML_O21|MSG0009|P|2.5.1',
            PID,
            segment('ORC', {1: 'NW', 2: 'ORD2004^EHR', 9: '20260315093000', 12: Doctor}),
            segment('OBR', {1: '1', 2: 'ORD2004^EHR', 4: '58410-2^CBC panel^LN', 16: Doctor}),
            segment('SPM', {1: '1', 2: 'SPM7002^EHR', 4: 'BLD^Blood^HL70487', 8: 'ARM^Arm^HL70163', 17: '20260315093000'}),
        )

        specimen = one_resource(bundle, 'Specimen')

        assert specimen['identifier'] == [{'value': 'SPM7002'}]
        assert specimen['type']['coding'][0]['code'] == 'BLD'
        assert specimen['collection']['bodySite']['coding'][0]['code'] == 'ARM'
        assert specimen['collection']['collectedDateTime'] == '2026-03-15T09:30:00+00:00'

        service_request = one_resource(bundle, 'ServiceRequest')
        assert service_request['authoredOn'] == '2026-03-15T09:30:00+00:00'
        assert 'requester' in service_request

        _assert_clean(bundle)

# ################################################################################################################################
# ################################################################################################################################

class TestDocumentsAppointmentsImmunizations:

    def test_mdm_t02_document(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|EHR|GENHOSP|HIM|GENHOSP|20260318160000||MDM^T02^MDM_T02|MSG0010|P|2.5.1',
            'EVN|T02|20260318160000',
            PID,
            segment('PV1', {1: '1', 2: 'I', 3: 'WEST^201^B^GENHOSP', 19: 'V2026001^^^GENHOSP'}),
            segment('TXA', {1: '1', 2: 'DS^Discharge summary^HL70270', 3: 'TX', 4: '20260318153000', 5: Doctor, 12: 'DOC5001^EHR',
                16: 'discharge-summary.txt', 17: 'AU', 19: 'AV'}),
            'OBX|1|TX|18842-5^Discharge summary^LN||Admitted with chest pain, ruled out for myocardial infarction.||||||F',
            'OBX|2|TX|18842-5^Discharge summary^LN||Discharged home in stable condition with follow-up in two weeks.||||||F',
        )

        document = one_resource(bundle, 'DocumentReference')

        assert document['status'] == 'current'
        assert document['docStatus'] == 'final'
        assert document['type']['coding'][0]['code'] == 'DS'
        assert document['date'] == '2026-03-18T15:30:00+00:00'
        assert document['masterIdentifier'] == {'value': 'DOC5001', 'system': 'urn:zato:hl7v2:authority:EHR'}

        attachment = document['content'][0]['attachment']

        assert attachment['contentType'] == 'text/plain'
        assert attachment['title'] == 'discharge-summary.txt'
        assert b64decode(attachment['data']).decode() == \
            'Admitted with chest pain, ruled out for myocardial infarction.\n' + \
            'Discharged home in stable condition with follow-up in two weeks.'

        _assert_clean(bundle)

# ################################################################################################################################

    def test_siu_s12_appointment(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|SCHED|GENHOSP|EHR|GENHOSP|20260320100000||SIU^S12^SIU_S12|MSG0011|P|2.5.1',
            segment('SCH', {1: 'APT6001^SCHED', 6: 'FOLLOWUP^Follow-up visit^L', 7: 'FOLLOWUP^Follow-up visit^L',
                8: 'ROUTINE^Routine^HL70276', 9: '30', 10: 'min^minute^UCUM', 11: '^^^20260401140000^20260401143000',
                16: '2001^Davis^Karen', 20: '3001^Miller^Thomas', 25: 'Booked'}),
            PID,
            'RGS|1',
            segment('AIS', {1: '1', 3: '99213^Office visit established patient^CPT'}),
            segment('AIP', {1: '1', 3: Doctor, 4: 'ATTENDING^Attending physician^L'}),
            segment('AIL', {1: '1', 3: 'CLINIC^ROOM5^^GENHOSP', 4: 'CLINIC^Outpatient clinic^L'}),
        )

        appointment = one_resource(bundle, 'Appointment')

        assert appointment['status'] == 'booked'
        assert appointment['identifier'] == [{'value': 'APT6001', 'system': 'urn:zato:hl7v2:authority:SCHED'}]
        assert appointment['reasonCode'][0]['coding'][0]['code'] == 'FOLLOWUP'
        assert appointment['appointmentType']['coding'][0]['code'] == 'ROUTINE'
        assert appointment['minutesDuration'] == 30
        assert appointment['start'] == '2026-04-01T14:00:00+00:00'
        assert appointment['end'] == '2026-04-01T14:30:00+00:00'
        assert appointment['serviceType'][0]['coding'][0]['code'] == '99213'
        assert len(appointment['participant']) == 4

        # The event reason and who entered the booking have no Appointment element, so they are kept as-is.
        urls = []
        for extension in appointment['extension']:
            urls.append(extension['url'])

        assert urls == [Unmapped + '/SCH-6', Unmapped + '/SCH-20']
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_vxu_v04_immunization(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|EHR|GENHOSP|IIS|STATE|20260315110000||VXU^V04^VXU_V04|MSG0012|P|2.5.1',
            PID,
            segment('ORC', {1: 'RE', 3: 'IMM8001^EHR'}),
            segment('RXA', {1: '0', 2: '1', 3: '20260315104500', 4: '20260315104500', 5: '140^Influenza seasonal injectable preservative free^CVX',
                6: '0.5', 7: 'mL^^UCUM', 9: '00^New immunization record^NIP001', 10: '2001^Davis^Karen^^^^RN', 15: 'FLU2026A',
                16: '20261031', 17: 'SKB^GlaxoSmithKline^MVX', 20: 'CP'}),
            'RXR|IM^Intramuscular^HL70162|LD^Left deltoid^HL70163',
        )

        immunization = one_resource(bundle, 'Immunization')

        assert immunization['status'] == 'completed'
        assert immunization['vaccineCode']['coding'][0] == {
            'code': '140',
            'display': 'Influenza seasonal injectable preservative free',
            'system': 'http://hl7.org/fhir/sid/cvx',
        }
        assert immunization['occurrenceDateTime'] == '2026-03-15T10:45:00+00:00'
        assert immunization['doseQuantity']['value'] == 0.5
        assert immunization['primarySource'] is True
        assert immunization['lotNumber'] == 'FLU2026A'
        assert immunization['expirationDate'] == '2026-10-31'
        assert immunization['route']['coding'][0]['code'] == 'IM'
        assert immunization['site']['coding'][0]['code'] == 'LD'
        assert immunization['identifier'] == [{'value': 'IMM8001', 'system': 'urn:zato:hl7v2:authority:EHR'}]

        _assert_clean(bundle)

# ################################################################################################################################
# ################################################################################################################################

class TestPharmacyAndBilling:

    def test_rde_o11_compound_order(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|EHR|GENHOSP|PHARM|GENHOSP|20260315120000||RDE^O11^RDE_O11|MSG0013|P|2.5.1',
            PID,
            'PV1|1|I|WEST^201^B^GENHOSP',
            segment('ORC', {1: 'NW', 2: 'RX9001^EHR', 9: '20260315120000', 12: Doctor}),
            segment('RXE', {2: 'TPN001^TPN Solution^L', 3: '1000', 5: 'mL^^UCUM'}),
            segment('TQ1', {1: '1', 3: 'Q24H^Every 24 hours^HL70335', 4: '1800', 7: '20260315', 8: '20260320',
                9: 'R^Routine^HL70485', 11: 'Infuse over 12 hours'}),
            'RXR|IV^Intravenous^HL70162',
            segment('RXC', {1: 'B', 2: 'DEX10^Dextrose 10%^L', 3: '500', 4: 'mL^^UCUM'}),
            segment('RXC', {1: 'A', 2: 'AMINO^Amino acids^L', 3: '50', 4: 'g^^UCUM', 8: '1000', 9: 'mL^^UCUM'}),
        )

        request = one_resource(bundle, 'MedicationRequest')
        medication = one_resource(bundle, 'Medication')

        assert request['medicationReference'] == {'reference': _full_url_of(bundle, medication)}
        assert request['authoredOn'] == '2026-03-15T12:00:00+00:00'
        assert 'requester' in request
        assert request['priority'] == 'routine'

        dosage = request['dosageInstruction'][0]
        assert dosage['timing']['repeat']['period'] == 24
        assert dosage['timing']['repeat']['timeOfDay'] == ['18:00:00']
        assert dosage['text'] == 'Infuse over 12 hours'
        assert dosage['route']['coding'][0]['code'] == 'IV'

        base, additive = medication['ingredient']

        assert medication['code']['coding'][0]['code'] == 'TPN001'
        assert base['isActive'] is False
        assert base['strength']['numerator']['value'] == 500.0
        assert additive['isActive'] is True
        assert additive['strength']['denominator']['value'] == 1000.0

        _assert_clean(bundle)

# ################################################################################################################################

    def test_rds_o13_dispense(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|PHARM|GENHOSP|EHR|GENHOSP|20260315130000||RDS^O13^RDS_O13|MSG0014|P|2.5.1',
            PID,
            segment('ORC', {1: 'RE', 2: 'RX9002^EHR', 3: 'FIL9002^PHARM'}),
            segment('RXD', {1: '1', 2: 'AMOX500^Amoxicillin 500 mg capsule^L', 3: '20260315125500', 4: '30', 5: 'CAP^Capsule^HL70162',
                7: 'RX9002'}),
            segment('TQ1', {1: '1', 2: '1^CAP', 3: 'TID^Three times a day^HL70335'}),
            'RXR|PO^Oral^HL70162',
        )

        dispense = one_resource(bundle, 'MedicationDispense')

        assert dispense['status'] == 'completed'
        assert dispense['medicationCodeableConcept']['coding'][0]['code'] == 'AMOX500'
        assert dispense['whenHandedOver'] == '2026-03-15T12:55:00+00:00'
        assert dispense['quantity']['value'] == 30.0
        assert dispense['quantity']['code'] == 'CAP'
        assert dispense['identifier'] == [
            {'value': 'RX9002'},
            {'value': 'RX9002', 'system': 'urn:zato:hl7v2:authority:EHR'},
            {'value': 'FIL9002', 'system': 'urn:zato:hl7v2:authority:PHARM'},
        ]

        dosage = dispense['dosageInstruction'][0]
        assert dosage['timing'] == {'repeat': {'frequency': 3, 'period': 1, 'periodUnit': 'd'}}
        assert dosage['doseAndRate'] == [{'doseQuantity': {'value': 1.0, 'unit': 'CAP'}}]
        assert dosage['route']['coding'][0]['code'] == 'PO'

        _assert_clean(bundle)

# ################################################################################################################################

    def test_dft_p03_charge(self) -> 'None':
        bundle = convert(
            'MSH|^~\\&|BILLING|GENHOSP|EHR|GENHOSP|20260318170000||DFT^P03^DFT_P03|MSG0015|P|2.5.1',
            'EVN|P03|20260318170000',
            PID,
            segment('PV1', {1: '1', 2: 'O', 3: 'CLINIC^^^GENHOSP', 19: 'V2026002^^^GENHOSP'}),
            segment('FT1', {1: '1', 2: 'TXN5001^BILLING', 4: '20260318', 6: 'CG', 7: '99213^Office visit established patient^CPT',
                10: '1', 20: Doctor}),
        )

        charge = one_resource(bundle, 'ChargeItem')
        encounter = one_resource(bundle, 'Encounter')

        assert charge['status'] == 'billable'
        assert charge['code']['coding'][0]['code'] == '99213'
        assert charge['identifier'] == [{'value': 'TXN5001', 'system': 'urn:zato:hl7v2:authority:BILLING'}]
        assert charge['occurrenceDateTime'] == '2026-03-18'
        assert charge['quantity'] == {'value': 1.0}
        assert charge['context'] == {'reference': _full_url_of(bundle, encounter)}
        assert len(charge['performer']) == 1

        _assert_clean(bundle)

# ################################################################################################################################
# ################################################################################################################################
