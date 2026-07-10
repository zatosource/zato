# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.facade import MongoDBFacade
from zato.server.generic.api.outconn_mongodb import OutconnMongoDBWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pymongo import MongoClient
    from containers import MongoDBServer
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, stranydict

    MongoDBServer = MongoDBServer

# ################################################################################################################################
# ################################################################################################################################

# Letters from four alphabets - collection names and document contents in the tests
# use them all to prove that Unicode round trips are byte-for-byte exact.
Ascii_Letters  = 'ABCDEF'
Dutch_Letters  = 'ÁÉÍÓÚË'
Greek_Letters  = 'ΑΒΓΔΕΖ'
Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

All_Letters = Ascii_Letters + Dutch_Letters + Greek_Letters + Korean_Letters

# ################################################################################################################################
# ################################################################################################################################

class _TestServer:
    """ A minimal stand-in for ParallelServer - the wrapper only needs the decrypt method
    and the test passwords are never encrypted, which is why they are returned as they are.
    """
    def decrypt(self, value:'str') -> 'str':
        return value

# ################################################################################################################################
# ################################################################################################################################

class _TestConfigManager:
    """ A minimal stand-in for ConfigManager - the facade only reads the outconn_mongodb dict.
    """
    def __init__(self, outconn_mongodb:'stranydict') -> 'None':
        self.outconn_mongodb = outconn_mongodb

# ################################################################################################################################
# ################################################################################################################################

def get_config(server:'MongoDBServer', conn_name:'str', **overrides:'any_') -> 'Bunch':
    """ Builds a connection configuration pointing at the given test server.
    """
    config = {
        'id': 1,
        'name': conn_name,
        'is_active': True,
        'server_list': f'{server.host}:{server.port}',
        'username': server.username,
        'secret': server.password,
        'auth_source': 'admin',
        'replica_set': '',
        'app_name': 'Zato',
        'pool_size_max': 10,
        'connect_timeout': 10,
        'server_select_timeout': 5,
        'is_tls_enabled': False,
        'tls_ca_certs_file': '',
        'tls_cert_key_file': '',
        'is_tls_validation_enabled': True,
    }
    config.update(overrides)

    out = bunchify(config)
    return out

# ################################################################################################################################

def get_client(server:'MongoDBServer', conn_name:'str', **overrides:'any_') -> 'MongoClient':
    """ Builds a wrapper out of a configuration and returns the underlying pymongo client,
    accessing it the same way services do, through the facade.
    """
    config = get_config(server, conn_name, **overrides)
    wrapper = OutconnMongoDBWrapper(config, cast_('any_', _TestServer()))

    # The same structure that the real config manager keeps for each connection
    outconn_mongodb = {conn_name: {'conn': wrapper}}
    config_manager = _TestConfigManager(outconn_mongodb)

    facade = MongoDBFacade()
    facade.init('test-cid', cast_('any_', config_manager))

    out = facade[conn_name]
    return out

# ################################################################################################################################
# ################################################################################################################################
