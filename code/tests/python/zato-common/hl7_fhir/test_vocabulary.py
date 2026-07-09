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
from zato.hl7.mappings import vocabulary
from zato.hl7.mappings.codes import coding_system_to_uri, lookup
from zato.hl7.mappings.config import _new_config

# Local
from conftest import V2_Mappings_Dir

# ################################################################################################################################
# ################################################################################################################################

def _load_concept_map(fixture_id:'str') -> 'dict':
    """ Loads one ConceptMap fixture from the IG package.
    """
    fixture_path = os.path.join(V2_Mappings_Dir, f'ConceptMap-{fixture_id}.json')

    with open(fixture_path) as fixture_file:
        out = json.load(fixture_file)

    return out

# ################################################################################################################################

def _extract_spec_codes(concept_map:'dict') -> 'dict':
    """ Extracts the source-to-target code pairs a ConceptMap defines, the same way
    generate_vocabulary.py does when it writes vocabulary.py.
    """
    out = {}

    for group in concept_map['group']:
        group_target = group.get('target')
        if not group_target:
            continue

        for element in group['element']:
            source_code = element['code']

            for target in element.get('target', []):
                target_code = target.get('code')
                if target_code:
                    if source_code not in out:
                        out[source_code] = {'code': target_code, 'system': group_target}
                    break

    return out

# ################################################################################################################################
# ################################################################################################################################

# Every vocabulary map and the ConceptMap fixture it must match
_map_names = sorted(vocabulary.table_sources)

# ################################################################################################################################

@pytest.mark.parametrize('map_name', _map_names)
def test_vocabulary_matches_spec(map_name):
    """ Proof - every map in vocabulary.py covers exactly what its IG ConceptMap defines.
    """
    fixture_id = vocabulary.table_sources[map_name]
    concept_map = _load_concept_map(fixture_id)

    spec_codes = _extract_spec_codes(concept_map)
    our_codes = getattr(vocabulary, map_name)

    # Same source codes, no more and no fewer ..
    assert set(our_codes) == set(spec_codes), f'{map_name} does not match ConceptMap-{fixture_id}'

    # .. and the same target code and system for each one.
    for source_code in spec_codes:
        assert our_codes[source_code] == spec_codes[source_code], \
            f'{map_name}[{source_code!r}] does not match ConceptMap-{fixture_id}'

# ################################################################################################################################

def test_all_maps_have_fixture_sources():
    """ Every documented vocabulary map exists and every fixture it points to is on disk.
    """
    for map_name in _map_names:
        assert hasattr(vocabulary, map_name)

        fixture_id = vocabulary.table_sources[map_name]
        fixture_path = os.path.join(V2_Mappings_Dir, f'ConceptMap-{fixture_id}.json')
        assert os.path.isfile(fixture_path), fixture_path

# ################################################################################################################################
# ################################################################################################################################

class TestLookup:

    def test_known_code(self, default_config):
        out = lookup('administrative_sex', 'F', default_config)
        assert out == {'code': 'female', 'system': 'http://hl7.org/fhir/administrative-gender'}

    def test_unknown_code(self, default_config):
        assert lookup('administrative_sex', 'ZZ', default_config) is None

    def test_empty_code(self, default_config):
        assert lookup('administrative_sex', None, default_config) is None
        assert lookup('administrative_sex', '', default_config) is None

    def test_config_override(self):
        config = _new_config()
        config.code_mappings = {'patient_class': {'P': 'AMB'}}

        out = lookup('patient_class', 'P', config)
        assert out['code'] == 'AMB'

    def test_config_override_new_code(self):
        # A code the standard table does not know at all, added by the config
        config = _new_config()
        config.code_mappings = {'patient_class': {'X': 'IMP'}}

        out = lookup('patient_class', 'X', config)
        assert out['code'] == 'IMP'

# ################################################################################################################################
# ################################################################################################################################

class TestCodingSystemToURI:

    def test_well_known_names(self):
        assert coding_system_to_uri('LN') == 'http://loinc.org'
        assert coding_system_to_uri('SCT') == 'http://snomed.info/sct'
        assert coding_system_to_uri('UCUM') == 'http://unitsofmeasure.org'
        assert coding_system_to_uri('I10') == 'http://hl7.org/fhir/sid/icd-10'

    def test_hl7_table_names(self):
        assert coding_system_to_uri('HL70001') == 'http://terminology.hl7.org/CodeSystem/v2-0001'
        assert coding_system_to_uri('HL70078') == 'http://terminology.hl7.org/CodeSystem/v2-0078'

    def test_uris_pass_through(self):
        assert coding_system_to_uri('http://loinc.org') == 'http://loinc.org'
        assert coding_system_to_uri('urn:oid:1.2.3') == 'urn:oid:1.2.3'

    def test_unknown_names(self):
        assert coding_system_to_uri('NOSUCH') is None
        assert coding_system_to_uri('') is None
        assert coding_system_to_uri(None) is None

# ################################################################################################################################
# ################################################################################################################################
