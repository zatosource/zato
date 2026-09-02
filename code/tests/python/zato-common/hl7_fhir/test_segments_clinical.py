# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every segment test builds on.
MSH = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q|||M'
PV1 = 'PV1|1|I|WARD1^101^A^GENHOSP|||||||MED|||||||||VN123^^^MYHOSP'

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

    def test_text_observation_decodes_escapes(self) -> 'None':
        # Formatting escapes become their characters and highlight markers are dropped.
        obx = r'OBX|1|FT|GDT^Description||Line one\.br\Line two \H\bold\N\ 1 \S\ 2 is \F\ separated||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'Line one\nLine two bold 1 ^ 2 is | separated'

# ################################################################################################################################

    def test_non_datetime_observation_time_is_preserved(self) -> 'None':
        # Other values can arrive in the OBX-14 observation-time slot with
        # shifted vendor feeds - those cannot become the effective time but
        # they are not dropped either.
        obx = 'OBX|1|ST|6462-6^Wound Culture^LN||Moderate growth||||||F|||LAB-STATION-4'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert 'effectiveDateTime' not in observation

        extensions = observation['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/OBX-14',
            'valueString': 'LAB-STATION-4',
        } in extensions

# ################################################################################################################################

    def test_text_observation_joins_repetitions_into_lines(self) -> 'None':
        # Senders split narrative reports into repetitions - each becomes
        # a line of its own so no part of the narrative is ever lost.
        obx = 'OBX|1|TX|22637-3^Pathology report^LN||REPORT TITLE~~FINDINGS: All clear.~~CONCLUSION: Negative.||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'REPORT TITLE\n\nFINDINGS: All clear.\n\nCONCLUSION: Negative.'

# ################################################################################################################################

    def test_text_observation_decodes_literal_periods(self) -> 'None':
        # Senders that escape literal periods produce \. pairs - each decodes to
        # its period without disturbing real formatting commands around it.
        obx = r'OBX|1|FT|GDT^Description||First\. Second sentence\. And a real\.br\line break\.||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'First. Second sentence. And a real\nline break.'

# ################################################################################################################################

    def test_text_observation_keeps_unknown_formatting_commands_verbatim(self) -> 'None':
        # Formatting commands the decoder does not know, like indentation,
        # stay whole so no wire data is ever lost.
        obx = r'OBX|1|FT|GDT^Description||before\.in+4\after||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['valueString'] == 'before\\.in+4\\after'

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

    def test_encapsulated_data_with_full_mime_subtype(self) -> 'None':
        # ED-3 carries a complete MIME type already, which must not be prefixed again.
        obx = 'OBX|1|ED|IMG^Image||^image^image/jpeg^Base64^/9j/4AAQ||||||F'

        bundle = convert(MSH, PID, obx)
        observation = one_resource(bundle, 'Observation')

        extensions = observation['extension']
        attachment_extension = extensions[0]
        attachment = attachment_extension['valueAttachment']

        assert attachment['contentType'] == 'image/jpeg'
        assert attachment['data'] == '/9j/4AAQ'

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

    def test_spelled_out_severity(self) -> 'None':
        # The severity can arrive spelled out instead of coded - MODERATE maps
        # to the reaction severity and, like the MO code, to no criticality.
        al1 = 'AL1|1|DA|70618^Penicillin^RXNORM|MODERATE|Rash'

        bundle = convert(MSH, PID, al1)
        allergy = one_resource(bundle, 'AllergyIntolerance')

        assert 'criticality' not in allergy
        assert allergy['reaction'] == [{'manifestation': [{'text': 'Rash'}], 'severity': 'moderate'}]

# ################################################################################################################################

    def test_unknown_severity_is_preserved(self) -> 'None':
        # A severity that maps to neither criticality nor reaction severity is not dropped.
        al1 = 'AL1|1|DA|70618^Penicillin^RXNORM|EXTREME|Rash'

        bundle = convert(MSH, PID, al1)
        allergy = one_resource(bundle, 'AllergyIntolerance')

        assert 'criticality' not in allergy
        assert allergy['reaction'] == [{'manifestation': [{'text': 'Rash'}]}]

        extensions = allergy['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/AL1-4',
            'valueString': 'EXTREME',
        } in extensions

# ################################################################################################################################
# ################################################################################################################################

class TestIAM:
    """ IAM segments - the successor of AL1 - become AllergyIntolerance resources.
    """

    def test_allergy_with_identifier_and_dates(self) -> 'None':
        iam = 'IAM|1|DA^Drug Allergy^HL70127|70618^Penicillin^RXNORM|SV^Severe^HL70128|Anaphylaxis|' + \
            'A^Add^HL70323|ALG-001^EHR||||20230412||20240517143000'

        bundle = convert(MSH, PID, iam)
        allergy = one_resource(bundle, 'AllergyIntolerance')

        code_coding = allergy['code']['coding'][0]
        assert code_coding['code'] == '70618'

        # DA is a drug allergy, a medication category.
        assert allergy['category'] == ['medication']

        # SV is severe, mapping to both criticality and reaction severity.
        assert allergy['criticality'] == 'high'
        assert allergy['reaction'] == [{'manifestation': [{'text': 'Anaphylaxis'}], 'severity': 'severe'}]

        # The unique identifier carried over.
        assert allergy['identifier'] == [{'value': 'ALG-001', 'system': 'urn:zato:hl7v2:authority:EHR'}]

        # The onset and reported times carried over.
        assert allergy['onsetDateTime'] == '2023-04-12'
        assert allergy['recordedDate'] == '2024-05-17T14:30:00+00:00'

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_deleted_allergy_was_entered_in_error(self) -> 'None':
        iam = 'IAM|1|DA^Drug Allergy^HL70127|70618^Penicillin^RXNORM||Rash|D^Delete^HL70323|ALG-002^EHR'

        bundle = convert(MSH, PID, iam)
        allergy = one_resource(bundle, 'AllergyIntolerance')

        assert allergy['verificationStatus'] == {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/allergyintolerance-verification',
                'code': 'entered-in-error',
            }],
        }

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_unknown_action_code_is_preserved(self) -> 'None':
        iam = 'IAM|1|DA^Drug Allergy^HL70127|70618^Penicillin^RXNORM||Rash|REVIEWED|ALG-003^EHR'

        bundle = convert(MSH, PID, iam)
        allergy = one_resource(bundle, 'AllergyIntolerance')

        assert 'verificationStatus' not in allergy

        extensions = allergy['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/IAM-6', 'valueString': 'REVIEWED'} in extensions

        assert get_conversion_warnings(bundle) == []

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
