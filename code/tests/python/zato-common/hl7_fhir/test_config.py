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
P=outpatient
A=ambulatory

[extensions]
base_url=http://example.org/fhir/ext
"""

# ################################################################################################################################
# ################################################################################################################################

def _write_config(tmp_path, contents:'str') -> 'str':
    """ Writes an .ini file into the test's temporary directory and returns its path.
    """
    file_path = os.path.join(tmp_path, 'test-config.ini')

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

    def test_full_config(self, tmp_path):
        file_path = _write_config(tmp_path, _full_config)
        config = load_mapping_config(file_path)

        assert config.bundle_type == 'collection'
        assert config.default_timezone == '+02:00'
        assert config.extension_base_url == 'http://example.org/fhir/ext'

        assert config.identifier_systems == {
            'MYHOSP': 'http://example.org/mrn',
            'MYVISIT': 'http://example.org/visit',
        }

        assert config.code_mappings == {
            'patient_class': {'P': 'outpatient', 'A': 'ambulatory'},
        }

    def test_partial_config_keeps_defaults(self, tmp_path):
        file_path = _write_config(tmp_path, '[bundle]\ntype=batch\n')
        config = load_mapping_config(file_path)

        assert config.bundle_type == 'batch'
        assert config.default_timezone == Default_Timezone
        assert config.extension_base_url == Default_Extension_Base_URL

    def test_caching_returns_same_object(self, tmp_path):
        file_path = _write_config(tmp_path, _full_config)

        first = load_mapping_config(file_path)
        second = load_mapping_config(file_path)

        assert first is second

    def test_name_resolution_through_registered_directory(self, tmp_path):
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

    def test_unknown_section_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[nosuch]\nkey=value\n')

        with pytest.raises(Exception, match='Unknown section'):
            _ = load_mapping_config(file_path)

    def test_unknown_key_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[bundle]\nnosuch=value\n')

        with pytest.raises(Exception, match='Unknown key'):
            _ = load_mapping_config(file_path)

    def test_key_outside_section_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, 'stray=value\n')

        with pytest.raises(Exception, match='outside any section'):
            _ = load_mapping_config(file_path)

    def test_subsection_in_flat_section_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[bundle]\n[[nested]]\nkey=value\n')

        with pytest.raises(Exception, match='does not allow subsections'):
            _ = load_mapping_config(file_path)

    def test_loose_key_in_nested_section_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[identifiers]\nstray=value\n')

        with pytest.raises(Exception, match='only allows subsections'):
            _ = load_mapping_config(file_path)

    def test_unknown_bundle_type_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[bundle]\ntype=nosuch\n')

        with pytest.raises(Exception, match='Unknown bundle type'):
            _ = load_mapping_config(file_path)

    def test_identifier_subsection_missing_system_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[identifiers]\n[[mrn]]\nauthority=MYHOSP\n')

        with pytest.raises(Exception, match='Missing key `system`'):
            _ = load_mapping_config(file_path)

    def test_identifier_subsection_unknown_key_rejected(self, tmp_path):
        file_path = _write_config(tmp_path, '[identifiers]\n[[mrn]]\nauthority=A\nsystem=B\nnosuch=C\n')

        with pytest.raises(Exception, match='Unknown key `nosuch`'):
            _ = load_mapping_config(file_path)

# ################################################################################################################################
# ################################################################################################################################

class TestDemoFile:

    def test_shipped_demo_contents_load(self, tmp_path):
        # The very demo file zato create server writes into user-conf must load cleanly
        from zato.cli.create_server import hl7_fhir_demo_contents

        file_path = _write_config(tmp_path, hl7_fhir_demo_contents)
        config = load_mapping_config(file_path)

        assert config.bundle_type == 'transaction'
        assert 'MYHOSP' in config.identifier_systems

# ################################################################################################################################
# ################################################################################################################################
