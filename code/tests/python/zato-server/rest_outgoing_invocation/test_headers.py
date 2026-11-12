# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The headers of a request - the ones every request has, the default content type of each kind of connection,
# and the caller's own headers, which win over the defaults and are sent exactly as given.

# stdlib
from datetime import datetime

# pytest
import pytest

# requests
from requests.exceptions import InvalidHeader
from requests.utils import default_user_agent, DEFAULT_ACCEPT_ENCODING

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.util.api import get_component_name

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_headers_of_every_request(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Every request has the CID, the component it came from and the time it was made, along with the headers
    that requests sends by default.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)

    assert request.get_header('X-Zato-CID') == Test_CID
    assert request.get_header('X-Zato-Component') == get_component_name()

    message_timestamp = request.get_header('X-Zato-Msg-TS')
    assert message_timestamp is not None
    _ = datetime.fromisoformat(message_timestamp)

    assert request.get_header('User-Agent') == default_user_agent()
    assert request.get_header('Accept') == '*/*'
    assert request.get_header('Accept-Encoding') == DEFAULT_ACCEPT_ENCODING
    assert request.get_header('Connection') == 'keep-alive'

# ################################################################################################################################

@pytest.mark.parametrize(('content_type', 'data_format', 'expected'), [
    ('', '', 'text/plain'),
    ('', DATA_FORMAT.JSON, 'application/json'),
    ('', DATA_FORMAT.FORM_DATA, 'application/json'),
    ('application/vnd.api+json', DATA_FORMAT.JSON, 'application/vnd.api+json'),
    ('application/xml', '', 'application/xml'),
])
def test_default_content_type(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    content_type:'str',
    data_format:'str',
    expected:'str',
    ) -> 'None':
    """ A connection with an explicit content type sends it, one with a data format sends JSON, and one with neither sends plain text.
    """
    connection = new_connection(server, endpoint.http_base, path, content_type=content_type, data_format=data_format)

    _ = connection.post(Test_CID, 'Test request body')

    request = endpoint.get_request(path)
    assert request.get_header_list('Content-Type') == [expected]

# ################################################################################################################################

def test_caller_content_type_wins(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A Content-Type header of the caller replaces the default one.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    _ = connection.post(Test_CID, '<order/>', headers={'Content-Type': 'application/xml'})

    request = endpoint.get_request(path)
    assert request.get_header_list('Content-Type') == ['application/xml']

# ################################################################################################################################

def test_caller_content_type_in_lower_case(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A content type header of the caller spelled in lower case is sent once, with the caller's value.
    """
    connection = new_connection(server, endpoint.http_base, path, data_format=DATA_FORMAT.JSON)

    _ = connection.post(Test_CID, '<order/>', headers={'content-type': 'application/xml'})

    request = endpoint.get_request(path)
    assert request.get_header_list('Content-Type') == ['application/xml']

# ################################################################################################################################

def test_caller_headers_win_over_defaults(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The caller's headers replace the headers that requests sends by default, and so do the caller's own Zato headers.
    """
    connection = new_connection(server, endpoint.http_base, path)

    headers = {
        'User-Agent': 'Test-Client/1.0',
        'Accept': 'application/xml',
        'X-Zato-Component': 'test.component',
        'X-Custom-Header': 'Test value',
    }

    _ = connection.get(Test_CID, headers=headers)

    request = endpoint.get_request(path)

    assert request.get_header_list('User-Agent') == ['Test-Client/1.0']
    assert request.get_header_list('Accept') == ['application/xml']
    assert request.get_header_list('X-Zato-Component') == ['test.component']
    assert request.get_header('X-Custom-Header') == 'Test value'

# ################################################################################################################################

def test_caller_headers_unmodified(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The dict of headers the caller gave is not written into, so a content type in it applies to each call it is used for.
    """
    connection = new_connection(server, endpoint.http_base, path)

    headers = {
        'Content-Type': 'application/xml',
        'X-Custom-Header': 'Test value',
    }

    _ = connection.post(Test_CID, '<order/>', headers=headers)
    _ = connection.post(Test_CID, '<order/>', headers=headers)

    assert headers == {
        'Content-Type': 'application/xml',
        'X-Custom-Header': 'Test value',
    }

    requests = endpoint.get_requests(path)
    assert len(requests) == 2

    for item in requests:
        assert item.get_header('Content-Type') == 'application/xml'
        assert item.get_header('X-Custom-Header') == 'Test value'

# ################################################################################################################################

def test_empty_header_value(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A header with an empty value is sent as an empty header.
    """
    connection = new_connection(server, endpoint.http_base, path)

    _ = connection.get(Test_CID, headers={'Cookie': '', 'X-Empty': ''})

    request = endpoint.get_request(path)

    assert request.get_header_list('Cookie') == ['']
    assert request.get_header_list('X-Empty') == ['']

# ################################################################################################################################

def test_cid_that_is_a_url(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Any text can be a CID, including a URL, and it is sent as it is.
    """
    connection = new_connection(server, endpoint.http_base, path)
    cid = 'https://api.example.com/v1/items?id=1&page=2'

    _ = connection.get(cid)

    request = endpoint.get_request(path)
    assert request.get_header('X-Zato-CID') == cid

# ################################################################################################################################

@pytest.mark.parametrize('value', ['Test\r\nX-Injected: value', 'Test\nvalue', ' Test value'])
def test_invalid_header_value(endpoint:'TestEndpoint', server:'ServerStub', path:'str', value:'str') -> 'None':
    """ A header value with a line break or with leading whitespace is rejected before anything is sent.
    """
    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(InvalidHeader):
        _ = connection.get(Test_CID, headers={'X-Custom-Header': value})

    assert endpoint.get_requests(path) == []

# ################################################################################################################################

def test_header_value_that_is_not_text(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A header value that is neither text nor bytes is rejected before anything is sent.
    """
    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(InvalidHeader):
        _ = connection.get(Test_CID, headers={'X-Number': 123})

    assert endpoint.get_requests(path) == []

# ################################################################################################################################
# ################################################################################################################################
