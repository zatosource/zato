# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.ext.bunch import Bunch
from zato.server.base.parallel.config import generic_connection_key
from zato.server.config import ConfigDict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The columns a query in these tests returns, in the shape from_query expects - a dict keyed by attribute name
_attrs = {'id': None, 'name': None, 'type_': None, 'host': None}

# One name reused by three connections of three different types, which is allowed in the database
_shared_name = 'partner'

_type_sftp = 'outconn-sftp'
_type_smb = 'outconn-smb'
_type_mongodb = 'outconn-mongodb'

# ################################################################################################################################
# ################################################################################################################################

def _row(id:'int', name:'str', type_:'str', host:'str') -> 'Bunch':
    """ One row as SQLAlchemy would hand it over - attributes rather than keys.
    """
    out = Bunch()
    out.id = id
    out.name = name
    out.type_ = type_
    out.host = host
    return out

# ################################################################################################################################

def _rows_sharing_a_name() -> 'anylist':
    out = [
        _row(1, _shared_name, _type_sftp, 'sftp.example.com'),
        _row(2, _shared_name, _type_smb, 'smb.example.com'),
        _row(3, _shared_name, _type_mongodb, 'mongodb.example.com'),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFromQuery:
    """ How ConfigDict.from_query keys what it loads.
    """

    def test_default_key_is_the_name(self) -> 'None':

        rows = [
            _row(1, 'alpha', _type_sftp, 'alpha.example.com'),
            _row(2, 'beta', _type_sftp, 'beta.example.com'),
        ]

        config_dict = ConfigDict.from_query('generic_connection', (rows, _attrs))

        assert sorted(config_dict.keys()) == ['alpha', 'beta']
        assert config_dict['alpha'].config.host == 'alpha.example.com'
        assert config_dict['beta'].config.host == 'beta.example.com'

# ################################################################################################################################

    def test_same_name_across_types_collapses_without_key_func(self) -> 'None':

        # Keyed by name alone, three rows land under one key and only the last one survives,
        # which is the collision that key_func exists to prevent.
        config_dict = ConfigDict.from_query('generic_connection', (_rows_sharing_a_name(), _attrs))

        assert list(config_dict.keys()) == [_shared_name]
        assert config_dict[_shared_name].config.type_ == _type_mongodb

# ################################################################################################################################

    def test_key_func_keeps_same_name_across_types_apart(self) -> 'None':

        config_dict = ConfigDict.from_query('generic_connection', (_rows_sharing_a_name(), _attrs),
            key_func=generic_connection_key)

        expected:'strlist' = [
            f'{_type_mongodb}/{_shared_name}',
            f'{_type_sftp}/{_shared_name}',
            f'{_type_smb}/{_shared_name}',
        ]
        assert sorted(config_dict.keys()) == expected

        # Each connection is reachable under its own type and carries its own details
        sftp = config_dict[f'{_type_sftp}/{_shared_name}'].config
        smb = config_dict[f'{_type_smb}/{_shared_name}'].config
        mongodb = config_dict[f'{_type_mongodb}/{_shared_name}'].config

        assert sftp.id == 1
        assert sftp.host == 'sftp.example.com'

        assert smb.id == 2
        assert smb.host == 'smb.example.com'

        assert mongodb.id == 3
        assert mongodb.host == 'mongodb.example.com'

# ################################################################################################################################

    def test_key_func_result_is_the_only_key_used(self) -> 'None':

        # The row has a name, yet with key_func given the name on its own is never a key
        rows = [_row(1, _shared_name, _type_sftp, 'sftp.example.com')]

        config_dict = ConfigDict.from_query('generic_connection', (rows, _attrs), key_func=generic_connection_key)

        assert _shared_name not in config_dict
        assert f'{_type_sftp}/{_shared_name}' in config_dict

# ################################################################################################################################

    def test_generic_connection_key_is_type_and_name(self) -> 'None':

        row = _row(1, _shared_name, _type_sftp, 'sftp.example.com')
        assert generic_connection_key(row) == f'{_type_sftp}/{_shared_name}'

# ################################################################################################################################
# ################################################################################################################################
