# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, one_resource, organization_named

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every segment test builds on.
MSH = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John^Q|||M'

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

    def test_drivers_license_with_state_and_expiration(self) -> 'None':
        pid = 'PID|1||12345||Smith^John|||M||||||||||||D123456^IL^20261231'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        license_identifier = patient['identifier'][1]

        # The issuing state and the expiration date survive on the identifier itself.
        assert license_identifier['value'] == 'D123456'
        assert license_identifier['type']['coding'][0]['code'] == 'DL'
        assert license_identifier['assigner'] == {'display': 'IL'}
        assert license_identifier['period'] == {'end': '2026-12-31'}

# ################################################################################################################################

    def test_cx_shifted_into_drivers_license_slot(self) -> 'None':

        # Some senders shift a whole CX account identifier into PID-20 -
        # its assigning authority and type code mark it as one.
        pid = 'PID|1||12345||Smith^John|||M||||||||||||AN6271^^^MYHOSP&1.2.3.4&ISO^AN'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        shifted_identifier = patient['identifier'][1]

        assert shifted_identifier['value'] == 'AN6271'
        assert shifted_identifier['system'] == 'urn:oid:1.2.3.4'
        assert shifted_identifier['type']['coding'][0]['code'] == 'AN'

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

    def test_cdc_race_omb_category(self) -> 'None':
        pid = 'PID|1||12345||Smith^John|||M||2106-3^White^CDCREC'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        extensions = patient['extension']

        assert {
            'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
            'extension': [
                {'url': 'ombCategory', 'valueCoding': {
                    'system': 'urn:oid:2.16.840.1.113883.6.238', 'code': '2106-3', 'display': 'White'}},
                {'url': 'text', 'valueString': 'White'},
            ],
        } in extensions

# ################################################################################################################################

    def test_cdc_race_detailed_code(self) -> 'None':

        # A CDC code outside the OMB top-level categories goes to the detailed sub-extension.
        pid = 'PID|1||12345||Smith^John|||M||2131-1^Other Race^CDCREC'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        extensions = patient['extension']

        assert {
            'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
            'extension': [
                {'url': 'detailed', 'valueCoding': {
                    'system': 'urn:oid:2.16.840.1.113883.6.238', 'code': '2131-1', 'display': 'Other Race'}},
                {'url': 'text', 'valueString': 'Other Race'},
            ],
        } in extensions

# ################################################################################################################################

    def test_cdc_ethnicity(self) -> 'None':
        pid = 'PID|1||12345||Smith^John|||M||||||||||||||2186-5^Not Hispanic or Latino^CDCREC'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        extensions = patient['extension']

        assert {
            'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity',
            'extension': [
                {'url': 'ombCategory', 'valueCoding': {
                    'system': 'urn:oid:2.16.840.1.113883.6.238', 'code': '2186-5', 'display': 'Not Hispanic or Latino'}},
                {'url': 'text', 'valueString': 'Not Hispanic or Latino'},
            ],
        } in extensions

# ################################################################################################################################

    def test_non_cdc_race_stays_preserved(self) -> 'None':

        # A race from any other vocabulary never becomes a US Core extension.
        pid = 'PID|1||12345||Smith^John|||M||W1^White^LOCAL'

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        extensions = patient['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/PID-10',
            'valueString': 'W1^White^LOCAL',
        } in extensions

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
