# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Response identity - the response of a call is a response of the requests library, with its representation,
# its truth value and the attributes a caller assigns to it, and it is assigned as a service payload as such.

# stdlib
from http.client import NOT_FOUND, OK

# pytest
import pytest

# requests
from requests import Response as RequestsResponse

# Zato
from zato.common.api import DATA_FORMAT
from zato.server.reqresp.response import Response as ServiceResponse

# Test support
from endpoint import EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def _new_service_response() -> 'ServiceResponse':
    """ Returns the response of a service without I/O declarations, as a JSON channel invokes it with.
    """
    out = ServiceResponse()
    out.init(Test_CID, None, DATA_FORMAT.JSON)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_instance_and_repr(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The response is a response of the requests library, represented by its status code.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    assert isinstance(response, RequestsResponse)
    assert repr(response) == '<Response [200]>'

# ################################################################################################################################

@pytest.mark.parametrize(('status', 'is_true'), [(OK, True), (NOT_FOUND, False)])
def test_truth_value(endpoint:'TestEndpoint', server:'ServerStub', path:'str', status:'int', is_true:'bool') -> 'None':
    """ The response is true when it is successful and false otherwise.
    """
    endpoint.set_response(path, EndpointResponse(status))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    assert bool(response) is is_true

# ################################################################################################################################

def test_assigned_attributes(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A caller assigns attributes of its own to the response.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response:'any_' = connection.get(Test_CID)

    response.customer_id = 123
    response.data = {'replaced': True}

    assert response.customer_id == 123
    assert response.data == {'replaced': True}

# ################################################################################################################################

def test_successful_response_as_payload(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A successful response assigned as the payload of a service without I/O declarations is rejected as not serializable.
    """
    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)
    service_response = _new_service_response()

    with pytest.raises(Exception) as info:
        service_response.payload = response

    assert info.value.args[0] == 'Cannot serialise value without I/O output declaration (<Response [200]>)'

# ################################################################################################################################

def test_error_response_as_payload(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An error response assigned as the payload of a service without I/O declarations leaves the payload unchanged.
    """
    endpoint.set_response(path, EndpointResponse(NOT_FOUND))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    service_response = _new_service_response()
    payload_before = service_response.payload

    service_response.payload = response

    assert service_response.payload is payload_before

# ################################################################################################################################

def test_data_as_payload(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The parsed data of a response assigned as the payload of a service is the payload.
    """
    endpoint.set_response(path, EndpointResponse(body='{"customer_id": 123}', headers=[('Content-Type', 'application/json')]))

    connection = new_connection(server, endpoint.http_base, path)

    response = connection.get(Test_CID)

    service_response = _new_service_response()
    service_response.payload = response.data

    assert service_response.payload == {'customer_id': 123}

# ################################################################################################################################
# ################################################################################################################################
