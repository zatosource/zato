# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.hl7.common import add_config_location
from zato.hl7.mappings.config import Default_Bundle_Type, Default_Extension_Base_URL, Default_Timezone, load_mapping_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# A config file with every section populated, the same shape the shipped demo file has
_full_config = """
[bundle]
type=collection

[datetime]
default_timezone=+02:00

[identifiers]

[[patient_mrn]]
authority=MYHOSP
system=http://example.org/mrn

[[visit_number]]
authority=MYVISIT
system=http://example.org/visit

[codes]

[[patient_class]]
P=AMB
X=http://terminology.hl7.org/CodeSystem/v3-ActCode|IMP
Y=http://example.org/classes|day-case

[extensions]
base_url=http://example.org/fhir/ext
"""

# ################################################################################################################################
# ################################################################################################################################

def _write_config(tmp_path:'any_', contents:'str', file_name:'str'='test-config.ini') -> 'str':
    """ Writes an .ini file into the test's temporary directory and returns its path.
    """
    file_path = os.path.join(tmp_path, file_name)

    with open(file_path, 'w') as file_object:
        _ = file_object.write(contents)

    return file_path

# ################################################################################################################################
# ################################################################################################################################

class TestDefaults:

    def test_no_config_returns_defaults(self):
        config = load_mapping_config(None)

        assert config.bundle_type == Default_Bundle_Type
        assert config.default_timezone == Default_Timezone
        assert config.extension_base_url == Default_Extension_Base_URL
        assert config.identifier_systems == {}
        assert config.code_mappings == {}

    def test_empty_string_returns_defaults(self):
        config = load_mapping_config('')
        assert config.bundle_type == Default_Bundle_Type

# ################################################################################################################################
# ################################################################################################################################

class TestLoading:

    def test_full_config(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, _full_config)
        config = load_mapping_config(file_path)

        assert config.bundle_type == 'collection'
        assert config.default_timezone == '+02:00'
        assert config.extension_base_url == 'http://example.org/fhir/ext'

        assert config.identifier_systems == {
            'MYHOSP': 'http://example.org/mrn',
            'MYVISIT': 'http://example.org/visit',
        }

        # Each override resolves to its code and system when the file loads - the system
        # is inferred when only one of the map's systems knows the target, explicit otherwise.
        assert config.code_mappings == {
            'patient_class': {
                'P': {'code': 'AMB', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode'},
                'X': {'code': 'IMP', 'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode'},
                'Y': {'code': 'day-case', 'system': 'http://example.org/classes'},
            },
        }

    def test_partial_config_keeps_defaults(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[bundle]\ntype=batch\n')
        config = load_mapping_config(file_path)

        assert config.bundle_type == 'batch'
        assert config.default_timezone == Default_Timezone
        assert config.extension_base_url == Default_Extension_Base_URL

    def test_caching_returns_same_object(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, _full_config)

        first = load_mapping_config(file_path)
        second = load_mapping_config(file_path)

        assert first is second

    def test_name_resolution_through_registered_directory(self, tmp_path:'any_'):
        file_path = os.path.join(tmp_path, 'my-mappings.ini')

        with open(file_path, 'w') as file_object:
            _ = file_object.write('[bundle]\ntype=batch\n')

        add_config_location(str(tmp_path))
        config = load_mapping_config('my-mappings')

        assert config.bundle_type == 'batch'

    def test_unknown_name_raises(self):
        with pytest.raises(Exception, match='not found'):
            _ = load_mapping_config('no-such-config-name-anywhere')

# ################################################################################################################################
# ################################################################################################################################

class TestValidation:

    def test_unknown_section_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[nosuch]\nkey=value\n')

        with pytest.raises(Exception, match='Unknown section'):
            _ = load_mapping_config(file_path)

    def test_unknown_key_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[bundle]\nnosuch=value\n')

        with pytest.raises(Exception, match='Unknown key'):
            _ = load_mapping_config(file_path)

    def test_key_outside_section_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, 'stray=value\n')

        with pytest.raises(Exception, match='outside any section'):
            _ = load_mapping_config(file_path)

    def test_subsection_in_flat_section_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[bundle]\n[[nested]]\nkey=value\n')

        with pytest.raises(Exception, match='does not allow subsections'):
            _ = load_mapping_config(file_path)

    def test_loose_key_in_nested_section_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[identifiers]\nstray=value\n')

        with pytest.raises(Exception, match='only allows subsections'):
            _ = load_mapping_config(file_path)

    def test_unknown_bundle_type_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[bundle]\ntype=nosuch\n')

        with pytest.raises(Exception, match='Unknown bundle type'):
            _ = load_mapping_config(file_path)

    def test_identifier_subsection_missing_system_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[identifiers]\n[[mrn]]\nauthority=MYHOSP\n')

        with pytest.raises(Exception, match='Missing key `system`'):
            _ = load_mapping_config(file_path)

    def test_identifier_subsection_unknown_key_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[identifiers]\n[[mrn]]\nauthority=A\nsystem=B\nnosuch=C\n')

        with pytest.raises(Exception, match='Unknown key `nosuch`'):
            _ = load_mapping_config(file_path)

    def test_unknown_codes_map_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[codes]\n[[nosuch_map]]\nA=B\n')

        with pytest.raises(Exception, match='Unknown map `\\[\\[nosuch_map\\]\\]`'):
            _ = load_mapping_config(file_path)

    def test_override_unknown_target_rejected(self, tmp_path:'any_'):
        # `outpatient` is not a code any of the map's systems holds.
        file_path = _write_config(tmp_path, '[codes]\n[[patient_class]]\nP=outpatient\n')

        with pytest.raises(Exception, match='targets unknown code `outpatient`'):
            _ = load_mapping_config(file_path)

    def test_override_unknown_target_in_known_system_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[codes]\n[[patient_class]]\nP=http://terminology.hl7.org/CodeSystem/v3-ActCode|nosuch\n')

        with pytest.raises(Exception, match='targets unknown code `nosuch`'):
            _ = load_mapping_config(file_path)

    def test_override_coding_system_name_resolves(self, tmp_path:'any_'):
        # A coding system name stands for its URI.
        file_path = _write_config(tmp_path, '[codes]\n[[patient_class]]\nP=HL70004|R\n')
        config = load_mapping_config(file_path)

        assert config.code_mappings['patient_class']['P'] == {
            'code': 'R', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0004',
        }

    def test_override_without_target_rejected(self, tmp_path:'any_'):
        file_path = _write_config(tmp_path, '[codes]\n[[patient_class]]\nP=http://example.org/classes|\n')

        with pytest.raises(Exception, match='has no target code'):
            _ = load_mapping_config(file_path)

    def test_invalid_timezone_rejected(self, tmp_path:'any_'):
        for value in ('nonsense', '+2:00', '+0200', '+15:00', '+02:60', 'UTC'):
            file_path = _write_config(tmp_path, f'[datetime]\ndefault_timezone={value}\n')

            with pytest.raises(Exception, match='Invalid default_timezone'):
                _ = load_mapping_config(file_path)

    def test_valid_timezones_accepted(self, tmp_path:'any_'):

        # Configs cache by path, so each value gets a file of its own.
        for index, value in enumerate(('Z', '+02:00', '-05:30', '+14:00')):
            file_path = _write_config(tmp_path, f'[datetime]\ndefault_timezone={value}\n', f'tz-{index}.ini')
            config = load_mapping_config(file_path)

            assert config.default_timezone == value

    def test_invalid_base_url_rejected(self, tmp_path:'any_'):
        for value in ('not a url', 'example.org/ext', 'http://', '/relative/path'):
            file_path = _write_config(tmp_path, f'[extensions]\nbase_url={value}\n')

            with pytest.raises(Exception, match='Invalid base_url'):
                _ = load_mapping_config(file_path)

    def test_valid_base_urls_accepted(self, tmp_path:'any_'):

        # Configs cache by path, so each value gets a file of its own.
        for index, value in enumerate(('http://example.org/fhir/ext', 'urn:example:ext', 'https://example.org')):
            file_path = _write_config(tmp_path, f'[extensions]\nbase_url={value}\n', f'url-{index}.ini')
            config = load_mapping_config(file_path)

            assert config.extension_base_url == value

# ################################################################################################################################
# ################################################################################################################################

class TestDemoFile:

    def test_shipped_demo_contents_load(self, tmp_path:'any_'):
        # The very demo file zato create server writes into user-conf must load cleanly
        from zato.cli.create_server import hl7_fhir_demo_contents

        file_path = _write_config(tmp_path, hl7_fhir_demo_contents)
        config = load_mapping_config(file_path)

        assert config.bundle_type == 'transaction'
        assert 'MYHOSP' in config.identifier_systems

# ################################################################################################################################
# ################################################################################################################################
