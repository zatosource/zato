# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redirects - a redirect returned to the caller without being followed, unless the caller explicitly asks for it
# to be followed, with the redirect argument accepted by every method.

# stdlib
from http.client import FOUND, MOVED_PERMANENTLY, OK, PERMANENT_REDIRECT, TEMPORARY_REDIRECT

# pytest
import pytest

# Zato
from zato.common.api import ContentType

# Test support
from endpoint import EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The body the redirect target answers with
_target_body = 'Redirect target response'

# ################################################################################################################################
# ################################################################################################################################

def _set_redirect(endpoint:'TestEndpoint', path:'str', status:'int') -> 'str':
    """ Makes the path redirect to a target path under it and returns the address of the target.
    """
    target_path = path + '/target'
    target_address = endpoint.http_base + target_path

    endpoint.set_response(path, EndpointResponse(status, headers=[('Location', target_address)]))
    endpoint.set_response(target_path, EndpointResponse(body=_target_body))

    return target_path

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('status', [MOVED_PERMANENTLY, FOUND, TEMPORARY_REDIRECT, PERMANENT_REDIRECT])
def test_redirect_not_followed(endpoint:'TestEndpoint', server:'ServerStub', path:'str', status:'int') -> 'None':
    """ A redirect is returned to the caller as it is, and its target is not invoked.
    """
    target_path = _set_redirect(endpoint, path, status)

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert response.status_code == status
    assert response.headers['Location'] == endpoint.http_base + target_path
    assert endpoint.get_requests(target_path) == []

# ################################################################################################################################

@pytest.mark.parametrize('status', [MOVED_PERMANENTLY, FOUND, TEMPORARY_REDIRECT, PERMANENT_REDIRECT])
def test_redirect_not_followed_post(endpoint:'TestEndpoint', server:'ServerStub', path:'str', status:'int') -> 'None':
    """ A redirect of a request with a body is returned to the caller as it is, and its target is not invoked.
    """
    target_path = _set_redirect(endpoint, path, status)

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.post(Test_CID, {'customer_id': 123})

    assert response.status_code == status
    assert endpoint.get_requests(target_path) == []

# ################################################################################################################################

def test_redirect_argument_false_get(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A caller that says redirects are not followed receives the redirect with its target in the Location header.
    """
    target_path = _set_redirect(endpoint, path, FOUND)

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID, allow_redirects=False)

    assert response.status_code == FOUND
    assert response.headers.get('Location') == endpoint.http_base + target_path
    assert endpoint.get_requests(target_path) == []

# ################################################################################################################################

def test_redirect_argument_true_get(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A caller that says redirects are followed receives the response of the target.
    """
    target_path = _set_redirect(endpoint, path, FOUND)

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID, allow_redirects=True)

    assert response.status_code == OK
    assert response.text == _target_body

    request = endpoint.get_request(target_path)
    assert request.method == 'GET'

# ################################################################################################################################

def test_redirect_argument_false_post_form(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A form posted by a caller that says redirects are not followed receives the redirect with its target in the Location header.
    """
    target_path = _set_redirect(endpoint, path, FOUND)

    connection = new_connection(server, endpoint.http_base, path)

    headers = {'Content-Type': ContentType.FormURLEncoded}
    response = connection.post(Test_CID, 'username=john.smith&password=Test.2026', headers=headers, allow_redirects=False)

    assert response.status_code == FOUND
    assert response.headers.get('Location') == endpoint.http_base + target_path

    request = endpoint.get_request(path)
    assert request.body == b'username=john.smith&password=Test.2026'
    assert request.get_header('Content-Type') == ContentType.FormURLEncoded

    assert endpoint.get_requests(target_path) == []

# ################################################################################################################################

def test_redirect_argument_true_post_form(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A form posted by a caller that says redirects are followed receives the response of the target,
    which a 302 redirect makes requests invoke with GET.
    """
    target_path = _set_redirect(endpoint, path, FOUND)

    connection = new_connection(server, endpoint.http_base, path)

    headers = {'Content-Type': ContentType.FormURLEncoded}
    response = connection.post(Test_CID, 'username=john.smith&password=Test.2026', headers=headers, allow_redirects=True)

    assert response.status_code == OK
    assert response.text == _target_body

    request = endpoint.get_request(target_path)
    assert request.method == 'GET'

# ################################################################################################################################
# ################################################################################################################################
