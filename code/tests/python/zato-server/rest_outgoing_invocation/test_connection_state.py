# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Connection state - an inactive connection refusing to send anything, and a connection rebuilt from an updated
# configuration sending its requests to the new address with the new credentials.

# pytest
import pytest

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.exception import Inactive

# Test support
from support import Basic_Password, Basic_Username, get_basic_authorization, new_basic_auth_connection, new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('method_name', ['get', 'post', 'put', 'patch', 'delete', 'options', 'rest_invoke'])
def test_inactive_connection(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method_name:'str') -> 'None':
    """ An inactive connection raises Inactive without sending a request.
    """
    connection = new_connection(server, endpoint.http_base, path, is_active=False)
    method = getattr(connection, method_name)

    with pytest.raises(Inactive) as info:
        _ = method(Test_CID)

    assert info.value.msg == '`test.rest.outgoing` is inactive'
    assert endpoint.get_requests(path) == []

# ################################################################################################################################

def test_configuration_update(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection rebuilt from an updated configuration sends its requests to the new address with the new credentials,
    and nothing more is sent to the previous address.
    """
    new_path = path + '/updated'
    new_password = 'Updated.Password.2026'

    connection = new_basic_auth_connection(server, endpoint.http_base, path)
    _ = connection.get(Test_CID)

    # The server replaces the connection with one built from the updated configuration
    connection = new_connection(
        server,
        endpoint.https_base,
        new_path,
        sec_type=SEC_DEF_TYPE.BASIC_AUTH,
        username=Basic_Username,
        password=new_password,
        ca_certs_path=endpoint.certificates.ca_path,
    )

    _ = connection.get(Test_CID)
    _ = connection.get(Test_CID)

    previous_request = endpoint.get_request(path)
    first_new, second_new = endpoint.get_requests(new_path)

    assert previous_request.port == endpoint.http_port
    assert previous_request.get_header('Authorization') == get_basic_authorization(Basic_Username, Basic_Password)

    assert first_new.port == endpoint.https_port
    assert first_new.get_header('Authorization') == get_basic_authorization(Basic_Username, new_password)
    assert second_new.get_header('Authorization') == get_basic_authorization(Basic_Username, new_password)

# ################################################################################################################################

def test_activation_change(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection rebuilt as inactive from the configuration of an active one stops sending requests.
    """
    connection = new_connection(server, endpoint.http_base, path)
    _ = connection.get(Test_CID)

    connection = new_connection(server, endpoint.http_base, path, is_active=False)

    with pytest.raises(Inactive):
        _ = connection.get(Test_CID)

    assert len(endpoint.get_requests(path)) == 1

# ################################################################################################################################
# ################################################################################################################################
