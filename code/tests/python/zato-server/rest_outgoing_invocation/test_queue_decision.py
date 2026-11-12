# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Queue decision - whether a request goes through the queue of its connection, for each combination of the queue switch,
# the transport, the method and the type of the body, decided without the queue itself being involved.

# pytest
import pytest

# requests-toolbelt
from requests_toolbelt import MultipartEncoder

# Zato
from zato.common.api import DATA_FORMAT
from zato.server.connection.http_soap.outgoing.rest_call import _PreparedRequest

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

_read_methods  = ['GET', 'HEAD', 'OPTIONS']
_write_methods = ['POST', 'PUT', 'PATCH', 'DELETE']

# ################################################################################################################################
# ################################################################################################################################

def _needs_queue(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    *,
    use_queue:'bool',
    method:'str',
    data:'any_',
    data_format:'str'='',
    ) -> 'bool':
    """ Prepares a request of a REST connection exactly as a call does and returns whether it would be queued.
    """
    connection = new_connection(server, endpoint.http_base, path, use_queue=use_queue, data_format=data_format)
    prepared = connection._prepare_request(method, Test_CID, data, None, {}, needs_declarative_merge=False)

    out = connection._needs_queue(prepared)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('method', _read_methods + _write_methods)
def test_queue_off(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ Nothing is queued by a connection whose queue switch is off.
    """
    assert not _needs_queue(endpoint, server, path, use_queue=False, method=method, data='Request body')

# ################################################################################################################################

@pytest.mark.parametrize('method', _write_methods)
def test_text_body_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ A request that delivers a text body is queued.
    """
    assert _needs_queue(endpoint, server, path, use_queue=True, method=method, data='Request body')

# ################################################################################################################################

@pytest.mark.parametrize('method', _write_methods)
def test_serialized_body_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ A request whose body the JSON data format serializes to text is queued.
    """
    data = {'customer_id': 123}
    assert _needs_queue(endpoint, server, path, use_queue=True, method=method, data=data, data_format=DATA_FORMAT.JSON)

# ################################################################################################################################

@pytest.mark.parametrize('method', _read_methods)
def test_read_methods_not_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ A request that reads rather than delivers is not queued.
    """
    assert not _needs_queue(endpoint, server, path, use_queue=True, method=method, data='Request body')

# ################################################################################################################################

@pytest.mark.parametrize('method', _write_methods)
def test_bytes_body_not_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ A request with a body in bytes is not queued.
    """
    assert not _needs_queue(endpoint, server, path, use_queue=True, method=method, data=b'Request body')

# ################################################################################################################################

@pytest.mark.parametrize('method', _write_methods)
def test_dict_body_without_data_format_not_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ A request with a dict body that no data format serializes is not queued.
    """
    data = {'customer_id': 123}
    assert not _needs_queue(endpoint, server, path, use_queue=True, method=method, data=data)

# ################################################################################################################################

def test_multipart_body_not_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A request with a multipart body is not queued.
    """
    data = MultipartEncoder(fields={'title': 'Quarterly report'})
    assert not _needs_queue(endpoint, server, path, use_queue=True, method='POST', data=data)

# ################################################################################################################################

@pytest.mark.parametrize('method', _read_methods + _write_methods)
def test_soap_not_queued(endpoint:'TestEndpoint', server:'ServerStub', path:'str', method:'str') -> 'None':
    """ A SOAP request is not queued.
    """
    connection = new_connection(server, endpoint.http_base, path, use_queue=True)

    prepared = _PreparedRequest(
        method=method,
        address=connection.address,
        data=b'<soapenv:Envelope/>',
        headers={},
        qs_params={},
        model=None,
        needs_audit=False,
        is_soap=True,
        data_text='<soapenv:Envelope/>',
        user_headers={},
        params={},
    )

    assert not connection._needs_queue(prepared)

# ################################################################################################################################
# ################################################################################################################################
