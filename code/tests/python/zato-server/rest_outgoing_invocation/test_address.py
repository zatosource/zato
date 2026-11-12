# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The address a request goes to - the host and the path of the connection, with the path parameters
# of a template filled in from what the caller gave and removed from the query string.

# stdlib
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.exception import BadRequest

# Test support
from endpoint import Host
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The template the path parameter tests append to their own path
_template_suffix = '/items/{item_id}/{name}'

# ################################################################################################################################
# ################################################################################################################################

def test_host_and_path(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A request goes to the host and the path of the connection, with a Host header naming the host and the port.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert response.status_code == OK

    request = endpoint.get_request(path)

    assert request.method == 'GET'
    assert request.target == path
    assert request.version == 'HTTP/1.1'
    assert request.get_header('Host') == f'{Host}:{endpoint.http_port}'

# ################################################################################################################################

def test_path_parameters_are_encoded(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Every character that means something to a URL is encoded in a path parameter, the slash and the percent sign included,
    so a value fills in exactly one segment and a value spelled as ../ names no directory above it.
    """
    connection = new_connection(server, endpoint.http_base, path + _template_suffix)

    params = {
        'item_id': 'a/b%c?d#e f',
        'name': '../',
    }

    _ = connection.get(Test_CID, params)

    expected_path = path + '/items/a%2Fb%25c%3Fd%23e%20f/..%2F'
    request = endpoint.get_request(expected_path)

    assert request.query == ''

# ################################################################################################################################

def test_path_parameters_non_ascii(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A non-ASCII path parameter is sent as the percent-encoded bytes of its UTF-8 form.
    """
    connection = new_connection(server, endpoint.http_base, path + _template_suffix)

    params = {
        'item_id': 'Zürich',
        'name': 123,
    }

    _ = connection.get(Test_CID, params)

    expected_path = path + '/items/Z%C3%BCrich/123'
    _ = endpoint.get_request(expected_path)

# ################################################################################################################################

def test_path_parameters_removed_from_query_string(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The parameters a template names fill in the path, and only the remaining ones go to the query string.
    """
    connection = new_connection(server, endpoint.http_base, path + _template_suffix)

    params = {
        'item_id': '123',
        'name': 'first',
        'page': '2',
    }

    _ = connection.get(Test_CID, params)

    request = endpoint.get_request(path + '/items/123/first')
    assert request.query == 'page=2'

# ################################################################################################################################

def test_caller_parameters_unmodified(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The dict the caller gave is not written into, so it can be used for another call.
    """
    connection = new_connection(server, endpoint.http_base, path + _template_suffix)

    params = {
        'item_id': '123',
        'name': 'first',
        'page': '2',
    }

    _ = connection.get(Test_CID, params)
    _ = connection.get(Test_CID, params)

    assert params == {
        'item_id': '123',
        'name': 'first',
        'page': '2',
    }

    requests = endpoint.get_requests(path + '/items/123/first')
    assert len(requests) == 2

# ################################################################################################################################

def test_missing_path_parameter(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A parameter the template names and the caller did not give raises BadRequest with the template and its parameter names,
    and nothing is sent.
    """
    template = path + _template_suffix
    connection = new_connection(server, endpoint.http_base, template)

    with pytest.raises(BadRequest) as info:
        _ = connection.get(Test_CID, {'item_id': '123'})

    assert info.value.msg == f"Could not build URL path template `{template}`, missing parameters: ['item_id', 'name']"
    assert endpoint.get_requests(path + '/items/123') == []

# ################################################################################################################################

def test_no_path_parameters_given(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A template invoked without any parameters raises BadRequest with the template and its parameter names.
    """
    template = path + _template_suffix
    connection = new_connection(server, endpoint.http_base, template)

    with pytest.raises(BadRequest) as info:
        _ = connection.get(Test_CID)

    assert info.value.msg == f"No parameters given for URL path template `{template}`, missing parameters: ['item_id', 'name']"

# ################################################################################################################################
# ################################################################################################################################
