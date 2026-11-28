# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The decision of the push engine whether a response to a push is a redirect to follow, and to which address,
# without any network access.

# stdlib
from http.client import BAD_REQUEST, FOUND, INTERNAL_SERVER_ERROR, MOVED_PERMANENTLY, MULTIPLE_CHOICES, NO_CONTENT, \
    NOT_FOUND, NOT_MODIFIED, OK, PERMANENT_REDIRECT, SEE_OTHER, SERVICE_UNAVAILABLE, TEMPORARY_REDIRECT, USE_PROXY

# pytest
import pytest

# Zato - Rust
from zato_server_core.zato_server_core import get_push_redirect, Max_Push_Redirects

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone

# ################################################################################################################################
# ################################################################################################################################

# The address of the subscription that each push starts at
_http_url = 'http://orders.example.com:8080/webhook/orders?tenant=acme'
_https_url = 'https://orders.example.com/webhook/orders'

# The status that the transport reports for 306, which http.client does not name
_switch_proxy = 306

# The network scopes under which redirects are followed
_followed_scopes = ['public', 'private', 'loopback']

# ################################################################################################################################
# ################################################################################################################################

def _redirect(url:'str', location:'strnone', status_code:'int'=TEMPORARY_REDIRECT, hop_count:'int'=0) -> 'strnone':
    """ Returns the decision for one response of a push whose first address is public.
    """
    out = get_push_redirect(url, status_code, location, hop_count, 'public')
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('status_code', [TEMPORARY_REDIRECT, PERMANENT_REDIRECT])
def test_redirect_statuses_are_followed(status_code:'int') -> 'None':
    next_url = _redirect(_http_url, 'http://archive.example.com/webhook/orders', status_code)
    assert next_url == 'http://archive.example.com/webhook/orders'

# ################################################################################################################################

@pytest.mark.parametrize('status_code', [
    OK, NO_CONTENT, MULTIPLE_CHOICES, MOVED_PERMANENTLY, FOUND, SEE_OTHER, NOT_MODIFIED, USE_PROXY, _switch_proxy,
    BAD_REQUEST, NOT_FOUND, INTERNAL_SERVER_ERROR, SERVICE_UNAVAILABLE,
])
def test_other_statuses_are_not_redirects(status_code:'int') -> 'None':
    next_url = _redirect(_http_url, 'http://archive.example.com/webhook/orders', status_code)
    assert next_url is None

# ################################################################################################################################

@pytest.mark.parametrize(('url', 'location', 'expected'), [

    # An absolute address, another host, another port and an IPv6 literal ..
    (_http_url, 'http://orders.example.com:8080/webhook/v2', 'http://orders.example.com:8080/webhook/v2'),
    (_http_url, 'http://archive.example.net/webhook/orders', 'http://archive.example.net/webhook/orders'),
    (_http_url, 'http://orders.example.com:9090/webhook/orders', 'http://orders.example.com:9090/webhook/orders'),
    (_http_url, 'http://[2001:db8::10]:8443/webhook', 'http://[2001:db8::10]:8443/webhook'),

    # .. a path, a relative path and a query alone ..
    (_http_url, '/other', 'http://orders.example.com:8080/other'),
    (_http_url, 'other', 'http://orders.example.com:8080/webhook/other'),
    (_http_url, '../other', 'http://orders.example.com:8080/other'),
    (_http_url, '?page=2', 'http://orders.example.com:8080/webhook/orders?page=2'),

    # .. a scheme-relative address, which inherits the scheme ..
    (_http_url, '//archive.example.com/webhook', 'http://archive.example.com/webhook'),
    (_https_url, '//archive.example.com/webhook', 'https://archive.example.com/webhook'),

    # .. an upgrade from HTTP to HTTPS ..
    (_http_url, 'https://orders.example.com/webhook/orders', 'https://orders.example.com/webhook/orders'),

    # .. a scheme in upper case, which is lowercased ..
    (_http_url, 'HTTPS://archive.example.com/webhook', 'https://archive.example.com/webhook'),
    (_https_url, 'HTTPS://archive.example.com/webhook', 'https://archive.example.com/webhook'),

    # .. and a fragment, which is removed.
    (_http_url, '/other#section', 'http://orders.example.com:8080/other'),
    (_http_url, 'http://archive.example.com/webhook?page=2#top', 'http://archive.example.com/webhook?page=2'),
])
def test_location_forms(url:'str', location:'str', expected:'str') -> 'None':
    next_url = _redirect(url, location)
    assert next_url == expected

# ################################################################################################################################

@pytest.mark.parametrize(('url', 'location'), [

    # A missing or empty Location ..
    (_http_url, None),
    (_http_url, ''),

    # .. a scheme other than HTTP and HTTPS ..
    (_http_url, 'ftp://files.example.com/orders'),
    (_http_url, 'file:///etc/hosts'),
    (_http_url, 'javascript:alert(1)'),
    (_http_url, 'market://details?id=42'),

    # .. user information ..
    (_http_url, 'http://john.smith:Test.2026@archive.example.com/webhook'),
    (_http_url, 'http://john.smith@archive.example.com/webhook'),

    # .. HTTP after HTTPS, absolute and scheme-relative ..
    (_https_url, 'http://orders.example.com/webhook/orders'),
    (_https_url, 'http://archive.example.com/webhook'),

    # .. a missing host ..
    (_http_url, 'https://:443/'),
    (_http_url, 'http://:1'),

    # .. an invalid port ..
    (_http_url, 'http://archive.example.com:0/webhook'),
    (_http_url, 'http://archive.example.com:70000/webhook'),
    (_http_url, 'http://archive.example.com:http/webhook'),

    # .. whitespace and line breaks ..
    (_http_url, 'http://archive.example.com/web hook'),
    (_http_url, ' http://archive.example.com/webhook'),
    (_http_url, 'http://archive.example.com/webhook\t'),
    (_http_url, 'http://archive.example.com/webhook\r\nX-Test: 1'),
    (_http_url, 'http://archive.example.com/webhook\n'),

    # .. and characters outside ASCII, in the host and in the path.
    (_http_url, 'http://archivé.example.com/webhook'),
    (_http_url, 'http://archive.example.com/šablona'),
    (_http_url, 'http://archive.example.com/webhook\x7f'),
])
def test_redirects_not_followed(url:'str', location:'strnone') -> 'None':
    with pytest.raises(ValueError):
        _ = _redirect(url, location)

# ################################################################################################################################

@pytest.mark.parametrize('status_code', [TEMPORARY_REDIRECT, PERMANENT_REDIRECT])
def test_hop_limit(status_code:'int') -> 'None':

    # The last redirect within the limit is followed ..
    last_hop = Max_Push_Redirects - 1
    next_url = _redirect(_http_url, '/other', status_code, last_hop)

    assert next_url == 'http://orders.example.com:8080/other'

    # .. and the one after it is not.
    with pytest.raises(ValueError):
        _ = _redirect(_http_url, '/other', status_code, Max_Push_Redirects)

# ################################################################################################################################

@pytest.mark.parametrize('first_scope', _followed_scopes)
def test_scopes_of_followed_redirects(first_scope:'str') -> 'None':
    next_url = get_push_redirect(_http_url, TEMPORARY_REDIRECT, '/other', 0, first_scope)
    assert next_url == 'http://orders.example.com:8080/other'

# ################################################################################################################################

@pytest.mark.parametrize('first_scope', ['link-local', None])
def test_scopes_of_redirects_not_followed(first_scope:'strnone') -> 'None':
    with pytest.raises(ValueError):
        _ = get_push_redirect(_http_url, TEMPORARY_REDIRECT, '/other', 0, first_scope)

# ################################################################################################################################

@pytest.mark.parametrize('first_scope', ['link-local', None])
def test_scope_does_not_apply_to_other_statuses(first_scope:'strnone') -> 'None':
    next_url = get_push_redirect(_http_url, OK, '/other', 0, first_scope)
    assert next_url is None

# ################################################################################################################################
# ################################################################################################################################
