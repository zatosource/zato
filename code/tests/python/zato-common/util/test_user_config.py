# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.user_config import UserConfig, UserConfigFile, UserConfigSection

# ################################################################################################################################
# ################################################################################################################################

_file_name = 'codes.ini'

# ################################################################################################################################
# ################################################################################################################################

def _new_store() -> 'UserConfig':
    out = UserConfig()
    out.zato_dir_names.append('/opt/zato/env/qs-1/server1/config/repo/user-conf')

    return out

# ################################################################################################################################

def _new_config_file(store:'UserConfig') -> 'UserConfigFile':
    data = {
        'codes': {'A': 'Accepted', 'R': 'Rejected'},
        'partner': {'ACK': 'A', 'NAK': 'R'},
        'version': 2,
    }

    out = UserConfigFile(_file_name, store, data)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestUserConfig:

    def test_store_keeps_directories_out_of_keys(self) -> 'None':
        store = _new_store()

        assert store.zato_dir_names == ['/opt/zato/env/qs-1/server1/config/repo/user-conf']
        assert 'zato_dir_names' not in store

# ################################################################################################################################

    def test_sections_are_wrapped_on_init(self) -> 'None':
        store = _new_store()
        config_file = _new_config_file(store)

        codes = config_file.codes
        partner = config_file.partner

        assert isinstance(codes, UserConfigSection)
        assert isinstance(partner, UserConfigSection)

        assert codes.zato_file_name == _file_name
        assert codes.zato_section_name == 'codes'
        assert partner.zato_section_name == 'partner'

        assert 'zato_file_name' not in codes
        assert 'zato_section_name' not in codes

        assert codes.A == 'Accepted'
        assert config_file.version == 2

# ################################################################################################################################

    def test_reload_wraps_sections_and_drops_the_missing_ones(self) -> 'None':
        store = _new_store()
        config_file = _new_config_file(store)

        config_file.zato_reload({
            'codes': {'A': 'Accepted'},
            'supplier': {'OK': 'A'},
        })

        assert sorted(config_file) == ['codes', 'supplier']
        assert 'partner' not in config_file
        assert 'version' not in config_file

        supplier = config_file.supplier

        assert isinstance(supplier, UserConfigSection)
        assert supplier.zato_file_name == _file_name
        assert supplier.zato_section_name == 'supplier'
        assert supplier.OK == 'A'

        assert config_file.zato_file_name == _file_name

# ################################################################################################################################

    def test_validate_and_translate_work_on_wrapped_sections(self) -> 'None':
        store = _new_store()
        config_file = _new_config_file(store)
        store.codes = config_file

        assert config_file.validate('A')
        assert not config_file.validate('X')

        assert config_file.translate(source='partner', code='ACK') == 'A'
        assert config_file.translate(source='partner', code='ACK', codes='codes') == 'A'
        assert config_file.translate(source='partner', code='NAK', target='partner') == 'NAK'
        assert config_file.translate(source='partner', code='UNKNOWN') is None

# ################################################################################################################################
# ################################################################################################################################
