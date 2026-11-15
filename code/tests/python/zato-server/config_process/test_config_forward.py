# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# pytest
import pytest

# Zato
from zato.common.exception import Reportable, ZatoException
from zato.common.json_internal import dumps
from zato.common.typing_ import cast_
from zato.server.config_forward import apply_forward_result, describe_error, get_http_request_ctx, new_forward_body, \
    raise_error
from zato.server.reqresp.response import Response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    from zato.server.service import Service

    any_ = any_
    anydict = anydict
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

class RequestStub:
    def __init__(self, raw_request:'any_') -> 'None':
        self.raw_request = raw_request

# ################################################################################################################################

class ServiceStub:
    """ The attributes of a service object that the forwarding of an invocation reads and writes.
    """
    def __init__(self, raw_request:'any_') -> 'None':
        self.name = 'zato.security.basic-auth.create'
        self.cid = 'cid-1'
        self.data_format = 'json'
        self.transport = 'plain_http'
        self.request = RequestStub(raw_request)
        self.response = Response()

# ################################################################################################################################

def _new_service(raw_request:'any_') -> 'Service':
    out = cast_('Service', ServiceStub(raw_request))
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_http_parts_of_a_request_context_are_kept() -> 'None':
    request_ctx:'anydict' = {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/zato/admin/invoke',
        'HTTP_X_ZATO_CHANNEL': 'dashboard',
        'zato.http.GET': {'a': '1'},
        'zato.http.path_params': {'id': '7'},
        'wsgi.input': object(),
        'zato.channel_item': {'name': 'admin'},
    }

    out = get_http_request_ctx(request_ctx)

    assert out == {
        'REQUEST_METHOD': 'POST',
        'PATH_INFO': '/zato/admin/invoke',
        'HTTP_X_ZATO_CHANNEL': 'dashboard',
        'zato.http.GET': {'a': '1'},
        'zato.http.path_params': {'id': '7'},
    }

# ################################################################################################################################

@pytest.mark.parametrize('raw_request, payload, is_text', [
    (b'{"name": "a"}', '{"name": "a"}', True),
    ('{"name": "a"}', '{"name": "a"}', True),
    ({'name': 'a'}, '{"name": "a"}', False),
])
def test_the_body_of_a_forward_carries_the_request_as_text_or_json(raw_request:'any_', payload:'str', is_text:'bool') -> 'None':
    service = _new_service(raw_request)

    out = new_forward_body(service, 'http-soap', {'REQUEST_METHOD': 'POST'})

    assert out['name'] == 'zato.security.basic-auth.create'
    assert out['cid'] == 'cid-1'
    assert out['channel'] == 'http-soap'
    assert out['data_format'] == 'json'
    assert out['transport'] == 'plain_http'
    assert out['is_text'] is is_text
    assert loads(out['payload']) == loads(payload)
    assert loads(out['request_ctx']) == {'REQUEST_METHOD': 'POST'}

# ################################################################################################################################

def test_a_reportable_exception_is_raised_again_in_the_worker() -> 'None':
    error = describe_error(Reportable('cid-1', 'Not allowed', 403, True))

    with pytest.raises(Reportable) as info:
        raise_error('cid-2', error)

    assert info.value.cid == 'cid-2'
    assert info.value.msg == 'Not allowed'
    assert info.value.status == 403
    assert info.value.needs_msg is True

# ################################################################################################################################

def test_a_zato_exception_is_raised_again_in_the_worker() -> 'None':
    error = describe_error(ZatoException('cid-1', 'Definition exists'))

    with pytest.raises(ZatoException) as info:
        raise_error('cid-2', error)

    assert not isinstance(info.value, Reportable)
    assert info.value.msg == 'Definition exists'

# ################################################################################################################################

def test_any_other_exception_is_raised_again_with_its_message() -> 'None':
    error = describe_error(ValueError('Missing required input element: password'))

    with pytest.raises(Exception) as info:
        raise_error('cid-2', error)

    assert not isinstance(info.value, ZatoException)
    assert str(info.value) == 'Missing required input element: password'

# ################################################################################################################################

def test_the_result_of_a_forward_becomes_the_response_of_the_worker() -> 'None':
    service = _new_service(None)

    result:'anydict' = {
        'payload': dumps({'zato_security_basic_auth_create_response': {'id': 7, 'name': 'a'}}),
        'status_code': 201,
        'headers': dumps({'X-Probe': '1'}),
        'content_type': 'application/json',
        'content_type_changed': True,
    }

    apply_forward_result(service, result)

    assert service.response.payload == {'zato_security_basic_auth_create_response': {'id': 7, 'name': 'a'}}
    assert service.response.status_code == 201
    assert service.response.headers == {'X-Probe': '1'}
    assert service.response.content_type == 'application/json'

# ################################################################################################################################

def test_a_content_type_left_unchanged_in_the_config_process_is_left_unchanged_in_the_worker() -> 'None':
    service = _new_service(None)
    default_content_type = service.response.content_type

    result:'anydict' = {
        'payload': dumps(''),
        'status_code': 200,
        'headers': dumps({}),
        'content_type': 'application/xml',
        'content_type_changed': False,
    }

    apply_forward_result(service, result)

    assert service.response.content_type == default_content_type
    assert not service.response.content_type_changed

# ################################################################################################################################

def test_an_error_result_raises_in_the_worker() -> 'None':
    service = _new_service(None)

    result:'anydict' = {'error': describe_error(ZatoException('cid-1', 'Definition exists'))}

    with pytest.raises(ZatoException):
        apply_forward_result(service, result)

# ################################################################################################################################
# ################################################################################################################################
