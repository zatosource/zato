# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, convert_fixture, one_resource, organization_named, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

MSH_ADT = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
MSH_SIU = 'MSH|^~\\&|SCHED|SCHEDFAC|EHR|EHRFAC|20240517143055||SIU^S12|MSG00004|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestIN1Coverage:
    """ IN1 segments become Coverage resources.
    """

    def test_coverage_core_fields(self) -> 'None':
        in1 = 'IN1|1|PLAN01|IC123^^^^NIIP|Great Health Insurance||||GRP-77||' + \
            '||20240101|20241231||HMO^Health Plan^HL70086|Smith^John|SEL^Self^HL70063|||||||||||||||||||POL-42'

        bundle = convert(MSH_ADT, PID, in1)
        coverage = one_resource(bundle, 'Coverage')

        assert coverage['status'] == 'active'

        # The insurance company became the payor Organization.
        organization = organization_named(bundle, 'Great Health Insurance')
        assert organization['name'] == 'Great Health Insurance'

        payors = coverage['payor']
        payor = payors[0]
        payor_url = payor['reference']

        assert payor_url.startswith('urn:uuid:')

        # The plan and the group number are class entries.
        classes = coverage['class']
        plan_class = classes[0]
        group_class = classes[1]

        assert plan_class['value'] == 'PLAN01'
        assert group_class['value'] == 'GRP-77'

        # The plan dates bound the period.
        assert coverage['period'] == {'start': '2024-01-01', 'end': '2024-12-31'}

        # SEL means the patient subscribes to their own plan.
        subscriber = coverage['subscriber']
        beneficiary = coverage['beneficiary']

        assert subscriber == beneficiary

        # The policy number doubles as the identifier and the subscriber ID.
        assert coverage['subscriberId'] == 'POL-42'
        assert coverage['identifier'] == [{'value': 'POL-42'}]

# ################################################################################################################################

    def test_repeating_in1_makes_multiple_coverages(self) -> 'None':
        in1_first = 'IN1|1|PLAN01||First Health'
        in1_second = 'IN1|2|PLAN02||Second Health'

        bundle = convert(MSH_ADT, PID, in1_first, in1_second)

        coverages = resources_of_type(bundle, 'Coverage')

        assert len(coverages) == 2

        # Each insurance company became its own payor Organization.
        _ = organization_named(bundle, 'First Health')
        _ = organization_named(bundle, 'Second Health')

# ################################################################################################################################
# ################################################################################################################################

class TestSIUAppointment:
    """ SIU messages become Appointment resources.
    """

    def test_appointment_core_fields(self) -> 'None':
        sch = 'SCH|APPT-1^SCHED|FIL-1^SCHED||||CHECKUP^Wellness checkup^L||ROUTINE^Routine^HL70276|30|MIN^Minutes' + \
            '|^^^20240601090000^20240601093000|||||||||||||||Booked'
        ais = 'AIS|1||EXAM^Wellness exam^L'

        bundle = convert(MSH_SIU, PID, sch, ais)
        appointment = one_resource(bundle, 'Appointment')

        assert appointment['status'] == 'booked'

        identifiers = appointment['identifier']
        placer_identifier = identifiers[0]
        filler_identifier = identifiers[1]

        assert placer_identifier['value'] == 'APPT-1'
        assert filler_identifier['value'] == 'FIL-1'

        # SCH-6 is the event reason, not a clinical one, so it is preserved rather than mapped to reasonCode.
        assert 'reasonCode' not in appointment

        extensions = appointment['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/SCH-6', 'valueString': 'CHECKUP^Wellness checkup^L'} in extensions

        assert appointment['minutesDuration'] == 30
        assert appointment['start'] == '2024-06-01T09:00:00+00:00'
        assert appointment['end'] == '2024-06-01T09:30:00+00:00'

        # The AIS service joined the appointment.
        service_types = appointment['serviceType']
        service_type = service_types[0]

        assert service_type['text'] == 'Wellness exam'

# ################################################################################################################################

    def test_patient_is_a_participant(self) -> 'None':
        sch = 'SCH|APPT-1^SCHED|FIL-1^SCHED||||CHECKUP^Wellness checkup^L'

        bundle = convert(MSH_SIU, PID, sch)
        appointment = one_resource(bundle, 'Appointment')

        bundle_dict = bundle.to_dict()
        patient_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_url = entry['fullUrl']

        participants = appointment['participant']
        patient_participant = participants[0]
        actor = patient_participant['actor']

        assert actor == {'reference': patient_url}
        assert patient_participant['status'] == 'accepted'

# ################################################################################################################################

    def test_personnel_and_location_participants(self) -> 'None':
        sch = 'SCH|APPT-1^SCHED|FIL-1^SCHED||||CHECKUP^Wellness checkup^L'
        aip = 'AIP|1||1234^Welby^Marcus'
        ail = 'AIL|1||CLINIC^^^MAINFAC'

        bundle = convert(MSH_SIU, PID, sch, aip, ail)
        appointment = one_resource(bundle, 'Appointment')

        # The patient, the practitioner and the location all take part.
        participants = appointment['participant']
        assert len(participants) == 3

        practitioner = one_resource(bundle, 'Practitioner')

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Welby'

        # The facility and the point of care become a Location hierarchy, the appointment takes place in the latter.
        facility, point_of_care = resources_of_type(bundle, 'Location')

        assert facility['name'] == 'MAINFAC'
        assert point_of_care['name'] == 'CLINIC'
        assert 'partOf' in point_of_care

        location_participant = participants[2]
        location_actor = location_participant['actor']

        assert location_actor['reference'].startswith('urn:uuid:')

# ################################################################################################################################

    def test_ig_siu_s12(self) -> 'None':
        bundle = convert_fixture('SIU_S12.hl7')
        appointment = one_resource(bundle, 'Appointment')

        assert appointment['status'] == 'booked'

        identifiers = appointment['identifier']
        assert len(identifiers) == 2

    def test_unparseable_duration_and_timing_stay_preserved(self) -> 'None':

        # A duration slot with no number in it makes no minutes - the value,
        # its units and the unusable timing quantity all stay preserved.
        sch = 'SCH|APT001|||||OFFICE^Office Visit|||MIN|^^30^20260418140000^20260418143000|TBD'

        bundle = convert(MSH_SIU, PID, sch)
        appointment = one_resource(bundle, 'Appointment')

        assert 'minutesDuration' not in appointment
        assert 'start' not in appointment

        extensions = appointment['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/SCH-9',
            'valueString': 'MIN',
        } in extensions

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/SCH-10',
            'valueString': '^^30^20260418140000^20260418143000',
        } in extensions

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/SCH-11',
            'valueString': 'TBD',
        } in extensions

# ################################################################################################################################
# ################################################################################################################################

class TestRDEPharmacyOrder:
    """ RDE messages become MedicationRequest resources.
    """

    def test_shifted_give_code_is_preserved_in_full(self) -> 'None':
        # The medication code can arrive shifted from RXE-2 into the RXE-3
        # amount slot - the whole coded value survives, not just its first component.
        msh = 'MSH|^~\\&|CPOE|HOSP|RX|PHARMACY|20240517143055||RDE^O01|MSG00007|P|2.5'
        orc = 'ORC|NW|RX001^CPOE'
        rxe = 'RXE|1^BID||5111-1^Amoxicillin 500mg^NDC|500||mg|CAP'

        bundle = convert(msh, PID, orc, rxe)
        medication_request = one_resource(bundle, 'MedicationRequest')

        extensions = medication_request['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/RXE-3',
            'valueString': '5111-1^Amoxicillin 500mg^NDC',
        } in extensions

# ################################################################################################################################

    def test_maximum_only_dose_becomes_a_high_range(self) -> 'None':

        # A give amount that arrives only in the RXE-4 maximum slot makes
        # a dose range with just the high bound.
        msh = 'MSH|^~\\&|CPOE|HOSP|RX|PHARMACY|20240517143055||RDE^O01|MSG00010|P|2.5'
        rxe = 'RXE|1^BID|316672^Vancomycin 1000 mg IV^RXNORM||1000|mg^milligram^UCUM'

        bundle = convert(msh, PID, rxe)
        medication_request = one_resource(bundle, 'MedicationRequest')

        dose = medication_request['dosageInstruction'][0]['doseAndRate'][0]

        assert dose['doseRange'] == {
            'high': {'value': 1000, 'unit': 'milligram', 'code': 'mg', 'system': 'http://unitsofmeasure.org'},
        }

# ################################################################################################################################
# ################################################################################################################################

class TestRXOPharmacyOrder:
    """ RXO - the prescriber's original order - becomes a MedicationRequest of its own.
    """

    def test_rxo_becomes_a_medication_request(self) -> 'None':
        msh = 'MSH|^~\\&|CPOE|HOSP|RX|PHARMACY|20240517143055||OMP^O09|MSG00020|P|2.5'
        orc = 'ORC|NW|RX010^CPOE'
        rxo = 'RXO|314076^Lisinopril 10 mg PO^RXNORM|10||mg^milligram^UCUM||TAKE WITH FOOD^^L|' + \
            'ONE TABLET DAILY^^L||||30|TAB^tablet^L|2'

        bundle = convert(msh, PID, orc, rxo)
        medication_request = one_resource(bundle, 'MedicationRequest')

        # An RXO is the original order, not the encoded one.
        assert medication_request['intent'] == 'original-order'
        assert medication_request['status'] == 'active'

        # The requested give code is the medication.
        medication = medication_request['medicationCodeableConcept']
        assert medication['text'] == 'Lisinopril 10 mg PO'

        coding = medication['coding'][0]
        assert coding['code'] == '314076'
        assert coding['system'] == 'http://www.nlm.nih.gov/research/umls/rxnorm'

        # The give amount and units make the dose.
        dosage = medication_request['dosageInstruction'][0]
        dose = dosage['doseAndRate'][0]

        assert dose['doseQuantity'] == {
            'value': 10, 'unit': 'milligram', 'code': 'mg', 'system': 'http://unitsofmeasure.org',
        }

        # The administration instructions spell the dosage out in words ..
        assert dosage['text'] == 'ONE TABLET DAILY'

        # .. and the pharmacy instructions became a note.
        assert medication_request['note'] == [{'text': 'TAKE WITH FOOD'}]

        # The dispense amount, units and refills make the dispense request.
        dispense_request = medication_request['dispenseRequest']

        # The dispense units are local, so per qty-3 there is no code without a system.
        assert dispense_request['quantity'] == {'value': 30, 'unit': 'tablet'}
        assert dispense_request['numberOfRepeatsAllowed'] == 2

        # The order number identifies the request.
        identifiers = medication_request['identifier']
        assert {'value': 'RX010', 'system': 'urn:zato:hl7v2:authority:CPOE'} in identifiers

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_rxo_shares_its_orc_with_the_rxe_that_follows(self) -> 'None':
        # In an RDE message the RXO and the RXE belong to one order group,
        # so both resources carry the group's order number.
        msh = 'MSH|^~\\&|CPOE|HOSP|RX|PHARMACY|20240517143055||RDE^O11|MSG00021|P|2.5'
        orc = 'ORC|NW|RX011^CPOE'
        rxo = 'RXO|314076^Lisinopril 10 mg PO^RXNORM|10||mg^milligram^UCUM'
        rxe = 'RXE|1^QD|314076^Lisinopril 10 mg PO^RXNORM|10||mg^milligram^UCUM'

        bundle = convert(msh, PID, orc, rxo, rxe)
        medication_requests = resources_of_type(bundle, 'MedicationRequest')

        assert len(medication_requests) == 2

        original_order = medication_requests[0]
        encoded_order = medication_requests[1]

        assert original_order['intent'] == 'original-order'
        assert encoded_order['intent'] == 'order'

        expected_identifier = {'value': 'RX011', 'system': 'urn:zato:hl7v2:authority:CPOE'}

        assert expected_identifier in original_order['identifier']
        assert expected_identifier in encoded_order['identifier']

        # No leftover ServiceRequest was made from the shared ORC.
        assert resources_of_type(bundle, 'ServiceRequest') == []

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_units_without_an_amount_are_preserved(self) -> 'None':
        # Senders shift other values into the units slots - without an amount
        # to pair them with they are preserved instead of being dropped.
        msh = 'MSH|^~\\&|CPOE|HOSP|RX|PHARMACY|20240517143055||OMP^O09|MSG00022|P|2.5'
        rxo = 'RXO|314076^Lisinopril 10 mg PO^RXNORM|||mg^milligram^UCUM'

        bundle = convert(msh, PID, rxo)
        medication_request = one_resource(bundle, 'MedicationRequest')

        assert 'dosageInstruction' not in medication_request

        extensions = medication_request['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/RXO-4',
            'valueString': 'mg^milligram^UCUM',
        } in extensions

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestFT1Charge:
    """ FT1 segments become ChargeItem resources.
    """

    def test_non_date_transaction_date_is_preserved(self) -> 'None':

        # A transaction date slot carrying something other than a date keeps its value.
        msh = 'MSH|^~\\&|BILLING|HOSP|EHR|HOSPFAC|20240517143055||DFT^P03|MSG00011|P|2.5'
        ft1 = 'FT1|1|TXN001||CG|D'

        bundle = convert(msh, PID, ft1)
        charge = one_resource(bundle, 'ChargeItem')

        extensions = charge['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/FT1-4',
            'valueString': 'CG',
        } in extensions

# ################################################################################################################################

    def test_coded_transaction_type_is_preserved_whole(self) -> 'None':

        # A transaction type slot carrying a full coded value keeps all its components.
        msh = 'MSH|^~\\&|BILLING|HOSP|EHR|HOSPFAC|20240517143055||DFT^P03|MSG00012|P|2.5'
        ft1 = 'FT1|1|TXN001||20240517143000||J0190^HEPARIN SODIUM INJECTION^HCPCS|HEPARIN DRIP'

        bundle = convert(msh, PID, ft1)
        charge = one_resource(bundle, 'ChargeItem')

        extensions = charge['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/FT1-6',
            'valueString': 'J0190^HEPARIN SODIUM INJECTION^HCPCS',
        } in extensions

# ################################################################################################################################
# ################################################################################################################################

class TestRDSPharmacyDispense:
    """ RDS messages become MedicationDispense resources.
    """

    def test_dispense_core_fields(self) -> 'None':
        msh = 'MSH|^~\\&|PHARM|HOSP|EHR|HOSPFAC|20240517143055||RDS^O13|MSG00008|P|2.5'
        orc = 'ORC|RE|RX001|DISP001||CM'
        rxe = 'RXE|1^BID^D2|314076^Lisinopril 10 mg PO^RXNORM||10|mg^milligram^UCUM'
        rxd = 'RXD|1|314076^Lisinopril 10 mg PO^RXNORM|20240517143000|1|TAB^Tablet^HL70505||RX001'
        rxr = 'RXR|PO^Oral^HL70162'

        bundle = convert(msh, PID, orc, rxe, rxd, rxr)
        dispense = one_resource(bundle, 'MedicationDispense')

        # The dispense is always a completed one - RDS reports what already happened.
        assert dispense['status'] == 'completed'

        # RXD-2 is the dispensed medication ..
        assert dispense['medicationCodeableConcept'] == {
            'coding': [{
                'system': 'http://www.nlm.nih.gov/research/umls/rxnorm',
                'code': '314076',
                'display': 'Lisinopril 10 mg PO',
            }],
            'text': 'Lisinopril 10 mg PO',
        }

        # .. RXD-3 is the handover time ..
        assert dispense['whenHandedOver'] == '2024-05-17T14:30:00+00:00'

        # .. RXD-4 and RXD-5 make the quantity ..
        quantity = dispense['quantity']
        assert quantity['value'] == 1
        assert quantity['unit'] == 'Tablet'

        # .. RXD-7 is the prescription number - the ORC order numbers went
        # .. to the MedicationRequest the preceding RXE became ..
        assert dispense['identifier'] == [{'value': 'RX001'}]

        medication_request = one_resource(bundle, 'MedicationRequest')
        assert medication_request['identifier'] == [{'value': 'RX001'}, {'value': 'DISP001'}]

        # .. and the trailing RXR routes the dispense.
        instruction = dispense['dosageInstruction'][0]
        assert instruction['route']['coding'][0]['code'] == 'PO'

# ################################################################################################################################

    def test_dispense_without_medication_code(self) -> 'None':

        # A dispense with an empty RXD-2 still carries the required medication element.
        msh = 'MSH|^~\\&|PHARM|HOSP|EHR|HOSPFAC|20240517143055||RDS^O13|MSG00009|P|2.5'
        rxd = 'RXD|1||20240517143000|1|TAB^Tablet^HL70505'

        bundle = convert(msh, PID, rxd)
        dispense = one_resource(bundle, 'MedicationDispense')

        medication = dispense['medicationCodeableConcept']
        extensions = medication['extension']
        extension = extensions[0]

        assert extension['url'] == 'http://hl7.org/fhir/StructureDefinition/data-absent-reason'
        assert extension['valueCode'] == 'unknown'

# ################################################################################################################################
# ################################################################################################################################

class TestMDMDocument:
    """ MDM messages become DocumentReference resources.
    """

    def test_document_gathers_obx_text(self) -> 'None':
        msh = 'MSH|^~\\&|TRANS|TRANSFAC|EHR|EHRFAC|20240517143055||MDM^T02|MSG00006|P|2.5'
        evn = 'EVN|T02|20240517143055'
        txa = 'TXA|1|CN^Consultation note^HL70270||||||||||DOC-1^TRANS'
        obx_first = 'OBX|1|TX|BODY^Document body||The visit went very well.||||||F'
        obx_second = 'OBX|2|TX|BODY^Document body||All questions were answered.||||||F'

        bundle = convert(msh, PID, evn, txa, obx_first, obx_second)
        document = one_resource(bundle, 'DocumentReference')

        assert document['status'] == 'current'

        document_type = document['type']
        type_codings = document_type['coding']
        type_coding = type_codings[0]

        assert type_coding['code'] == 'CN'

        master_identifier = document['masterIdentifier']
        assert master_identifier['value'] == 'DOC-1'

        # The OBX lines came together as the document body.
        contents = document['content']
        content = contents[0]
        attachment = content['attachment']

        assert attachment['contentType'] == 'text/plain'

        decoded_bytes = b64decode(attachment['data'])
        decoded = decoded_bytes.decode('utf8')

        assert decoded == 'The visit went very well.\nAll questions were answered.'

        # The text OBX segments carried the document, not observations.
        observations = resources_of_type(bundle, 'Observation')
        assert observations == []

# ################################################################################################################################

    def test_document_text_decodes_escapes(self) -> 'None':
        # Formatting escapes in the document body become the characters they stand for.
        msh = 'MSH|^~\\&|TRANS|TRANSFAC|EHR|EHRFAC|20240517143055||MDM^T02|MSG00016|P|2.5'
        evn = 'EVN|T02|20240517143055'
        txa = 'TXA|1|CN^Consultation note^HL70270||||||||||DOC-9^TRANS'
        obx = r'OBX|1|FT|BODY^Document body||First paragraph.\.br\\.br\Second paragraph.||||||F'

        bundle = convert(msh, PID, evn, txa, obx)
        document = one_resource(bundle, 'DocumentReference')

        contents = document['content']
        content = contents[0]
        attachment = content['attachment']

        decoded_bytes = b64decode(attachment['data'])
        decoded = decoded_bytes.decode('utf8')

        assert decoded == 'First paragraph.\n\nSecond paragraph.'

# ################################################################################################################################

    def test_obx_attachment_survives_document_text(self) -> 'None':
        # An ED attachment and TX body lines in one MDM - the attachment keeps its
        # data and the text becomes a content entry of its own.
        msh = 'MSH|^~\\&|TRANS|TRANSFAC|EHR|EHRFAC|20240517143055||MDM^T02|MSG00007|P|2.5'
        evn = 'EVN|T02|20240517143055'
        txa = 'TXA|1|CN^Consultation note^HL70270||||||||||DOC-2^TRANS'
        obx_image = 'OBX|1|ED|IMG^Scan image||^image^jpeg^Base64^/9j/AAAA||||||F'
        obx_text = 'OBX|2|TX|BODY^Document body||Findings were unremarkable.||||||F'

        bundle = convert(msh, PID, evn, txa, obx_image, obx_text)
        document = one_resource(bundle, 'DocumentReference')

        contents = document['content']

        image_content = contents[0]
        text_content = contents[1]

        image_attachment = image_content['attachment']
        text_attachment = text_content['attachment']

        assert image_attachment['contentType'] == 'image/jpeg'
        assert image_attachment['data'] == '/9j/AAAA'
        assert image_attachment['title'] == 'Scan image'

        assert text_attachment['contentType'] == 'text/plain'

        decoded_bytes = b64decode(text_attachment['data'])
        decoded = decoded_bytes.decode('utf8')

        assert decoded == 'Findings were unremarkable.'

# ################################################################################################################################

    def test_titled_attachment_keeps_the_file_name(self) -> 'None':
        # TXA-16 names the document file and the OBX attachment brings its own
        # title - both survive as separate content entries.
        msh = 'MSH|^~\\&|TRANS|TRANSFAC|EHR|EHRFAC|20240517143055||MDM^T02|MSG00008|P|2.5'
        evn = 'EVN|T02|20240517143055'
        txa = 'TXA|1|CN^Consultation note^HL70270||||||||||DOC-3^TRANS||||report.rtf'
        obx_image = 'OBX|1|ED|IMG^Scan image||^image^jpeg^Base64^/9j/BBBB||||||F'
        obx_text = 'OBX|2|TX|BODY^Document body||All clear.||||||F'

        bundle = convert(msh, PID, evn, txa, obx_image, obx_text)
        document = one_resource(bundle, 'DocumentReference')

        contents = document['content']

        text_content = contents[0]
        image_content = contents[1]

        text_attachment = text_content['attachment']
        image_attachment = image_content['attachment']

        # The placeholder kept its file name and received the document text.
        assert text_attachment['title'] == 'report.rtf'
        assert text_attachment['contentType'] == 'text/plain'

        decoded_bytes = b64decode(text_attachment['data'])
        decoded = decoded_bytes.decode('utf8')

        assert decoded == 'All clear.'

        assert image_attachment['title'] == 'Scan image'
        assert image_attachment['data'] == '/9j/BBBB'

# ################################################################################################################################

    def test_ig_mdm_t02(self) -> 'None':
        bundle = convert_fixture('MDM_T02.hl7')
        document = one_resource(bundle, 'DocumentReference')

        contents = document['content']
        content = contents[0]
        attachment = content['attachment']

        # The document body arrived from the message's OBX segments.
        assert 'data' in attachment

# ################################################################################################################################
# ################################################################################################################################

class TestZSegments:
    """ Z segments are preserved as Basic resources.
    """

    def test_z_segment_becomes_basic_resource(self) -> 'None':
        zpd = 'ZPD|GOLD|12345|Preferred customer'

        bundle = convert(MSH_ADT, PID, zpd)
        basic = one_resource(bundle, 'Basic')

        # The resource says which segment it preserves.
        code = basic['code']
        code_codings = code['coding']
        code_coding = code_codings[0]

        assert code_coding == {'system': 'urn:zato:hl7v2:extension/segment', 'code': 'ZPD'}

        # Every populated field became one extension, named after its position.
        extensions = basic['extension']

        assert extensions == [
            {'url': 'urn:zato:hl7v2:extension/ZPD/1', 'valueString': 'GOLD'},
            {'url': 'urn:zato:hl7v2:extension/ZPD/2', 'valueString': '12345'},
            {'url': 'urn:zato:hl7v2:extension/ZPD/3', 'valueString': 'Preferred customer'},
        ]

        # The preserved data belongs to the patient from the same message.
        subject = basic['subject']
        subject_url = subject['reference']

        assert subject_url.startswith('urn:uuid:')

# ################################################################################################################################

    def test_z_segment_keeps_components(self) -> 'None':
        zpd = 'ZPD|GOLD^LEVEL&2~SILVER'

        bundle = convert(MSH_ADT, PID, zpd)
        basic = one_resource(bundle, 'Basic')

        # Components, subcomponents and repetitions survive in wire form.
        extensions = basic['extension']
        extension = extensions[0]

        assert extension['valueString'] == 'GOLD^LEVEL&2~SILVER'

# ################################################################################################################################

    def test_empty_z_segment_is_skipped(self) -> 'None':
        zpd = 'ZPD|'

        bundle = convert(MSH_ADT, PID, zpd)

        basics = resources_of_type(bundle, 'Basic')
        assert basics == []

# ################################################################################################################################
# ################################################################################################################################
