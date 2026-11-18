# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Rust transport sends exactly what requests sends - the same request line, the same headers in the same order
# and the same body, directly and through an HTTP proxy from the environment, in absolute form for http endpoints
# and through a CONNECT tunnel for https endpoints, and it raises the same errors when the proxy refuses a request.

# stdlib
from base64 import b64encode
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.api import ContentType
from zato.server.connection.http_soap.outgoing.transport import Transport_Env_Key, Transport_Requests, TransportResponse

# Test support
from endpoint import Host
from proxy import Proxy_Response_Body, TestProxy
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from endpoint import RecordedRequest, TestEndpoint
    from support import ServerStub
    from zato.common.typing_ import any_, anytuple
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

    proxygen = Iterator[TestProxy]

# ################################################################################################################################
# ################################################################################################################################

# Every environment variable that names a proxy or the hosts reached without one
_proxy_env_keys = ('http_proxy', 'https_proxy', 'all_proxy', 'no_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY')

# The credentials of the proxy, as they appear in its address
_proxy_username = 'proxy.user'
_proxy_password = 'Proxy.Password.2026'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def proxy() -> 'proxygen':
    """ A new proxy for each test, so each test reads only the requests it sent.
    """
    out = TestProxy()
    out.start()

    yield out

    out.stop()

# ################################################################################################################################

@pytest.fixture
def authenticating_proxy() -> 'proxygen':
    """ A new proxy for each test that requires the credentials of the suite.
    """
    credentials = f'{_proxy_username}:{_proxy_password}'.encode('ascii')
    authorization = 'Basic ' + b64encode(credentials).decode('ascii')

    out = TestProxy(authorization)
    out.start()

    yield out

    out.stop()

# ################################################################################################################################
# ################################################################################################################################

def _set_environment_proxy(monkeypatch:'pytest.MonkeyPatch', proxy_url:'str', no_proxy:'str'='') -> 'None':
    """ Names the proxy in the environment of the process, for both http and https endpoints.
    """
    for key in _proxy_env_keys:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv('HTTP_PROXY', proxy_url)
    monkeypatch.setenv('HTTPS_PROXY', proxy_url)

    if no_proxy:
        monkeypatch.setenv('NO_PROXY', no_proxy)

# ################################################################################################################################

def _new_connection_pair(
    monkeypatch:'pytest.MonkeyPatch',
    server:'ServerStub',
    address_host:'str',
    path:'str',
    **kwargs:'any_',
    ) -> 'tuple[HTTPSOAPWrapper, HTTPSOAPWrapper]':
    """ Returns two connections built from the same configuration - one that sends through the Rust transport
    and one built while the environment selects requests.
    """
    through_transport = new_connection(server, address_host, path, **kwargs)

    monkeypatch.setenv(Transport_Env_Key, Transport_Requests)
    through_requests = new_connection(server, address_host, path, **kwargs)
    monkeypatch.delenv(Transport_Env_Key)

    out = (through_transport, through_requests)
    return out

# ################################################################################################################################

def _as_sent(request:'RecordedRequest') -> 'anytuple':
    """ Returns everything of a request that went over the wire.
    """
    out = (request.method, request.target, request.version, request.headers, request.body)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_http_through_proxy(
    monkeypatch:'pytest.MonkeyPatch',
    endpoint:'TestEndpoint',
    server:'ServerStub',
    proxy:'TestProxy',
    path:'str',
    ) -> 'None':
    """ A request to an http endpoint goes to the proxy of the environment in absolute form, the same as requests sends it.
    """
    _set_environment_proxy(monkeypatch, proxy.url())
    through_transport, through_requests = _new_connection_pair(monkeypatch, server, endpoint.http_base, path)

    transport_response = through_transport.get(Test_CID, {'page': '2'})
    requests_response = through_requests.get(Test_CID, {'page': '2'})

    assert isinstance(transport_response, TransportResponse)
    assert not isinstance(requests_response, TransportResponse)

    assert transport_response.status_code == requests_response.status_code == OK
    assert transport_response.content == requests_response.content == Proxy_Response_Body
    assert transport_response.url == requests_response.url

    first, second = proxy.requests

    assert first.target == f'http://{Host}:{endpoint.http_port}{path}?page=2'
    assert _as_sent(first) == _as_sent(second)

# ################################################################################################################################

def test_http_through_proxy_with_credentials(
    monkeypatch:'pytest.MonkeyPatch',
    endpoint:'TestEndpoint',
    server:'ServerStub',
    authenticating_proxy:'TestProxy',
    path:'str',
    ) -> 'None':
    """ The credentials in the address of the proxy are sent in a Proxy-Authorization header, the same as requests sends them.
    """
    proxy_url = authenticating_proxy.url(f'{_proxy_username}:{_proxy_password}')

    _set_environment_proxy(monkeypatch, proxy_url)
    through_transport, through_requests = _new_connection_pair(monkeypatch, server, endpoint.http_base, path)

    transport_response = through_transport.post(Test_CID, 'Request body')
    requests_response = through_requests.post(Test_CID, 'Request body')

    assert isinstance(transport_response, TransportResponse)
    assert transport_response.status_code == requests_response.status_code == OK

    first, second = authenticating_proxy.requests

    assert first.get_header('Proxy-Authorization') == authenticating_proxy.authorization
    assert _as_sent(first) == _as_sent(second)

# ################################################################################################################################

def test_https_through_tunnel(
    monkeypatch:'pytest.MonkeyPatch',
    endpoint:'TestEndpoint',
    server:'ServerStub',
    authenticating_proxy:'TestProxy',
    path:'str',
    ) -> 'None':
    """ A request to an https endpoint goes through a tunnel the proxy opens, with the same CONNECT request
    and the same request inside the tunnel as requests sends.
    """
    proxy_url = authenticating_proxy.url(f'{_proxy_username}:{_proxy_password}')
    ca_path = endpoint.certificates.ca_path

    _set_environment_proxy(monkeypatch, proxy_url)
    through_transport, through_requests = _new_connection_pair(
        monkeypatch, server, endpoint.https_base, path, ca_certs_path=ca_path)

    transport_response = through_transport.get(Test_CID)
    requests_response = through_requests.get(Test_CID)

    assert isinstance(transport_response, TransportResponse)
    assert transport_response.status_code == requests_response.status_code == OK

    first_connect, second_connect = authenticating_proxy.requests

    assert first_connect.method == 'CONNECT'
    assert first_connect.target == f'{Host}:{endpoint.https_port}'
    assert _as_sent(first_connect) == _as_sent(second_connect)

    first, second = endpoint.get_requests(path)
    assert _as_sent(first) == _as_sent(second)

# ################################################################################################################################

def test_tunnel_refused(
    monkeypatch:'pytest.MonkeyPatch',
    endpoint:'TestEndpoint',
    server:'ServerStub',
    authenticating_proxy:'TestProxy',
    path:'str',
    ) -> 'None':
    """ A proxy that refuses to open a tunnel fails the request with the same error requests raises.
    """
    _set_environment_proxy(monkeypatch, authenticating_proxy.url())
    through_transport, through_requests = _new_connection_pair(
        monkeypatch, server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.ca_path)

    with pytest.raises(Exception) as transport_info:
        _ = through_transport.get(Test_CID)

    with pytest.raises(Exception) as requests_info:
        _ = through_requests.get(Test_CID)

    assert type(transport_info.value) is type(requests_info.value)
    assert transport_info.value.args == requests_info.value.args
    assert 'Tunnel connection failed: 407 Proxy Authentication Required' in str(transport_info.value)

# ################################################################################################################################

def test_proxy_bypassed_for_no_proxy_host(
    monkeypatch:'pytest.MonkeyPatch',
    endpoint:'TestEndpoint',
    server:'ServerStub',
    proxy:'TestProxy',
    path:'str',
    ) -> 'None':
    """ A host the environment lists as reached without a proxy is invoked directly.
    """
    _set_environment_proxy(monkeypatch, proxy.url(), no_proxy=Host)
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert isinstance(response, TransportResponse)
    assert proxy.requests == []
    assert len(endpoint.get_requests(path)) == 1

# ################################################################################################################################

def test_json_body(monkeypatch:'pytest.MonkeyPatch', endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A body given as the json argument is encoded and sent with its Content-Type, the same as requests sends it.
    """
    through_transport, through_requests = _new_connection_pair(monkeypatch, server, endpoint.http_base, path)
    value = {'customer': 'Zażółć gęślą jaźń', 'amount': 249.5, 'items': [1, 2, 3]}

    transport_response = through_transport.post(Test_CID, json=value)
    _ = through_requests.post(Test_CID, json=value)

    assert isinstance(transport_response, TransportResponse)

    first, second = endpoint.get_requests(path)
    assert _as_sent(first) == _as_sent(second)

# ################################################################################################################################

def test_form_body(monkeypatch:'pytest.MonkeyPatch', endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A dict given to a form-urlencoded connection is encoded as a form, the same as requests encodes it.
    """
    through_transport, through_requests = _new_connection_pair(
        monkeypatch, server, endpoint.http_base, path, content_type=ContentType.FormURLEncoded)

    data = {'name': 'John Smith', 'city': 'Zürich', 'customer_id': 123}

    transport_response = through_transport.post(Test_CID, data)
    _ = through_requests.post(Test_CID, data)

    assert isinstance(transport_response, TransportResponse)

    first, second = endpoint.get_requests(path)
    assert _as_sent(first) == _as_sent(second)

# ################################################################################################################################

def test_address_without_path(monkeypatch:'pytest.MonkeyPatch', endpoint:'TestEndpoint', server:'ServerStub') -> 'None':
    """ An address without a path is sent to the root path, the same as requests sends it.
    """
    through_transport, through_requests = _new_connection_pair(monkeypatch, server, endpoint.http_base, '')

    transport_response = through_transport.get(Test_CID)
    _ = through_requests.get(Test_CID)

    assert isinstance(transport_response, TransportResponse)
    assert transport_response.url == f'http://{Host}:{endpoint.http_port}/'

    first, second = endpoint.get_requests('/')[-2:]
    assert _as_sent(first) == _as_sent(second)

# ################################################################################################################################
# ################################################################################################################################
