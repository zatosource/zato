# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from shutil import copy as shutil_copy

# PyYAML
from yaml import safe_load

# pytest
import pytest

# Zato
from zato.common.util.open_ import open_r
from zato.common.util.safeguards import masking
from zato.common.util.safeguards.masking import get_masking_config, resolve_masked_fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many industry sets ship with the product.
_expected_set_count = 18

# The directory the set files are read from.
_sets_directory = masking._sets_directory

# ################################################################################################################################
# ################################################################################################################################

def _set_file_names() -> 'strlist':
    out = sorted(name for name in os.listdir(_sets_directory) if name.endswith('.yaml'))
    return out

# ################################################################################################################################

def _load_set_file(file_name:'str') -> 'anydict':
    with open_r(os.path.join(_sets_directory, file_name)) as opened:
        out = safe_load(opened.read())
    return out

# ################################################################################################################################

def _fields_of(set_name:'str') -> 'strlist':
    for item in get_masking_config():
        if item['name'] == set_name:
            return item['fields']
    raise Exception(f'No set `{set_name}`')

# ################################################################################################################################
# ################################################################################################################################

class TestSetFiles:

    def test_the_directory_yields_every_set(self) -> 'None':
        assert len(_set_file_names()) == _expected_set_count
        assert len(get_masking_config()) == _expected_set_count

    @pytest.mark.parametrize('file_name', _set_file_names())
    def test_each_file_loads_on_its_own(self, file_name:'str') -> 'None':

        data = _load_set_file(file_name)

        assert sorted(data) == ['fields', 'label', 'position'], file_name
        assert isinstance(data['label'], str), file_name
        assert isinstance(data['position'], int), file_name
        assert data['fields'], file_name

    @pytest.mark.parametrize('file_name', _set_file_names())
    def test_each_file_holds_lowercase_unique_names(self, file_name:'str') -> 'None':

        fields = _load_set_file(file_name)['fields']
        lowercase = [name.lower() for name in fields]

        assert fields == lowercase, file_name
        assert len(set(lowercase)) == len(lowercase), file_name

    @pytest.mark.parametrize('file_name', _set_file_names())
    def test_no_file_holds_a_generic_tax_identifier(self, file_name:'str') -> 'None':
        fields = _load_set_file(file_name)['fields']
        assert 'tax_id' not in fields, file_name

    def test_no_two_sets_share_a_position(self) -> 'None':
        positions = [item['position'] for item in get_masking_config()]
        assert len(set(positions)) == len(positions)

    def test_the_sets_are_ordered_by_position(self) -> 'None':
        positions = [item['position'] for item in get_masking_config()]
        assert positions == sorted(positions)
        assert positions == list(range(1, _expected_set_count + 1))

    def test_the_names_come_from_the_file_names(self) -> 'None':
        names = sorted(item['name'] for item in get_masking_config())
        expected = sorted(name.removesuffix('.yaml') for name in _set_file_names())
        assert names == expected

    def test_the_first_and_last_sets(self) -> 'None':
        config = get_masking_config()
        assert config[0]['name'] == 'common'
        assert config[-1]['name'] == 'it_operations'

    def test_the_files_are_read_once(self) -> 'None':
        assert get_masking_config() is get_masking_config()

    def test_a_file_other_than_a_set_is_skipped(self, tmp_path:'Path', monkeypatch:'pytest.MonkeyPatch') -> 'None':

        # A directory holding one set file and one file that is not a set ..
        _ = shutil_copy(os.path.join(_sets_directory, 'banking.yaml'), tmp_path)
        _ = (tmp_path / 'README.txt').write_text('Not a set')

        # .. is read in place of the shipped one ..
        monkeypatch.setattr(masking, '_sets_directory', str(tmp_path))
        get_masking_config.cache_clear()

        # .. and only the set file yields a set.
        try:
            names = [item['name'] for item in get_masking_config()]
            assert names == ['banking']
        finally:
            get_masking_config.cache_clear()

# ################################################################################################################################
# ################################################################################################################################

class TestResolveMaskedFields:

    def test_nothing_picked_masks_nothing(self) -> 'None':
        assert resolve_masked_fields([], [], [], True) == set()

    def test_one_set_masks_its_fields(self) -> 'None':
        out = resolve_masked_fields(['banking'], [], [], True)
        assert out == {name.lower() for name in _fields_of('banking')}

    def test_two_sets_are_merged(self) -> 'None':
        out = resolve_masked_fields(['banking', 'healthcare'], [], [], True)
        expected = {name.lower() for name in _fields_of('banking') + _fields_of('healthcare')}
        assert out == expected

    def test_an_excluded_field_is_left_out(self) -> 'None':
        out = resolve_masked_fields(['banking'], ['iban'], [], True)
        assert 'iban' not in out
        assert 'iban' in _fields_of('banking')

    def test_an_exclusion_is_compared_without_regard_to_case(self) -> 'None':
        out = resolve_masked_fields(['banking'], ['IBAN'], [], True)
        assert 'iban' not in out

    def test_custom_fields_switched_on_are_masked(self) -> 'None':
        out = resolve_masked_fields([], [], ['loyalty_id', 'Internal_Code'], True)
        assert out == {'loyalty_id', 'internal_code'}

    def test_custom_fields_switched_off_are_not_masked(self) -> 'None':
        out = resolve_masked_fields(['banking'], [], ['loyalty_id'], False)
        assert 'loyalty_id' not in out
        assert 'iban' in out

    def test_a_custom_field_duplicating_a_set_field_is_one_name(self) -> 'None':
        out = resolve_masked_fields(['banking'], [], ['IBAN', 'Iban'], True)
        assert [name for name in out if name == 'iban'] == ['iban']
        assert len(out) == len(set(_fields_of('banking')))

    def test_an_exclusion_does_not_remove_a_custom_field(self) -> 'None':
        out = resolve_masked_fields(['banking'], ['iban'], ['iban'], True)
        assert 'iban' in out

    def test_an_unknown_set_is_rejected(self) -> 'None':
        with pytest.raises(Exception, match='Unknown data masking set'):
            _ = resolve_masked_fields(['no_such_set'], [], [], True)

# ################################################################################################################################
# ################################################################################################################################
