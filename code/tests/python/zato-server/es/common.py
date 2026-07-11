# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from zato.common.api import ES
from zato.common.typing_ import cast_
from zato.server.connection.facade import ESFacade
from zato.server.generic.api.outconn_es import OutconnESWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from elasticsearch import Elasticsearch
    from es_server import ESServer
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, stranydict

    ESServer = ESServer

# ################################################################################################################################
# ################################################################################################################################

# Letters from four alphabets - document contents in the tests use them all
# to prove that Unicode round trips are byte-for-byte exact.
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
    """ A minimal stand-in for ConfigManager - the facade only reads the outconn_es dict.
    """
    def __init__(self, outconn_es:'stranydict') -> 'None':
        self.outconn_es = outconn_es

# ################################################################################################################################
# ################################################################################################################################

def get_config(server:'ESServer', conn_name:'str', **overrides:'any_') -> 'Bunch':
    """ Builds a connection configuration pointing at the given test server.
    """
    config = {
        'id': 1,
        'name': conn_name,
        'is_active': True,
        'address_list': f'{server.scheme}://{server.host}:{server.port}',
        'username': server.username,
        'secret': server.password,
        'timeout': ES.Default.Timeout,
        'is_tls_validation_enabled': True,
        'tls_ca_certs_file': '',
        'tls_cert_key_file': '',
    }
    config.update(overrides)

    out = bunchify(config)
    return out

# ################################################################################################################################

def get_client(server:'ESServer', conn_name:'str', **overrides:'any_') -> 'Elasticsearch':
    """ Builds a wrapper out of a configuration and returns the underlying Elasticsearch client,
    accessing it the same way services do, through the facade.
    """
    config = get_config(server, conn_name, **overrides)
    wrapper = OutconnESWrapper(config, cast_('any_', _TestServer()))

    # The same structure that the real config manager keeps for each connection
    outconn_es = {conn_name: {'conn': wrapper}}
    config_manager = _TestConfigManager(outconn_es)

    facade = ESFacade()
    facade.init('test-cid', cast_('any_', config_manager))

    out = facade[conn_name]
    return out

# ################################################################################################################################
# ################################################################################################################################
