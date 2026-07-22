# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# Test suite
from _test_util import create_definition, delete_definition, get_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My Tenant CRM'
_conn_type = 'outconn-crm'
_service_name = 'demo.crm.get-customer-tenant'

_main_api_key = 'main.key.' + CryptoManager.generate_hex_string()
_tenant_key_1 = 'tenant.key.1.' + CryptoManager.generate_hex_string()
_tenant_key_2 = 'tenant.key.2.' + CryptoManager.generate_hex_string()

_customer_id = 'CUST-8001'

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def test_tenant_create_definition(zato_server:'stranydict') -> 'None':
    """ The definition the multi-tenant scenarios run against.
    """
    _TestState.conn_id = create_definition(zato_server, _conn_name, _conn_type,
        host='127.0.0.1',
        port=zato_server['echo_port'],
        api_key=_main_api_key,
    )

# ################################################################################################################################

def test_tenant_clients_use_their_own_credentials(zato_server:'stranydict') -> 'None':
    """ One definition serves many credential sets - each with_config call resolves
    to a client of its own, built with the overridden values (4.6).
    """
    client = get_client(zato_server)

    # Each tenant's reply carries the key that tenant's client was built with,
    # proving that the overrides reached create_client.
    for tenant_key in (_tenant_key_1, _tenant_key_2):
        response = client.invoke(_service_name, {'customer_id': _customer_id, 'api_key': tenant_key})
        assert response['response'] == f'{tenant_key} get-customer {_customer_id}'

    # A repeated call with the same overrides reuses the same client - and still works.
    response = client.invoke(_service_name, {'customer_id': _customer_id, 'api_key': _tenant_key_1})
    assert response['response'] == f'{_tenant_key_1} get-customer {_customer_id}'

# ################################################################################################################################

def test_tenant_delete_definition(zato_server:'stranydict') -> 'None':
    """ Deleting the definition stops the tenants' clients along with the main one.
    """
    delete_definition(zato_server, _TestState.conn_id)

# ################################################################################################################################
# ################################################################################################################################
