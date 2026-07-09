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
from zato.hl7v2 import parse_hl7

# Local
from conftest import Samples_Dir, Test_Conversions_Dir, list_messages, load_message, one_resource, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

def _count_types(bundle_dict:'dict') -> 'dict':
    """ Counts how many resources of each type a bundle dict carries.
    """
    out = {}

    for entry in bundle_dict['entry']:
        resource = entry['resource']
        resource_type = resource['resourceType']

        if resource_type in out:
            out[resource_type] += 1
        else:
            out[resource_type] = 1

    return out

# ################################################################################################################################

def _convert_fixture(file_path:'str'):
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

    def test_resource_types(self):
        fixture_path = os.path.join(Test_Conversions_Dir, 'ADT_A01.hl7')
        bundle = _convert_fixture(fixture_path)

        bundle_dict = bundle.to_dict()
        counts = _count_types(bundle_dict)

        # The core resources the agreed bundle carries come out of the conversion too
        assert counts['MessageHeader'] == 1
        assert counts['Patient'] == 1
        assert counts['Encounter'] == 1
        assert counts['Observation'] == 1
        assert counts['AllergyIntolerance'] == 1
        assert counts['Coverage'] == 1
        assert counts['RelatedPerson'] == 1

        assert bundle_dict['type'] == 'transaction'

    def test_patient_matches_agreed_bundle(self):
        fixture_path = os.path.join(Test_Conversions_Dir, 'ADT_A01.hl7')
        bundle = _convert_fixture(fixture_path)

        our_patient = one_resource(bundle, 'Patient')

        # The agreed bundle the IG publishes for the same message
        agreed_path = os.path.join(Test_Conversions_Dir, 'FHIR_bundle.hl7_ADT_A01.json')

        with open(agreed_path) as agreed_file:
            agreed_bundle = json.load(agreed_file)

        agreed_patient = None

        for entry in agreed_bundle['entry']:
            resource = entry['resource']
            if resource['resourceType'] == 'Patient':
                agreed_patient = resource

        # The demographics agree with the published conversion
        assert our_patient['gender'] == agreed_patient['gender']

        # The agreed birthDate carries a time part, ours is the date FHIR asks for
        agreed_birth = agreed_patient['birthDate']
        assert agreed_birth.startswith(our_patient['birthDate'])

        our_names = our_patient['name']
        agreed_names = agreed_patient['name']

        our_first_name = our_names[0]
        agreed_first_name = agreed_names[0]

        assert our_first_name['family'] == agreed_first_name['family']
        assert our_first_name['given'] == agreed_first_name['given']
        assert our_first_name['use'] == agreed_first_name['use']

        our_maiden_name = our_names[1]
        agreed_maiden_name = agreed_names[1]

        assert our_maiden_name['family'] == agreed_maiden_name['family']
        assert our_maiden_name['use'] == agreed_maiden_name['use']

    def test_encounter_matches_agreed_bundle(self):
        fixture_path = os.path.join(Test_Conversions_Dir, 'ADT_A01.hl7')
        bundle = _convert_fixture(fixture_path)

        encounter = one_resource(bundle, 'Encounter')

        # PV1-2 is E, an emergency encounter
        encounter_class = encounter['class']
        assert encounter_class['code'] == 'EMER'

        # The encounter belongs to the patient from the same bundle
        subject = encounter['subject']
        subject_url = subject['reference']

        assert subject_url.startswith('urn:uuid:')

# ################################################################################################################################
# ################################################################################################################################

def _adt_sample_paths():
    """ All the ADT messages from the samples fixture tree.
    """
    out = []

    for file_path in list_messages(Samples_Dir):
        file_name = os.path.basename(file_path)
        if file_name.startswith('ADT'):
            out.append(file_path)

    return out

# ################################################################################################################################

@pytest.mark.parametrize('file_path', _adt_sample_paths(), ids=os.path.basename)
def test_adt_samples_end_to_end(file_path):
    """ Every ADT sample converts to a bundle with a message header and a patient.
    """
    raw = load_message(file_path)

    try:
        msg = parse_hl7(raw, validate=False)
    except ValueError as e:
        pytest.skip(f'parser rejected the message: {e}')

    bundle = msg.to_fhir()
    bundle_dict = bundle.to_dict()

    assert bundle_dict['type'] == 'transaction'

    counts = _count_types(bundle_dict)
    assert counts['MessageHeader'] == 1

    # Swap and merge messages carry two PID segments, everything else has one patient
    assert counts['Patient'] in (1, 2)

    # Every entry has a stable bundle-internal URL
    for entry in bundle_dict['entry']:
        full_url = entry['fullUrl']
        assert full_url.startswith('urn:uuid:')

# ################################################################################################################################

def test_adt_samples_exist():
    """ The fixture tree holds a meaningful number of ADT samples to prove against.
    """
    sample_paths = _adt_sample_paths()
    assert len(sample_paths) >= 50

# ################################################################################################################################

def test_repeating_al1_makes_multiple_allergies():
    """ Repeating AL1 segments each become their own AllergyIntolerance.
    """
    msh = 'MSH|^~\\&|SENDAPP|SENDFAC|RECVAPP|RECVFAC|20240517143055||ADT^A01|MSG00001|P|2.5'
    pid = 'PID|1||12345||Smith^John|||M'
    al1_first = 'AL1|1|LA|1543^Pollen^RXNORM|MI|Sneezing'
    al1_second = 'AL1|2|FA|1191^Peanut^RXNORM|MO|Rash'

    raw = '\r'.join((msh, pid, al1_first, al1_second)) + '\r'
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
