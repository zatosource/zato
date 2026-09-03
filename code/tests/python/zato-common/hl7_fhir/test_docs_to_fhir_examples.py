# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from http.client import OK
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.test.fhir import FHIRTestServer
from zato.fhir import validate
from zato.hl7.mappings import get_conversion_warnings
from zato.hl7v2 import parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    anylist = anylist
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The Patient's fullUrl every page shows for the SMITH^JOHN^A patient with MRN 12345 from HOSP.
Smith_Patient_URL = 'urn:uuid:98e4f8aa-a5ad-5791-add1-66fd3afb4f83'

# The base URL the pages show in their default extension URLs.
Default_Base_URL = 'urn:zato:hl7v2:extension'

# The system of the UCUM units the resources page example carries.
UCUM_System = 'http://unitsofmeasure.org'

# The system of the bundle's processing-mode tag the config page shows.
Processing_ID_System = 'http://terminology.hl7.org/CodeSystem/v2-0103'

# The extension the codes page names for required elements with no value.
Data_Absent_Reason_URL = 'http://hl7.org/fhir/StructureDefinition/data-absent-reason'

# ################################################################################################################################
# ################################################################################################################################

def _resource_types(bundle:'any_') -> 'anylist':
    """ Returns the resource types of a bundle's entries, the way every page prints them.
    """
    out = []

    for entry in bundle.entry:
        out.append(entry.resource.resource_type)

    return out

# ################################################################################################################################

def _resources_of_type(bundle:'any_', resource_type:'str') -> 'anylist':
    """ Returns the resource dicts of one type from a bundle, in entry order.
    """
    out = []

    for entry in bundle.to_dict()['entry']:
        resource = entry['resource']
        if resource['resourceType'] == resource_type:
            out.append(resource)

    return out

# ################################################################################################################################

def _one_resource(bundle:'any_', resource_type:'str') -> 'stranydict':
    """ Returns the only resource of one type from a bundle.
    """
    resources = _resources_of_type(bundle, resource_type)
    assert len(resources) == 1, f'Expected one {resource_type}, found {len(resources)}'

    out = resources[0]
    return out

# ################################################################################################################################

def _write_config(tmp_path:'any_', contents:'str', file_name:'str') -> 'str':
    """ Writes an .ini file into the test's temporary directory and returns its path.
    """
    file_path = os.path.join(tmp_path, file_name)

    with open(file_path, 'w') as file_object:
        _ = file_object.write(contents)

    return file_path

# ################################################################################################################################

def _post_bundle(server:'FHIRTestServer', bundle_dict:'stranydict') -> 'stranydict':
    """ Posts a bundle to the server's base URL, the way the sending page's service does.
    """
    body = json.dumps(bundle_dict)
    body_bytes = body.encode('utf8')

    request = Request(server.address, data=body_bytes, headers={'Content-Type': 'application/fhir+json'})

    with urlopen(request) as response:
        assert response.status == OK
        out = json.loads(response.read())

    return out

# ################################################################################################################################

@pytest.fixture
def fhir_server():
    """ A fresh FHIR test server per test, so tests never see each other's data.
    """
    server = FHIRTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestIndexPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/index.
    """

    def test_what_comes_out_of_a_message(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'EVN|A01|20260315\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M|||123 MAIN ST^^BOSTON^MA^02101\r'
            'NK1|1|SMITH^JANE|SPO\r'
            'PV1|1|I|WARD^101^BED1|||||1234^JONES^MARIA|||||||||||V001\r'
            'AL1|1|DA|70618^Penicillin|SV\r'
            'DG1|1||I10^Essential hypertension^I10|||A\r'
        )

        msg = parse_hl7(raw, validate=False)
        bundle = msg.to_fhir()

        assert _resource_types(bundle) == [
            'MessageHeader',
            'Organization',
            'Organization',
            'Patient',
            'RelatedPerson',
            'Location',
            'Location',
            'Location',
            'Practitioner',
            'Encounter',
            'AllergyIntolerance',
            'Condition',
        ]

        # The two Organizations are the sending and receiving facilities from MSH-4 and MSH-6 ..
        organizations = _resources_of_type(bundle, 'Organization')
        assert organizations[0]['name'] == 'FACILITY'
        assert organizations[1]['name'] == 'FAC'

        # .. and the three Locations are the ward, the room and the bed, each part of the previous one.
        locations = _resources_of_type(bundle, 'Location')
        assert locations[0]['name'] == 'WARD'
        assert locations[1]['name'] == '101'
        assert locations[2]['name'] == 'BED1'

        assert 'partOf' not in locations[0]
        assert 'partOf' in locations[1]
        assert 'partOf' in locations[2]

    def test_dict_and_json_output(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
        )
        msg = parse_hl7(raw, validate=False)

        data = msg.to_fhir_dict()
        text = msg.to_fhir_json()

        assert data['resourceType'] == 'Bundle'
        assert json.loads(text) == data

        # Pretty-printed JSON
        text = msg.to_fhir_json(indent=2)
        assert '\n  "' in text
        assert json.loads(text) == data

    def test_validation_before_sending(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I|WARD^101^BED1|||||1234^JONES^MARIA\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()

        for entry in bundle.entry:
            result = validate(entry.resource)
            assert result.is_valid, result.errors

# ################################################################################################################################
# ################################################################################################################################

class TestResourcesPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/resources.
    """

    def test_oru_r01_example(self):

        raw = (
            'MSH|^~\\&|LAB|FACILITY|EHR|FAC|20260315101112||ORU^R01^ORU_R01|CTL002|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'ORC|RE|PLACER001|FILLER001\r'
            'OBR|1|PLACER001|FILLER001|24331-1^Lipid panel^LN|||202603150930||||||||||||||||||F\r'
            'OBX|1|NM|2093-3^Cholesterol^LN||187|mg/dL^^UCUM|<200|N|||F\r'
            'NTE|1||Fasting sample\r'
            'OBX|2|NM|2085-9^HDL cholesterol^LN||62|mg/dL^^UCUM|>40|N|||F\r'
            'OBX|3|NM|2571-8^Triglycerides^LN||145|mg/dL^^UCUM|<150|N|||F\r'
            'SPM|1|SPM001||SER^Serum\r'
        )

        msg = parse_hl7(raw, validate=False)
        bundle = msg.to_fhir()

        assert _resource_types(bundle) == [
            'MessageHeader',
            'Organization',
            'Organization',
            'Patient',
            'ServiceRequest',
            'DiagnosticReport',
            'Observation',
            'Observation',
            'Observation',
            'Specimen',
        ]

        # Each Observation has a valueQuantity - 187, 62 and 145 mg/dL ..
        observations = _resources_of_type(bundle, 'Observation')

        values = []
        for observation in observations:
            quantity = observation['valueQuantity']
            values.append(quantity['value'])

            assert quantity['unit'] == 'mg/dL'
            assert quantity['code'] == 'mg/dL'
            assert quantity['system'] == UCUM_System

        assert values == [187, 62, 145]

        # .. and the NTE comment is stored in the first one's note.
        assert observations[0]['note'] == [{'text': 'Fasting sample'}]
        assert 'note' not in observations[1]
        assert 'note' not in observations[2]

        # The DiagnosticReport is final from OBR-25, lists all three Observations in result and the Specimen in specimen ..
        report = _one_resource(bundle, 'DiagnosticReport')
        assert report['status'] == 'final'
        assert len(report['result']) == 3
        assert len(report['specimen']) == 1

        # .. and everything points back at the Patient.
        assert report['subject'] == {'reference': Smith_Patient_URL}
        for observation in observations:
            assert observation['subject'] == {'reference': Smith_Patient_URL}

        # Nothing was left out.
        assert get_conversion_warnings(bundle) == []

    def test_observation_values(self):

        header = (
            'MSH|^~\\&|LAB|FACILITY|EHR|FAC|20260315101112||ORU^R01^ORU_R01|CTL002|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
        )

        raw = header + (
            'OBX|1|NM|A^B^L||187|mg/dL^^UCUM||||||F\r'
            'OBX|2|NM|A^B^L||187|mg/dL||||||F\r'
            'OBX|3|ST|A^B^L||Free text||||||F\r'
            'OBX|4|CWE|A^B^L||POS^Positive^L||||||F\r'
            'OBX|5|SN|A^B^L||<^5||||||F\r'
            'OBX|6|DTM|A^B^L||20260315101112||||||F\r'
            'OBX|7|TM|A^B^L||1011||||||F\r'
            'OBX|8|ED|A^B^L||^AP^PDF^Base64^JVBERi0x||||||F\r'
            'OBX|9|RP|A^B^L||http://example.org/img/1^^IM^JPEG||||||F\r'
            'OBX|10|XX|A^B^L||whatever||||||F\r'
            'OBX|11|MO|A^B^L||12^USD||||||F\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()
        observations = _resources_of_type(bundle, 'Observation')

        # NM - valueQuantity, with units from OBX-6, system and code only when OBX-6 names a coding system
        assert observations[0]['valueQuantity'] == {'value': 187, 'unit': 'mg/dL', 'code': 'mg/dL', 'system': UCUM_System}
        assert observations[1]['valueQuantity'] == {'value': 187, 'unit': 'mg/dL'}

        # ST - valueString
        assert observations[2]['valueString'] == 'Free text'

        # CWE - valueCodeableConcept
        concept = observations[3]['valueCodeableConcept']
        assert concept['coding'][0]['code'] == 'POS'

        # SN - a comparator makes it a valueQuantity
        assert observations[4]['valueQuantity'] == {'value': 5, 'comparator': '<'}

        # DTM - valueDateTime
        assert observations[5]['valueDateTime'] == '2026-03-15T10:11:12+00:00'

        # TM - valueTime
        assert observations[6]['valueTime'] == '10:11:00'

        # ED - an attachment extension
        extension = observations[7]['extension'][0]
        assert extension['url'] == f'{Default_Base_URL}/attachment'
        assert extension['valueAttachment'] == {'contentType': 'application/pdf', 'data': 'JVBERi0x'}

        # RP - valueString with the whole reference pointer
        assert observations[8]['valueString'] == 'http://example.org/img/1^^IM^JPEG'

        # An unrecognized value type arrives as valueString ..
        assert observations[9]['valueString'] == 'whatever'

        # .. a recognized one outside the table is preserved as unmapped OBX-2 and OBX-5.
        urls = []
        for extension in observations[10]['extension']:
            urls.append((extension['url'], extension['valueString']))

        assert urls == [
            (f'{Default_Base_URL}/unmapped/OBX-2', 'MO'),
            (f'{Default_Base_URL}/unmapped/OBX-5', '12^USD'),
        ]

    def test_standard_segments_without_a_parent_become_basic(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV2|||R51^Headache^I10\r'
            'RXR|PO^Oral\r'
            'UAC|X|Y\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()

        codes = []
        for basic in _resources_of_type(bundle, 'Basic'):
            codes.append(basic['code']['coding'][0]['code'])

        assert codes == ['PV2', 'RXR', 'UAC']

# ################################################################################################################################
# ################################################################################################################################

class TestReferencesPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/references.
    """

    def test_every_entry_has_a_full_url(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I\r'
        )
        msg = parse_hl7(raw, validate=False)

        bundle_dict = msg.to_fhir_dict()

        patient_url = ''
        encounter_subject:'stranydict' = {}
        header_focus:'anylist' = []

        for entry in bundle_dict['entry']:
            assert entry['fullUrl'].startswith('urn:uuid:')

            resource = entry['resource']

            if resource['resourceType'] == 'Patient':
                patient_url = entry['fullUrl']

            if resource['resourceType'] == 'Encounter':
                encounter_subject = resource['subject']

            if resource['resourceType'] == 'MessageHeader':
                header_focus = resource['focus']

        # The Encounter's subject points at the Patient entry from the same bundle ..
        assert patient_url == Smith_Patient_URL
        assert encounter_subject == {'reference': Smith_Patient_URL}

        # .. and the MessageHeader's focus points at the Patient and the Encounter.
        assert len(header_focus) == 2
        assert header_focus[0] == {'reference': Smith_Patient_URL}

        # The UUIDs are deterministic - converting the same message twice yields the same URLs.
        assert msg.to_fhir_dict() == bundle_dict

        # The bundle carries the message's identity too.
        assert bundle_dict['identifier'] == {'system': 'urn:zato:hl7v2:message-control-id', 'value': 'CTL001'}
        assert bundle_dict['timestamp'] == '2026-03-15T10:11:12+00:00'
        assert bundle_dict['meta'] == {'tag': [{'system': Processing_ID_System, 'code': 'P'}]}

    def test_deduplication(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'

            # The same doctor is both the attending and the referring physician ..
            'PV1|1|I|WARD^101^BED1||||1234^JONES^MARIA|1234^JONES^MARIA\r'
        )

        msg = parse_hl7(raw, validate=False)
        bundle = msg.to_fhir()

        # .. yet the bundle contains a single Practitioner.
        assert _resource_types(bundle) == [
            'MessageHeader',
            'Organization',
            'Organization',
            'Patient',
            'Location',
            'Location',
            'Location',
            'Practitioner',
            'Encounter',
        ]

        # Both Encounter.participant entries point at the one Practitioner.
        practitioner_url = None
        for entry in bundle.to_dict()['entry']:
            if entry['resource']['resourceType'] == 'Practitioner':
                practitioner_url = entry['fullUrl']

        encounter = _one_resource(bundle, 'Encounter')
        participants = encounter['participant']

        assert len(participants) == 2
        for participant in participants:
            assert participant['individual'] == {'reference': practitioner_url}

        # The three Locations are the ward, the room and the bed, each partOf the one before it.
        location_urls = []
        for entry in bundle.to_dict()['entry']:
            if entry['resource']['resourceType'] == 'Location':
                location_urls.append(entry['fullUrl'])

        locations = _resources_of_type(bundle, 'Location')
        assert locations[1]['partOf'] == {'reference': location_urls[0]}
        assert locations[2]['partOf'] == {'reference': location_urls[1]}

    def test_what_bundle_type_changes(self, tmp_path:'any_'):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I\r'
        )
        msg = parse_hl7(raw, validate=False)

        # By default the bundle is a transaction and each entry has a request with POST and the resource type as the URL ..
        default_dict = msg.to_fhir_dict()
        assert default_dict['type'] == 'transaction'

        for entry in default_dict['entry']:
            assert entry['request'] == {'method': 'POST', 'url': entry['resource']['resourceType']}

        # .. batch keeps the same entries ..
        batch_path = _write_config(tmp_path, '[bundle]\ntype=batch\n', 'batch.ini')
        batch_dict = msg.to_fhir_dict(config=batch_path)
        assert batch_dict['type'] == 'batch'

        for entry in batch_dict['entry']:
            assert entry['request'] == {'method': 'POST', 'url': entry['resource']['resourceType']}

        # .. collection and message have no request elements at all, and message opens with the MessageHeader.
        for bundle_type in ('collection', 'message'):
            file_path = _write_config(tmp_path, f'[bundle]\ntype={bundle_type}\n', f'{bundle_type}.ini')
            bundle_dict = msg.to_fhir_dict(config=file_path)
            assert bundle_dict['type'] == bundle_type

            for entry in bundle_dict['entry']:
                assert 'request' not in entry

            first_entry = bundle_dict['entry'][0]
            assert first_entry['resource']['resourceType'] == 'MessageHeader'

            # In all four cases the fullUrl values stay the same.
            for default_entry, entry in zip(default_dict['entry'], bundle_dict['entry']):
                assert entry['fullUrl'] == default_entry['fullUrl']

# ################################################################################################################################
# ################################################################################################################################

class TestConfigPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/config.
    """

    # The demo file the page shows, the same one create_server.py ships as hl7-fhir-demo.ini
    demo_config = """
[bundle]
type=transaction

[datetime]
default_timezone=+00:00

[identifiers]

[[patient_mrn]]
authority=MYHOSP
system=http://example.org/mrn

[[visit_number]]
authority=MYVISITS
system=http://example.org/visit

[codes]

[[patient_class]]
P=AMB

[extensions]
base_url=http://example.org/fhir/ext
"""

    def test_demo_file_loads(self, tmp_path:'any_'):

        file_path = _write_config(tmp_path, self.demo_config, 'hl7-fhir-demo.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^MYHOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|P\r'
            'ZPD|GOLD\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        patient = _one_resource(bundle, 'Patient')
        assert patient['identifier'][0]['system'] == 'http://example.org/mrn'

        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['class'] == {'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode', 'code': 'AMB'}

        basic = _one_resource(bundle, 'Basic')
        assert basic['extension'][0]['url'] == 'http://example.org/fhir/ext/ZPD/1'

    def test_bundle_identity(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
        )
        bundle_dict = parse_hl7(raw, validate=False).to_fhir_dict()

        assert bundle_dict['resourceType'] == 'Bundle'
        assert bundle_dict['type'] == 'transaction'
        assert bundle_dict['identifier'] == {'system': 'urn:zato:hl7v2:message-control-id', 'value': 'CTL001'}
        assert bundle_dict['timestamp'] == '2026-03-15T10:11:12+00:00'
        assert bundle_dict['meta'] == {'tag': [{'system': Processing_ID_System, 'code': 'P'}]}

    def test_default_timezone(self, tmp_path:'any_'):

        file_path = _write_config(tmp_path, '[datetime]\ndefault_timezone=+02:00\n', 'timezone.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I||||||||||||||||||||||||||||||||||||||||||20260315101112+0100|20260315120000\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        # A timestamp's own offset wins, one without gets default_timezone, a date-only value gets no offset at all.
        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['period'] == {'start': '2026-03-15T10:11:12+01:00', 'end': '2026-03-15T12:00:00+02:00'}

        patient = _one_resource(bundle, 'Patient')
        assert patient['birthDate'] == '1980-01-15'

    def test_identifiers(self, tmp_path:'any_'):

        contents = """
[identifiers]

[[patient_mrn]]
authority=MYHOSP
system=http://example.org/mrn
"""
        file_path = _write_config(tmp_path, contents, 'identifiers.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^MYHOSP^MR~67890^^^OTHER^MR||SMITH^JOHN^A||19800115|M\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        patient = _one_resource(bundle, 'Patient')
        identifiers = patient['identifier']

        assert identifiers[0] == {
            'value': '12345',
            'system': 'http://example.org/mrn',
            'type': {
                'coding': [
                    {
                        'system': 'http://terminology.hl7.org/CodeSystem/v2-0203',
                        'code': 'MR',
                    }
                ]
            },
        }

        # An authority the file does not mention falls back to the urn:zato:hl7v2:authority placeholder.
        assert identifiers[1]['system'] == 'urn:zato:hl7v2:authority:OTHER'

    def test_strict_validation(self, tmp_path:'any_'):

        cases = [
            ('[bundles]\ntype=transaction\n', 'Unknown section `[bundles]`'),
            ('[bundle]\ntype=envelope\n', 'Unknown bundle type `envelope`'),
            ('[bundle]\nkind=transaction\n', 'Unknown key `kind`'),
            ('[identifiers]\n\n[[mrn]]\nauthority=MYHOSP\n', 'Missing key `system`'),
            ('[codes]\n\n[[patient_classes]]\nP=AMB\n', 'Unknown map `[[patient_classes]]`'),
            ('[codes]\n\n[[patient_class]]\nP=AMBU\n', 'targets unknown code `AMBU`'),
            ('[datetime]\ndefault_timezone=CET\n', 'Invalid default_timezone `CET`'),
            ('[extensions]\nbase_url=not a url\n', 'Invalid base_url `not a url`'),
        ]

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
        )
        msg = parse_hl7(raw, validate=False)

        for idx, (contents, expected) in enumerate(cases):
            file_path = _write_config(tmp_path, contents, f'invalid-{idx}.ini')

            with pytest.raises(Exception) as ctx:
                _ = msg.to_fhir(config=file_path)

            assert expected in str(ctx.value)
            assert file_path in str(ctx.value)

# ################################################################################################################################
# ################################################################################################################################

class TestCodesPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/codes.
    """

    def test_overriding_and_adding_codes(self, tmp_path:'any_'):

        contents = """
[codes]

# PV1-2 - P is our local code for ambulatory
[[patient_class]]
P=AMB

# PID-8 - map our local code D to unknown
[[administrative_sex]]
D=unknown
"""
        file_path = _write_config(tmp_path, contents, 'my-mappings.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|D\r'
            'PV1|1|P\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['class'] == {
            'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
            'code': 'AMB',
        }

        patient = _one_resource(bundle, 'Patient')
        assert patient['gender'] == 'unknown'

        # All other codes in the map keep their standard translations.
        raw = raw.replace('PV1|1|P', 'PV1|1|I')
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['class']['code'] == 'IMP'

    def test_system_and_code_overrides(self, tmp_path:'any_'):

        contents = """
[codes]

[[patient_class]]
P=http://terminology.hl7.org/CodeSystem/v3-ActCode|AMB
X=http://example.org/local-classes|XRAY
"""
        file_path = _write_config(tmp_path, contents, 'system-code.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|X\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['class'] == {'system': 'http://example.org/local-classes', 'code': 'XRAY'}

    def test_unknown_codes(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'

            # PID-8 contains X, which is not a standard administrative sex code ..
            'PID|||12345^^^HOSP^MR||SMITH^JOHN||19800115|X\r'

            # .. and neither is Q a standard patient class in PV1-2.
            'PV1|1|Q\r'
        )

        msg = parse_hl7(raw, validate=False)
        bundle = msg.to_fhir()

        printed = []

        for entry in bundle.entry:
            resource = entry.resource.to_dict()
            if 'extension' in resource:
                for item in resource['extension']:
                    printed.append(f'{item["url"]} -> {item["valueString"]}')

        assert printed == [
            f'{Default_Base_URL}/unmapped/PID-8 -> X',
            f'{Default_Base_URL}/unmapped/PV1-2 -> Q',
        ]

        # Optional elements are left unset, required ones get the code their value set reserves for this.
        patient = _one_resource(bundle, 'Patient')
        assert 'gender' not in patient

        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['class'] == {'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'code': 'UNK'}

        # Unknown codes and unmapped fields are preserved, so they never produce a warning.
        assert get_conversion_warnings(bundle) == []

    def test_required_elements_carry_data_absent_reason(self):

        absent = {'extension': [{'url': Data_Absent_Reason_URL, 'valueCode': 'unknown'}]}

        # A MedicationRequest whose RXO-1 is empty ..
        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||OMP^O09^OMP_O09|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'ORC|NW\r'
            'RXO||10||mg\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()
        request = _one_resource(bundle, 'MedicationRequest')
        assert request['medicationCodeableConcept'] == absent

        # .. a Coverage whose IN1 names no payor ..
        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'IN1|1|PLAN1\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()
        coverage = _one_resource(bundle, 'Coverage')
        assert coverage['payor'] == [absent]

        # .. an Immunization with no RXA-5.
        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||VXU^V04^VXU_V04|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'ORC|RE\r'
            'RXA|0|1|20260315\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()
        immunization = _one_resource(bundle, 'Immunization')
        assert immunization['vaccineCode'] == absent

    def test_verifying_a_conversion_is_complete(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'

            # A birth date of February 30th ..
            'PID|||12345^^^HOSP^MR||SMITH^JOHN||19800230|M\r'

            # .. and a discharge time with an hour of 25 in PV1-45.
            'PV1|1|I|||||||||||||||||||||||||||||||||||||||||||20260315251500\r'
        )

        msg = parse_hl7(raw, validate=False)
        bundle = msg.to_fhir()

        assert get_conversion_warnings(bundle) == [
            'PID-7: `19800230` is not a valid date',
            'PV1-45: `20260315251500` is not a valid date/time',
        ]

        # A number with more digits than a float can hold keeps its digits in an extension and is named too.
        raw = (
            'MSH|^~\\&|LAB|FACILITY|EHR|FAC|20260315101112||ORU^R01^ORU_R01|CTL002|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'OBX|1|NM|2093-3^Cholesterol^LN||0.12345678901234567890123||||||F\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()

        observation = _one_resource(bundle, 'Observation')
        assert observation['extension'] == [
            {'url': f'{Default_Base_URL}/unmapped/OBX-5', 'valueString': '0.12345678901234567890123'},
        ]

        warnings = get_conversion_warnings(bundle)
        assert len(warnings) == 1
        assert warnings[0].startswith('OBX-5: `0.12345678901234567890123` cannot be carried exactly as a number')

        # A clean message yields an empty list.
        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()

        warnings = get_conversion_warnings(bundle)
        assert warnings == []

# ################################################################################################################################
# ################################################################################################################################

class TestZSegmentsPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/z-segments.
    """

    def test_what_a_z_segment_becomes(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'

            # A custom segment with a membership level and a renewal year
            'ZPD|GOLD|2026\r'
        )

        msg = parse_hl7(raw, validate=False)
        bundle = msg.to_fhir()

        text = msg.to_fhir_json(indent=2)
        assert json.loads(text) == bundle.to_dict()

        basic = _one_resource(bundle, 'Basic')

        assert basic == {
            'resourceType': 'Basic',
            'code': {
                'coding': [
                    {
                        'system': f'{Default_Base_URL}/segment',
                        'code': 'ZPD',
                    }
                ]
            },
            'extension': [
                {
                    'url': f'{Default_Base_URL}/ZPD/1',
                    'valueString': 'GOLD',
                },
                {
                    'url': f'{Default_Base_URL}/ZPD/2',
                    'valueString': '2026',
                },
            ],
            'subject': {
                'reference': Smith_Patient_URL,
            },
        }

        # A Z-segment with no populated fields produces nothing ..
        raw = raw.replace('ZPD|GOLD|2026', 'ZPD')
        bundle = parse_hl7(raw, validate=False).to_fhir()
        assert _resources_of_type(bundle, 'Basic') == []

        # .. and field values keep their HL7 wire form.
        raw = raw.replace('ZPD', 'ZPD|A^B~C&D')
        bundle = parse_hl7(raw, validate=False).to_fhir()

        basic = _one_resource(bundle, 'Basic')
        assert basic['extension'] == [{'url': f'{Default_Base_URL}/ZPD/1', 'valueString': 'A^B~C&D'}]

    def test_setting_the_extension_base_url(self, tmp_path:'any_'):

        file_path = _write_config(tmp_path, '[extensions]\nbase_url=http://example.org/fhir/ext\n', 'base-url.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M||||MIDDLESEX\r'
            'ZPD|GOLD|2026\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir(config=file_path)

        basic = _one_resource(bundle, 'Basic')
        assert basic['code']['coding'][0]['system'] == 'http://example.org/fhir/ext/segment'
        assert basic['extension'][0]['url'] == 'http://example.org/fhir/ext/ZPD/1'

        # The unmapped URLs are built under the same base URL.
        patient = _one_resource(bundle, 'Patient')
        assert patient['extension'] == [
            {'url': 'http://example.org/fhir/ext/unmapped/PID-12', 'valueString': 'MIDDLESEX'},
        ]

    def test_unmapped_fields_of_standard_segments(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M||||MIDDLESEX\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()

        patient = _one_resource(bundle, 'Patient')
        assert patient['extension'] == [
            {'url': f'{Default_Base_URL}/unmapped/PID-12', 'valueString': 'MIDDLESEX'},
        ]

    def test_standard_segments_that_become_basic_too(self):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'UAC|X|Y\r'
            'DSC|ABC\r'
            'AIS|1|A|X^Y\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()

        codes = []
        for basic in _resources_of_type(bundle, 'Basic'):
            codes.append(basic['code']['coding'][0]['code'])

        assert codes == ['UAC', 'DSC', 'AIS']

        # ZBE and ZDS have mappings of their own when their parent is present.
        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I\r'
            'ZBE|MOV1^SYS|20260301||INSERT\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()
        assert _resources_of_type(bundle, 'Basic') == []

        encounter = _one_resource(bundle, 'Encounter')
        assert encounter['identifier'] == [{'value': 'MOV1', 'system': 'urn:zato:hl7v2:authority:SYS'}]

# ################################################################################################################################
# ################################################################################################################################

class TestSendingPage:
    """ Mirrors docs/dev/healthcare/hl7/to-fhir/sending.
    """

    def test_posting_a_bundle_and_what_the_server_sends_back(self, fhir_server:'FHIRTestServer'):

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
            'PV1|1|I\r'
        )
        bundle = parse_hl7(raw, validate=False).to_fhir()
        bundle_dict = bundle.to_dict()

        # Transaction bundles are posted to the server's root URL ..
        response = _post_bundle(fhir_server, bundle_dict)

        # .. and the server replies with a transaction-response bundle, one entry per posted resource, in the same order.
        assert response['type'] == 'transaction-response'
        assert len(response['entry']) == len(bundle_dict['entry'])

        locations = {}

        for request_entry, response_entry in zip(bundle_dict['entry'], response['entry']):
            entry_response = response_entry['response']
            assert entry_response['status'] == '201 Created'

            resource_type = request_entry['resource']['resourceType']
            location = entry_response['location'].split('/_history')[0]

            assert location.startswith(f'{resource_type}/')
            locations[resource_type] = location

        # The server assigned real IDs and rewrote the urn:uuid references - the stored Encounter's subject points at the Patient.
        with urlopen(f'{fhir_server.address}/{locations["Encounter"]}') as stored:
            encounter = json.loads(stored.read())

        assert encounter['subject'] == {'reference': locations['Patient']}

    def test_batch_reports_each_entry(self, fhir_server:'FHIRTestServer', tmp_path:'any_'):

        file_path = _write_config(tmp_path, '[bundle]\ntype=batch\n', 'batch.ini')

        raw = (
            'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FAC|20260315101112||ADT^A01^ADT_A01|CTL001|P|2.9\r'
            'PID|||12345^^^HOSP^MR||SMITH^JOHN^A||19800115|M\r'
        )
        bundle_dict = parse_hl7(raw, validate=False).to_fhir_dict(config=file_path)

        response = _post_bundle(fhir_server, bundle_dict)
        assert response['type'] == 'batch-response'

        # The response includes a per-entry status the service checks.
        rejected = []

        for entry in response['entry']:
            status = entry['response']['status']

            if not status.startswith('2'):
                rejected.append(entry['response'])

        assert rejected == []

# ################################################################################################################################
# ################################################################################################################################
