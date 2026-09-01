# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, organization_named, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every segment test builds on.
MSH = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q|||M'
PV1 = 'PV1|1|I|WARD1^101^A^GENHOSP|||||||MED|||||||||VN123^^^MYHOSP'

# ################################################################################################################################
# ################################################################################################################################

class TestROL:
    """ ROL segments become Encounter participants.
    """

    def test_rol_before_pv1(self) -> 'None':
        # IHE PAM places ROL between PID and PV1 - it still becomes an Encounter participant.
        rol = 'ROL||AD|FHCP|7777^Morris^Philip'

        bundle = convert(MSH, PID, rol, PV1)

        encounter = one_resource(bundle, 'Encounter')
        practitioner = one_resource(bundle, 'Practitioner')

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Morris'

        participants = encounter['participant']
        participant = participants[0]

        participant_types = participant['type']
        participant_type = participant_types[0]
        type_codings = participant_type['coding']
        type_coding = type_codings[0]

        assert type_coding['code'] == 'FHCP'

# ################################################################################################################################
# ################################################################################################################################

class TestMSH:
    """ MSH segments become MessageHeader resources.
    """

    def test_message_header(self) -> 'None':
        bundle = convert(MSH, PID)
        header = one_resource(bundle, 'MessageHeader')

        assert header['eventCoding'] == {'system': 'http://terminology.hl7.org/CodeSystem/v2-0003', 'code': 'A01'}
        assert header['source'] == {'name': 'SENDAPP', 'endpoint': 'urn:zato:hl7v2:authority:SENDAPP'}

        destinations = header['destination']
        destination = destinations[0]

        assert destination['name'] == 'RECVAPP'
        assert destination['endpoint'] == 'urn:zato:hl7v2:authority:RECVAPP'

        # The facilities became the sender and receiver Organizations.
        sender = organization_named(bundle, 'SENDFAC')
        receiver = organization_named(bundle, 'RECVFAC')

        assert sender['name'] == 'SENDFAC'
        assert receiver['name'] == 'RECVFAC'

        sender_reference = header['sender']
        sender_url = sender_reference['reference']

        assert sender_url.startswith('urn:uuid:')

        receiver_reference = destination['receiver']
        receiver_url = receiver_reference['reference']

        assert receiver_url.startswith('urn:uuid:')

# ################################################################################################################################

    def test_header_points_at_patient(self) -> 'None':
        bundle = convert(MSH, PID)
        bundle_dict = bundle.to_dict()

        header = one_resource(bundle, 'MessageHeader')
        patient_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_url = entry['fullUrl']

        assert header['focus'] == [{'reference': patient_url}]

# ################################################################################################################################

    def test_bundle_control_id_and_timestamp(self) -> 'None':
        bundle = convert(MSH, PID)
        bundle_dict = bundle.to_dict()

        assert bundle_dict['identifier'] == {'system': 'urn:zato:hl7v2:message-control-id', 'value': 'MSG00001'}
        assert bundle_dict['timestamp'] == '2024-05-17T14:30:55+00:00'

        # MSH-11 rides along as the processing-mode tag.
        meta = bundle_dict['meta']
        assert meta['tag'] == [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0103', 'code': 'P'}]

# ################################################################################################################################
# ################################################################################################################################

class TestPID:
    """ PID segments become Patient resources.
    """

    def test_patient_core_fields(self) -> 'None':
        pid = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q||19800115|M|||123 Main St^^Springfield^IL^62701^USA^H' + \
            '||(555)555-1234^PRN^PH|||M|||987-65-4320'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        identifiers = patient['identifier']
        mrn_identifier = identifiers[0]
        ssn_identifier = identifiers[1]

        assert mrn_identifier['value'] == '12345'
        assert mrn_identifier['system'] == 'urn:zato:hl7v2:authority:MYHOSP'

        # The field carries a bare value with no authority, so the identifier
        # has the SS type code and no system of its own.
        assert ssn_identifier['value'] == '987-65-4320'
        assert 'system' not in ssn_identifier
        assert ssn_identifier['type'] == {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'SS'}]}

        assert patient['name'] == [{'family': 'Smith', 'given': ['John', 'Q']}]
        assert patient['birthDate'] == '1980-01-15'
        assert patient['gender'] == 'male'

        addresses = patient['address']
        home_address = addresses[0]

        assert home_address['city'] == 'Springfield'
        assert home_address['use'] == 'home'

        telecoms = patient['telecom']
        home_telecom = telecoms[0]

        assert home_telecom['value'] == '(555)555-1234'

        marital_status = patient['maritalStatus']
        marital_codings = marital_status['coding']
        marital_coding = marital_codings[0]

        assert marital_coding['code'] == 'M'

# ################################################################################################################################

    def test_deceased_patient(self) -> 'None':
        pid = 'PID|1||12345||Smith^John|||M|||||||||||||||||||||20240101120000|Y'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        # The timestamp wins over the yes/no indicator.
        assert patient['deceasedDateTime'] == '2024-01-01T12:00:00+00:00'
        assert 'deceasedBoolean' not in patient

# ################################################################################################################################

    def test_multiple_birth_order(self) -> 'None':
        pid = 'PID|1||12345||Smith^Baby|||F||||||||||||||||Y|2'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        assert patient['multipleBirthInteger'] == 2

# ################################################################################################################################

    def test_unknown_gender_code_is_preserved(self) -> 'None':
        pid = 'PID|1||12345||Smith^John|||X9'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        # The unknown code never becomes a gender but survives as an extension.
        assert 'gender' not in patient

        extensions = patient['extension']
        preserved = extensions[0]

        assert preserved == {'url': 'urn:zato:hl7v2:extension/unmapped/PID-8', 'valueString': 'X9'}

# ################################################################################################################################
# ################################################################################################################################

class TestNK1:
    """ NK1 segments become RelatedPerson resources.
    """

    def test_related_person(self) -> 'None':
        nk1 = 'NK1|1|Smith^Jane|SPO^Spouse^HL70063|456 Oak St^^Springfield^IL^62701|(555)555-9999'

        bundle = convert(MSH, PID, nk1)
        related = one_resource(bundle, 'RelatedPerson')

        assert related['name'] == [{'family': 'Smith', 'given': ['Jane']}]

        relationships = related['relationship']
        relationship = relationships[0]
        relationship_codings = relationship['coding']
        relationship_coding = relationship_codings[0]

        assert relationship_coding['code'] == 'SPO'

        addresses = related['address']
        address = addresses[0]

        assert address['line'] == ['456 Oak St']

        telecoms = related['telecom']
        telecom = telecoms[0]

        assert telecom['value'] == '(555)555-9999'

        # The related person points back at the patient.
        patient_reference = related['patient']
        reference_url = patient_reference['reference']

        assert reference_url.startswith('urn:uuid:')

# ################################################################################################################################
# ################################################################################################################################

class TestPV1:
    """ PV1 segments become Encounter resources.
    """

    def test_encounter_core_fields(self) -> 'None':
        bundle = convert(MSH, PID, PV1)
        encounter = one_resource(bundle, 'Encounter')

        # Patient class I is inpatient, mapping to IMP and in-progress.
        encounter_class = encounter['class']

        assert encounter_class['code'] == 'IMP'
        assert encounter['status'] == 'in-progress'

        identifiers = encounter['identifier']
        visit_identifier = identifiers[0]

        assert visit_identifier['value'] == 'VN123'

        subject = encounter['subject']
        subject_url = subject['reference']

        assert subject_url.startswith('urn:uuid:')

# ################################################################################################################################

    def test_location_resource(self) -> 'None':
        bundle = convert(MSH, PID, PV1)

        location = one_resource(bundle, 'Location')
        assert location['name'] == 'WARD1-101-A-GENHOSP'

        encounter = one_resource(bundle, 'Encounter')

        locations = encounter['location']
        first_location = locations[0]
        location_reference = first_location['location']
        location_url = location_reference['reference']

        assert location_url.startswith('urn:uuid:')

# ################################################################################################################################

    def test_location_facility_universal_id(self) -> 'None':
        # A spelled-out facility name can arrive in the HD universal ID subcomponent.
        pv1 = 'PV1|1|O|^^^0105&North Clinic'

        bundle = convert(MSH, PID, pv1)
        location = one_resource(bundle, 'Location')

        assert location['name'] == '0105-North Clinic'

# ################################################################################################################################

    def test_location_description(self) -> 'None':
        # PL-9 spells out what the location is.
        pv1 = 'PV1|1|O|^12^^^^^^^West Wing Clinic'

        bundle = convert(MSH, PID, pv1)
        location = one_resource(bundle, 'Location')

        assert location['name'] == '12'
        assert location['description'] == 'West Wing Clinic'

# ################################################################################################################################

    def test_attending_doctor_becomes_practitioner(self) -> 'None':
        pv1 = 'PV1|1|O|||||1234^Welby^Marcus^^^Dr'

        bundle = convert(MSH, PID, pv1)
        practitioner = one_resource(bundle, 'Practitioner')

        practitioner_identifiers = practitioner['identifier']
        practitioner_identifier = practitioner_identifiers[0]

        assert practitioner_identifier['value'] == '1234'

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Welby'

        encounter = one_resource(bundle, 'Encounter')

        participants = encounter['participant']
        participant = participants[0]
        participant_types = participant['type']
        participant_type = participant_types[0]
        type_codings = participant_type['coding']
        type_coding = type_codings[0]

        assert type_coding['code'] == 'ATND'

# ################################################################################################################################

    def test_discharge_makes_encounter_finished(self) -> 'None':
        pv1 = 'PV1|1|I|||||||||||||||||VN1|||||||||||||||||||||||||20240501100000|20240503150000'

        bundle = convert(MSH, PID, pv1)
        encounter = one_resource(bundle, 'Encounter')

        assert encounter['status'] == 'finished'
        assert encounter['period'] == {'start': '2024-05-01T10:00:00+00:00', 'end': '2024-05-03T15:00:00+00:00'}

# ################################################################################################################################

    def test_pv2_admit_reason(self) -> 'None':
        pv2 = 'PV2|||Routine checkup'

        bundle = convert(MSH, PID, PV1, pv2)
        encounter = one_resource(bundle, 'Encounter')

        reason_codes = encounter['reasonCode']
        reason = reason_codes[0]

        assert reason['text'] == 'Routine checkup'

# ################################################################################################################################
# ################################################################################################################################

class TestOBX:
    """ OBX segments become Observation resources.
    """

    def test_numeric_observation(self) -> 'None':
        obx = 'OBX|1|NM|8302-2^Body Height^LN||175|cm^^UCUM|150-200|N|||F|||20240517'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        code = observation['code']
        code_codings = code['coding']
        code_coding = code_codings[0]

        assert code_coding == {'code': '8302-2', 'display': 'Body Height', 'system': 'http://loinc.org'}
        assert observation['status'] == 'final'

        assert observation['valueQuantity'] == {
            'value': 175.0,
            'code': 'cm',
            'system': 'http://unitsofmeasure.org',
            'unit': 'cm',
        }

        assert observation['referenceRange'] == [{'text': '150-200'}]

        interpretations = observation['interpretation']
        interpretation = interpretations[0]
        interpretation_codings = interpretation['coding']
        interpretation_coding = interpretation_codings[0]

        assert interpretation_coding['code'] == 'N'
        assert observation['effectiveDateTime'] == '2024-05-17'

# ################################################################################################################################

    def test_text_observation(self) -> 'None':
        obx = 'OBX|1|ST|GDT^Description||All results in good shape||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'All results in good shape'

# ################################################################################################################################

    def test_coded_observation(self) -> 'None':
        obx = 'OBX|1|CWE|11331-6^Fitness status^LN||excellent^Excellent^L||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        concept = observation['valueCodeableConcept']
        concept_codings = concept['coding']
        concept_coding = concept_codings[0]

        assert concept_coding['code'] == 'excellent'

# ################################################################################################################################

    def test_repeating_coded_observation(self) -> 'None':
        # Every repetition of the coded value contributes its coding to the one concept.
        obx = 'OBX|1|CE|CHOICES^Multiple choices^L||first^First^L~second^Second^L||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        concept = observation['valueCodeableConcept']
        concept_codings = concept['coding']

        first_coding = concept_codings[0]
        second_coding = concept_codings[1]

        assert first_coding == {'code': 'first', 'display': 'First'}
        assert second_coding == {'code': 'second', 'display': 'Second'}

# ################################################################################################################################

    def test_structured_numeric_observation(self) -> 'None':
        obx = 'OBX|1|SN|TITER^Titer||^1^:^128||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueRatio'] == {'numerator': {'value': 1.0}, 'denominator': {'value': 128.0}}

# ################################################################################################################################

    def test_datetime_observation(self) -> 'None':
        obx = 'OBX|1|DTM|COLLECT^Collection time||20240517143000||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueDateTime'] == '2024-05-17T14:30:00+00:00'

# ################################################################################################################################

    def test_time_observation(self) -> 'None':
        obx = 'OBX|1|TM|WAKE^Wake time||063000||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueTime'] == '06:30:00'

# ################################################################################################################################

    def test_status_defaults_to_unknown(self) -> 'None':
        obx = 'OBX|1|ST|GDT^Description||Feeling great'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['status'] == 'unknown'

# ################################################################################################################################

    def test_encapsulated_data_with_spelled_out_media_type(self) -> 'None':
        # ED-2 carries the literal media type word instead of the HL7 table code.
        obx = 'OBX|1|ED|DOC^Document||^application^pdf^Base64^JVBERi0xLjQK||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        extensions = observation['extension']
        attachment_extension = extensions[0]
        attachment = attachment_extension['valueAttachment']

        assert attachment['contentType'] == 'application/pdf'
        assert attachment['data'] == 'JVBERi0xLjQK'

# ################################################################################################################################
# ################################################################################################################################

class TestAL1:
    """ AL1 segments become AllergyIntolerance resources.
    """

    def test_allergy(self) -> 'None':
        al1 = 'AL1|1|LA|1543^Pollen^RXNORM|MI|Sneezing'

        bundle = convert(MSH, PID, al1)
        allergy = one_resource(bundle, 'AllergyIntolerance')

        code = allergy['code']
        code_codings = code['coding']
        code_coding = code_codings[0]

        assert code_coding['code'] == '1543'

        # LA is a pollen allergy, an environmental category.
        assert allergy['category'] == ['environment']

        # MI is mild, mapping to both criticality and reaction severity.
        assert allergy['criticality'] == 'low'
        assert allergy['reaction'] == [{'manifestation': [{'text': 'Sneezing'}], 'severity': 'mild'}]

        patient_reference = allergy['patient']
        reference_url = patient_reference['reference']

        assert reference_url.startswith('urn:uuid:')

# ################################################################################################################################
# ################################################################################################################################

class TestDG1:
    """ DG1 segments become Condition resources.
    """

    def test_condition_and_encounter_diagnosis(self) -> 'None':
        dg1 = 'DG1|1||Z00.0^Routine health check^I10||20240101|A'

        bundle = convert(MSH, PID, PV1, dg1)
        condition = one_resource(bundle, 'Condition')

        code = condition['code']
        code_codings = code['coding']
        code_coding = code_codings[0]

        assert code_coding['code'] == 'Z00.0'
        assert condition['onsetDateTime'] == '2024-01-01'

        # The encounter records the diagnosis with its role.
        encounter = one_resource(bundle, 'Encounter')

        diagnoses = encounter['diagnosis']
        diagnosis = diagnoses[0]

        condition_reference = diagnosis['condition']
        condition_url = condition_reference['reference']

        assert condition_url.startswith('urn:uuid:')

        diagnosis_use = diagnosis['use']
        use_codings = diagnosis_use['coding']
        use_coding = use_codings[0]

        assert use_coding['code'] == 'AD'

# ################################################################################################################################
# ################################################################################################################################

class TestPR1:
    """ PR1 segments become Procedure resources.
    """

    def test_procedure(self) -> 'None':
        pr1 = 'PR1|1||410620009^Wellness visit^SCT||20240502093000||||||5678^Carter^Jane'

        bundle = convert(MSH, PID, PV1, pr1)
        procedure = one_resource(bundle, 'Procedure')

        assert procedure['status'] == 'completed'

        code = procedure['code']
        code_codings = code['coding']
        code_coding = code_codings[0]

        assert code_coding['code'] == '410620009'
        assert procedure['performedDateTime'] == '2024-05-02T09:30:00+00:00'

        performers = procedure['performer']
        performer = performers[0]
        actor = performer['actor']
        actor_url = actor['reference']

        assert actor_url.startswith('urn:uuid:')

# ################################################################################################################################
# ################################################################################################################################

class TestPD1:
    """ PD1 segments enrich the Patient with a general practitioner.
    """

    def test_general_practitioner(self) -> 'None':
        pd1 = 'PD1|||Family Practice Clinic|1234^Welby^Marcus'

        bundle = convert(MSH, PID, pd1)
        patient = one_resource(bundle, 'Patient')

        organization = organization_named(bundle, 'Family Practice Clinic')
        assert organization['name'] == 'Family Practice Clinic'

        practitioner = one_resource(bundle, 'Practitioner')

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Welby'

        general_practitioners = patient['generalPractitioner']
        assert len(general_practitioners) == 2

# ################################################################################################################################

    def test_facility_identifier(self) -> 'None':

        # XON-3 is the identifier of the primary facility.
        pd1 = 'PD1|||Riverside Medical Centre^^Y99901'

        bundle = convert(MSH, PID, pd1)

        organization = organization_named(bundle, 'Riverside Medical Centre')
        assert organization['identifier'] == [{'value': 'Y99901'}]

# ################################################################################################################################
# ################################################################################################################################

class TestDeduplication:
    """ Identical resources are stored once and shared by reference.
    """

    def test_same_practitioner_dedupes(self) -> 'None':
        # The same doctor is the attending, the referring and the admitting one.
        pv1 = 'PV1|1|O|||||1234^Welby^Marcus|1234^Welby^Marcus|||||||||1234^Welby^Marcus'

        bundle = convert(MSH, PID, pv1)

        practitioners = resources_of_type(bundle, 'Practitioner')
        assert len(practitioners) == 1

        # All three participants point at the same resource.
        encounter = one_resource(bundle, 'Encounter')
        participants = encounter['participant']

        references = set()

        for participant in participants:
            individual = participant['individual']
            references.add(individual['reference'])

        assert len(participants) == 3
        assert len(references) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestUnmappedFields:
    """ Populated fields the mapper does not consume become extensions.
    """

    def test_populated_unhandled_field_is_preserved(self) -> 'None':
        # PID-22, ethnic group, is not a field the mapper consumes.
        pid = 'PID|1||12345||Smith^John|||M||||||||||||||2186-5'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        # The value survives as an extension instead of raising a warning.
        extensions = patient['extension']
        preserved = extensions[0]

        assert preserved == {'url': 'urn:zato:hl7v2:extension/unmapped/PID-22', 'valueString': '2186-5'}

        warnings = get_conversion_warnings(bundle)
        assert warnings == []

# ################################################################################################################################

    def test_clean_message_has_no_warnings(self) -> 'None':
        bundle = convert(MSH, PID)
        warnings = get_conversion_warnings(bundle)

        assert warnings == []

# ################################################################################################################################
# ################################################################################################################################
