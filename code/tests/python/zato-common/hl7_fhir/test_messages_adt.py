# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# pytest
import pytest

# Zato
from zato.common.typing_ import cast_
from zato.hl7.mappings import get_conversion_warnings
from zato.hl7v2 import parse_hl7

# Local
from conftest import Samples_Dir, Test_Conversions_Dir, convert, list_messages, load_message, one_resource, \
    resources_of_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strintdict, stranydict
    any_ = any_
    anylist = anylist
    strintdict = strintdict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

def _count_types(bundle_dict:'stranydict') -> 'strintdict':
    """ Counts how many resources of each type a bundle dict carries.
    """
    out:'strintdict' = {}

    for entry in bundle_dict['entry']:
        resource = entry['resource']
        resource_type = resource['resourceType']

        if resource_type in out:
            out[resource_type] += 1
        else:
            out[resource_type] = 1

    return out

# ################################################################################################################################

def _convert_fixture(file_path:'str') -> 'any_':
    """ Parses one fixture message and converts it to a bundle.
    """
    raw = load_message(file_path)
    msg = parse_hl7(raw, validate=False)

    out = msg.to_fhir()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestIGTestConversion:
    """ The IG's agreed ADT_A01 message-to-Bundle pair, compared structurally.
    """

    def test_resource_types(self) -> 'None':
        fixture_path = os.path.join(Test_Conversions_Dir, 'ADT_A01.hl7')
        bundle = _convert_fixture(fixture_path)

        bundle_dict = bundle.to_dict()
        counts = _count_types(bundle_dict)

        assert counts['MessageHeader'] == 1
        assert counts['Patient'] == 1
        assert counts['Encounter'] == 1
        assert counts['Observation'] == 1
        assert counts['AllergyIntolerance'] == 1
        assert counts['Coverage'] == 1
        assert counts['RelatedPerson'] == 1

        assert bundle_dict['type'] == 'transaction'

# ################################################################################################################################

    def test_patient_matches_agreed_bundle(self) -> 'None':
        fixture_path = os.path.join(Test_Conversions_Dir, 'ADT_A01.hl7')
        bundle = _convert_fixture(fixture_path)

        our_patient = one_resource(bundle, 'Patient')

        # The agreed bundle the IG publishes for the same message.
        agreed_path = os.path.join(Test_Conversions_Dir, 'FHIR_bundle.hl7_ADT_A01.json')

        with open(agreed_path) as agreed_file:
            agreed_bundle = json.load(agreed_file)

        agreed_patient = None

        for entry in agreed_bundle['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                agreed_patient = resource

        agreed = cast_('any_', agreed_patient)

        assert our_patient['gender'] == agreed['gender']

        # The agreed birthDate carries a time part, ours is the date FHIR asks for.
        agreed_birth = agreed['birthDate']
        assert agreed_birth.startswith(our_patient['birthDate'])

        our_names = our_patient['name']
        agreed_names = agreed['name']

        our_first_name = our_names[0]
        agreed_first_name = agreed_names[0]

        assert our_first_name['family'] == agreed_first_name['family']
        assert our_first_name['given'] == agreed_first_name['given']
        assert our_first_name['use'] == agreed_first_name['use']

        our_maiden_name = our_names[1]
        agreed_maiden_name = agreed_names[1]

        assert our_maiden_name['family'] == agreed_maiden_name['family']
        assert our_maiden_name['use'] == agreed_maiden_name['use']

# ################################################################################################################################

    def test_encounter_matches_agreed_bundle(self) -> 'None':
        fixture_path = os.path.join(Test_Conversions_Dir, 'ADT_A01.hl7')
        bundle = _convert_fixture(fixture_path)

        encounter = one_resource(bundle, 'Encounter')

        # PV1-2 is E, an emergency encounter.
        encounter_class = encounter['class']
        assert encounter_class['code'] == 'EMER'

        subject = encounter['subject']
        subject_url = subject['reference']

        assert subject_url.startswith('urn:uuid:')

# ################################################################################################################################
# ################################################################################################################################

def _adt_sample_paths() -> 'anylist':
    """ All the ADT messages from the samples fixture tree.
    """
    out = []

    for file_path in list_messages(Samples_Dir):
        file_name = os.path.basename(file_path)
        if file_name.startswith('ADT'):
            out.append(file_path)

    return out

# ################################################################################################################################

_adt_paths = _adt_sample_paths()

# ################################################################################################################################

@pytest.mark.parametrize('file_path', _adt_paths, ids=os.path.basename)
def test_adt_samples_end_to_end(file_path:'any_') -> 'None':
    """ Every ADT sample converts to a bundle with a message header and a patient.
    """
    raw = load_message(file_path)
    msg = parse_hl7(raw, validate=False)

    bundle = msg.to_fhir()
    bundle_dict = bundle.to_dict()

    assert bundle_dict['type'] == 'transaction'

    counts = _count_types(bundle_dict)
    assert counts['MessageHeader'] == 1

    # Swap and merge messages carry two patients.
    active_patients = 0

    for entry in bundle_dict['entry']:
        resource = entry['resource']
        if resource['resourceType'] == 'Patient':
            if 'active' not in resource:
                active_patients += 1

    assert active_patients in (1, 2)

    for entry in bundle_dict['entry']:
        full_url = entry['fullUrl']
        assert full_url.startswith('urn:uuid:')

# ################################################################################################################################

def test_adt_samples_exist() -> 'None':
    """ The fixture tree holds at least 50 ADT samples.
    """
    sample_paths = _adt_sample_paths()
    assert len(sample_paths) >= 50

# ################################################################################################################################

def test_repeating_al1_makes_multiple_allergies() -> 'None':
    """ Repeating AL1 segments each become their own AllergyIntolerance.
    """
    msh = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
    pid = 'PID|1||12345||Smith^John|||M'
    al1_first = 'AL1|1|LA|1543^Pollen^RXNORM|MI|Sneezing'
    al1_second = 'AL1|2|FA|1191^Peanut^RXNORM|MO|Rash'

    joined = '\r'.join((msh, pid, al1_first, al1_second))
    raw = joined + '\r'
    msg = parse_hl7(raw, validate=False)

    bundle = msg.to_fhir()
    allergies = resources_of_type(bundle, 'AllergyIntolerance')

    assert len(allergies) == 2

    first_allergy = allergies[0]
    second_allergy = allergies[1]

    assert first_allergy['category'] == ['environment']
    assert second_allergy['category'] == ['food']

# ################################################################################################################################
# ################################################################################################################################

class TestMultiPatientMessages:
    """ Messages that carry more than one patient - each PID group keeps its own context.
    """

    def test_a17_swaps_two_patients_with_their_own_encounters(self) -> 'None':
        msh = 'MSH|^~\\&|ADT|HOSPFAC|EHR|EHRFAC|20240517143055||ADT^A17|MSG00070|P|2.5'
        pid_first = 'PID|1||111^^^MYHOSP^MR||Smith^John|||M'
        pv1_first = 'PV1|1|I|WARD1^101^A'
        pid_second = 'PID|2||222^^^MYHOSP^MR||Smith^Jane|||F'
        pv1_second = 'PV1|2|I|WARD2^202^B'

        bundle = convert(msh, pid_first, pv1_first, pid_second, pv1_second)

        patients = resources_of_type(bundle, 'Patient')
        encounters = resources_of_type(bundle, 'Encounter')

        assert len(patients) == 2
        assert len(encounters) == 2

        bundle_dict = bundle.to_dict()
        patient_urls = []

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_urls.append(entry['fullUrl'])

        assert encounters[0]['subject'] == {'reference': patient_urls[0]}
        assert encounters[1]['subject'] == {'reference': patient_urls[1]}

# ################################################################################################################################

    def test_a24_links_the_two_patients(self) -> 'None':
        msh = 'MSH|^~\\&|ADT|HOSPFAC|EHR|EHRFAC|20240517143055||ADT^A24|MSG00071|P|2.5'
        pid_first = 'PID|1||111^^^MYHOSP^MR||Smith^John|||M'
        pid_second = 'PID|2||222^^^MYHOSP^MR||Smith^Jane|||F'

        bundle = convert(msh, pid_first, pid_second)

        patients = resources_of_type(bundle, 'Patient')
        assert len(patients) == 2

        bundle_dict = bundle.to_dict()
        patient_urls = []

        for entry in bundle_dict['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                patient_urls.append(entry['fullUrl'])

        assert patients[0]['link'] == [{'other': {'reference': patient_urls[1]}, 'type': 'seealso'}]
        assert patients[1]['link'] == [{'other': {'reference': patient_urls[0]}, 'type': 'seealso'}]

# ################################################################################################################################

    def test_rsp_k22_keeps_each_patient_group_apart(self) -> 'None':
        msh = 'MSH|^~\\&|MPI|HIEFAC|EHR|EHRFAC|20240517143055||RSP^K22^RSP_K22|MSG00072|P|2.5'
        msa = 'MSA|AA|QRY00001'
        qak = 'QAK|QRY00001|OK'
        qpd = 'QPD|IHE PDQ Query|QRY00001|@PID.5.1.1^SMITH'
        pid_first = 'PID|1||111^^^MYHOSP^MR||Smith^Anna|||F'
        qri_first = 'QRI|95|MATCHWARE'
        pid_second = 'PID|2||222^^^MYHOSP^MR||Smith^Bruno|||M'
        qri_second = 'QRI|80|MATCHWARE'

        bundle = convert(msh, msa, qak, qpd, pid_first, qri_first, pid_second, qri_second)

        patients = resources_of_type(bundle, 'Patient')
        assert len(patients) == 2

        assert patients[0]['name'] == [{'family': 'Smith', 'given': ['Anna']}]
        assert patients[1]['name'] == [{'family': 'Smith', 'given': ['Bruno']}]

        assert 'link' not in patients[0]
        assert 'link' not in patients[1]

        # The query frames are preserved whole.
        basics = resources_of_type(bundle, 'Basic')

        preserved_segments = []
        for basic in basics:
            preserved_segments.append(basic['code']['coding'][0]['code'])

        assert preserved_segments == ['QAK', 'QPD', 'QRI', 'QRI']

# ################################################################################################################################

    def test_rcp_is_preserved_whole(self) -> 'None':
        msh = 'MSH|^~\\&|EHR|EHRFAC|MPI|HIEFAC|20240517143055||QBP^Q22^QBP_Q21|MSG00073|P|2.5'
        qpd = 'QPD|IHE PDQ Query|QRY00002|@PID.5.1.1^SMITH'
        rcp = 'RCP|I|10^RD'

        bundle = convert(msh, qpd, rcp)

        basics = resources_of_type(bundle, 'Basic')

        preserved_segments = []
        for basic in basics:
            preserved_segments.append(basic['code']['coding'][0]['code'])

        assert preserved_segments == ['QPD', 'RCP']

        rcp_basic = basics[1]
        extensions = rcp_basic['extension']

        assert {'url': 'urn:zato:hl7v2:extension/RCP/1', 'valueString': 'I'} in extensions
        assert {'url': 'urn:zato:hl7v2:extension/RCP/2', 'valueString': '10^RD'} in extensions

# ################################################################################################################################
# ################################################################################################################################

class TestVisitMoves:
    """ A45 and A50 move visits between records - the MRG keeps the prior numbers.
    """

    def test_a45_keeps_the_prior_visit_number(self) -> 'None':
        msh = 'MSH|^~\\&|ADT|HOSPFAC|EHR|EHRFAC|20240517143055||ADT^A45|MSG00076|P|2.5'
        pid = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'
        mrg = 'MRG|999^^^MYHOSP^MR||||VN-OLD-1^^^MYHOSP'
        pv1 = 'PV1|1|I|WARD1^101^A||||||||||||||||VN-NEW-1^^^MYHOSP'

        bundle = convert(msh, pid, mrg, pv1)

        patients = resources_of_type(bundle, 'Patient')
        assert len(patients) == 2

        # The surviving patient replaces the prior record ..
        surviving = patients[0]
        prior = patients[1]

        assert surviving['link'][0]['type'] == 'replaces'
        assert prior['active'] is False

        # .. and the prior visit number is preserved on that record.
        extensions = prior['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/MRG-5', 'valueString': 'VN-OLD-1^^^MYHOSP'} \
            in extensions

        encounter = one_resource(bundle, 'Encounter')
        identifiers = encounter['identifier']

        assert identifiers[0]['value'] == 'VN-NEW-1'

# ################################################################################################################################
# ################################################################################################################################

class TestPDADeathAdvice:
    """ PDA marks the patient as deceased and keeps everything it carries.
    """

    def test_pda_marks_the_patient_deceased(self) -> 'None':
        msh = 'MSH|^~\\&|ADT|HOSPFAC|EHR|EHRFAC|20240517143055||ADT^A03|MSG00074|P|2.5'
        pid = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'
        pda = 'PDA|I46.9^Cardiac arrest^I10|CUH^WARD8||20240517080000'

        bundle = convert(msh, pid, pda)
        patient = one_resource(bundle, 'Patient')

        assert patient['deceasedBoolean'] is True

        extensions = patient['extension']

        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PDA-1', 'valueString': 'I46.9^Cardiac arrest^I10'} \
            in extensions
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PDA-2', 'valueString': 'CUH^WARD8'} in extensions
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PDA-4', 'valueString': '20240517080000'} in extensions

# ################################################################################################################################

    def test_pid_death_time_takes_precedence(self) -> 'None':
        msh = 'MSH|^~\\&|ADT|HOSPFAC|EHR|EHRFAC|20240517143055||ADT^A03|MSG00075|P|2.5'
        pid = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M|||||||||||||||||||||20240517080000|Y'
        pda = 'PDA|I46.9^Cardiac arrest^I10'

        bundle = convert(msh, pid, pda)
        patient = one_resource(bundle, 'Patient')

        assert patient['deceasedDateTime'] == '2024-05-17T08:00:00+00:00'
        assert 'deceasedBoolean' not in patient

# ################################################################################################################################
# ################################################################################################################################

class TestUnknownStructures:
    """ ORR, OMI_Z01 and ADT_A18 convert from their raw segments.
    """

    def test_orr_o02_is_an_order_response(self) -> 'None':
        msh = 'MSH|^~\\&|LAB|LABFAC|EHR|EHRFAC|20240517143055||ORR^O02|MSG00080|P|2.5'
        msa = 'MSA|AA|MSG00003'
        orc = 'ORC|OK|ORD-1^EHR|FIL-1^LAB'
        obr = 'OBR|1|ORD-1^EHR|FIL-1^LAB|24331-1^Lipid panel^LN'

        bundle = convert(msh, msa, orc, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['code']['text'] == 'Lipid panel'
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_omi_z01_is_an_imaging_order(self) -> 'None':
        msh = 'MSH|^~\\&|PACS|HOSPFAC|RIS|RADFAC|20240517143055||OMI^Z01^OMI_Z01|MSG00081|P|2.5'
        orc = 'ORC|NW|IMG-Z1^RIS'
        obr = 'OBR|1|IMG-Z1^RIS||74178^CT Abdomen^C4'
        ipc = 'IPC|ACC-Z1^RIS|RP-Z1^RIS|1.2.40.0.34.1.1.201^RIS||CT^Computed Tomography^DCM'

        pid = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

        bundle = convert(msh, pid, orc, obr, ipc)
        service_request = one_resource(bundle, 'ServiceRequest')

        identifiers = service_request['identifier']
        assert {'system': 'urn:dicom:uid', 'value': 'urn:oid:1.2.40.0.34.1.1.201'} in identifiers

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_a18_merges_the_prior_patient(self) -> 'None':
        msh = 'MSH|^~\\&|ADT|HOSPFAC|EHR|EHRFAC|20240517143055||ADT^A18^ADT_A18|MSG00082|P|2.5'
        pid = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'
        mrg = 'MRG|999^^^MYHOSP^MR'

        bundle = convert(msh, pid, mrg)

        patients = resources_of_type(bundle, 'Patient')
        assert len(patients) == 2

        surviving = patients[0]
        prior = patients[1]

        assert surviving['link'][0]['type'] == 'replaces'
        assert prior['active'] is False

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
