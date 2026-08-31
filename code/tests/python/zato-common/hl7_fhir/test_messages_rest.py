# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from base64 import b64decode

# Zato
from zato.hl7v2 import parse_hl7

# Local
from conftest import Test_Conversions_Dir, convert, load_message, one_resource, organization_named, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

MSH_ADT = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
MSH_SIU = 'MSH|^~\\&|SCHED|SCHEDFAC|EHR|EHRFAC|20240517143055||SIU^S12|MSG00004|P|2.5'
MSH_VXU = 'MSH|^~\\&|EHR|EHRFAC|REGISTRY|REGFAC|20240517143055||VXU^V04|MSG00005|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

def _convert_fixture(file_name:'str') -> 'any_':
    """ Parses one test conversion fixture and converts it to a bundle.
    """
    file_path = os.path.join(Test_Conversions_Dir, file_name)

    raw = load_message(file_path)
    msg = parse_hl7(raw, validate=False)

    out = msg.to_fhir()
    return out

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

        reason_codes = appointment['reasonCode']
        reason = reason_codes[0]

        assert reason['text'] == 'Wellness checkup'

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
        location = one_resource(bundle, 'Location')

        practitioner_names = practitioner['name']
        practitioner_name = practitioner_names[0]

        assert practitioner_name['family'] == 'Welby'
        assert location['name'] == 'CLINIC-MAINFAC'

# ################################################################################################################################

    def test_ig_siu_s12(self) -> 'None':
        bundle = _convert_fixture('SIU_S12.hl7')
        appointment = one_resource(bundle, 'Appointment')

        assert appointment['status'] == 'booked'

        identifiers = appointment['identifier']
        assert len(identifiers) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestVXUImmunization:
    """ VXU messages become Immunization resources.
    """

    def test_immunization_core_fields(self) -> 'None':
        orc = 'ORC|RE||IMM-1^REGISTRY'
        rxa = 'RXA|0|1|20240517103000||08^Hepatitis B vaccine^CVX|0.5|mL^^UCUM|||1234^Welby^Marcus|||||LOT-9|20250101|GHC^Good Health Vaccines^MVX|||CP'
        rxr = 'RXR|IM^Intramuscular^HL70162|LD^Left deltoid^HL70163'

        bundle = convert(MSH_VXU, PID, orc, rxa, rxr)
        immunization = one_resource(bundle, 'Immunization')

        # CP means the immunization is complete.
        assert immunization['status'] == 'completed'

        vaccine_code = immunization['vaccineCode']
        vaccine_codings = vaccine_code['coding']
        vaccine_coding = vaccine_codings[0]

        assert vaccine_coding == {
            'code': '08',
            'display': 'Hepatitis B vaccine',
            'system': 'http://hl7.org/fhir/sid/cvx',
        }

        assert immunization['occurrenceDateTime'] == '2024-05-17T10:30:00+00:00'

        assert immunization['doseQuantity'] == {
            'value': 0.5,
            'code': 'mL',
            'system': 'http://unitsofmeasure.org',
            'unit': 'mL',
        }

        assert immunization['lotNumber'] == 'LOT-9'
        assert immunization['expirationDate'] == '2025-01-01'

        # The ORC filler number identifies the immunization.
        identifiers = immunization['identifier']
        identifier = identifiers[0]

        assert identifier['value'] == 'IMM-1'

        # The manufacturer became an Organization.
        organization = organization_named(bundle, 'Good Health Vaccines')
        assert organization['name'] == 'Good Health Vaccines'

        # The RXR route and site joined the immunization.
        route = immunization['route']
        route_codings = route['coding']
        route_coding = route_codings[0]

        assert route_coding['code'] == 'IM'

        site = immunization['site']
        site_codings = site['coding']
        site_coding = site_codings[0]

        assert site_coding['code'] == 'LD'

# ################################################################################################################################

    def test_ig_vxu_v04(self) -> 'None':
        bundle = _convert_fixture('VXU_V04.hl7')

        # The message carries three RXA groups.
        immunizations = resources_of_type(bundle, 'Immunization')
        assert len(immunizations) == 3

        # Each immunization belongs to the patient from the same bundle.
        bundle_dict = bundle.to_dict()
        patient_url = None

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_url = entry['fullUrl']

        for immunization in immunizations:
            patient_reference = immunization['patient']
            assert patient_reference == {'reference': patient_url}

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
        bundle = _convert_fixture('MDM_T02.hl7')
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
