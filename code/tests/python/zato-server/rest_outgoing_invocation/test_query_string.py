# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The query string of a request - the parameters the caller gave, encoded the way an HTML form encodes them.

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_parameters_encoded(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Each parameter becomes a key and a value of the query string, in the order given, with numbers sent as text.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID, {'q': 'abc', 'page': 2})

    request = endpoint.get_request(path)
    assert request.query == 'q=abc&page=2'

    assert response.zato_qs_params == {'q': 'abc', 'page': 2}

# ################################################################################################################################

def test_repeated_keys(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A list of values repeats its key once per value.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, {'tag': ['first', 'second'], 'page': '1'})

    request = endpoint.get_request(path)
    assert request.query == 'tag=first&tag=second&page=1'

# ################################################################################################################################

def test_non_ascii_and_reserved_values(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Non-ASCII values are sent as the percent-encoded bytes of their UTF-8 form, spaces as plus signs,
    and the characters that separate parameters are encoded.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, {'city': 'Zürich', 'name': 'John Smith', 'filter': 'a=b&c'})

    request = endpoint.get_request(path)
    assert request.query == 'city=Z%C3%BCrich&name=John+Smith&filter=a%3Db%26c'

# ################################################################################################################################

def test_empty_and_none_values(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An empty value is sent with its key, and a value of None is not sent at all.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, {'empty': '', 'absent': None, 'page': '1'})

    request = endpoint.get_request(path)
    assert request.query == 'empty=&page=1'

# ################################################################################################################################

def test_empty_dict(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An empty dict sends no query string at all.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, {})

    request = endpoint.get_request(path)

    assert request.target == path
    assert request.query == ''

# ################################################################################################################################

def test_combined_with_path_parameters(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Parameters a template names fill in the path while all the others form the query string.
    """
    connection = new_connection(server, endpoint.http_base, path + '/customers/{customer_id}')

    response = connection.get(Test_CID, {'customer_id': 'C-100', 'status': 'active', 'limit': 10})

    request = endpoint.get_request(path + '/customers/C-100')
    assert request.query == 'status=active&limit=10'

    assert response.zato_qs_params == {'status': 'active', 'limit': 10}

# ################################################################################################################################
# ################################################################################################################################
