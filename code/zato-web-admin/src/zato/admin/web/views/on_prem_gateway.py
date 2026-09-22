# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import on_prem_gateway_page_config
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, strdict, strdictnone

    # Dummy assignments to satisfy type checkers
    strdict = strdict
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_service_prefix = 'zato.on-prem-gateway.'

_template = 'zato/settings/on-prem-gateway/index.html'

# ################################################################################################################################
# ################################################################################################################################

def json_response(data:'strdict', success:'bool'=True) -> 'HttpResponse':

    response_json = dumps(data)

    if success:
        response_class = HttpResponse
    else:
        response_class = HttpResponseServerError

    out = response_class(response_json, content_type='application/json')

    return out

# ################################################################################################################################

def error_response(error:'str') -> 'HttpResponse':

    data = {'success': False, 'error': error}
    out = json_response(data, success=False)

    return out

# ################################################################################################################################

def _invoke(req:'HttpRequest', service:'str', request_data:'strdictnone'=None) -> 'strdict':
    """ Invokes one of the on-premises gateway services and returns what came back.
    """
    if request_data is None:
        request_data = {}

    response = req.zato.client.invoke(_service_prefix + service, request_data)

    if response.ok:
        out = {'success': True, 'data': response.data}
        return out

    logger.error('on_prem_gateway %s: invoke failed: %s', service, response)

    out = {'success': False, 'error': str(response.details)}

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'HttpRequest') -> 'any_':

    gateways = []

    try:
        response = _invoke(req, 'get-list')

        if response['success']:
            gateways = response['data']

    except Exception:
        logger.error('on_prem_gateway index: %s', format_exc())

    context = {
        'page_config': on_prem_gateway_page_config,
        'gateways': gateways,
        'gateways_json': dumps(gateways),
    }

    out = TemplateResponse(req, _template, context)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_list(req:'HttpRequest') -> 'HttpResponse':
    """ The list of gateways on its own.
    """
    try:
        response = _invoke(req, 'get-list')
        out = json_response(response, success=response['success'])

        return out

    except Exception as e:
        logger.error('on_prem_gateway get_list: %s', format_exc())
        return error_response(str(e))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def create(req:'HttpRequest') -> 'HttpResponse':

    try:
        body = req.body.decode('utf-8')
        payload = loads(body)

        request_data = {
            'name': payload['name'],
            'is_active': payload['is_active'],
            'hosts': payload['hosts'],
        }

        response = _invoke(req, 'create', request_data)
        out = json_response(response, success=response['success'])

        return out

    except Exception as e:
        logger.error('on_prem_gateway create: %s', format_exc())
        return error_response(str(e))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def edit(req:'HttpRequest') -> 'HttpResponse':

    try:
        body = req.body.decode('utf-8')
        payload = loads(body)

        request_data = {
            'id': payload['id'],
            'name': payload['name'],
            'is_active': payload['is_active'],
            'hosts': payload['hosts'],
        }

        response = _invoke(req, 'edit', request_data)
        out = json_response(response, success=response['success'])

        return out

    except Exception as e:
        logger.error('on_prem_gateway edit: %s', format_exc())
        return error_response(str(e))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete(req:'HttpRequest', id:'str') -> 'HttpResponse':

    try:
        request_data = {'id': id}

        response = _invoke(req, 'delete', request_data)
        out = json_response(response, success=response['success'])

        return out

    except Exception as e:
        logger.error('on_prem_gateway delete: %s', format_exc())
        return error_response(str(e))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def enrollment_token(req:'HttpRequest', id:'str') -> 'HttpResponse':
    """ Mints an enrollment token for one gateway.
    """
    try:
        request_data = {
            'id': id,
            'dashboard_host': req.get_host(),
        }

        response = _invoke(req, 'get-enrollment-token', request_data)
        out = json_response(response, success=response['success'])

        return out

    except Exception as e:
        logger.error('on_prem_gateway enrollment_token: %s', format_exc())
        return error_response(str(e))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def reset_key(req:'HttpRequest', id:'str') -> 'HttpResponse':

    try:
        request_data = {'id': id}

        response = _invoke(req, 'reset-key', request_data)
        out = json_response(response, success=response['success'])

        return out

    except Exception as e:
        logger.error('on_prem_gateway reset_key: %s', format_exc())
        return error_response(str(e))

# ################################################################################################################################
# ################################################################################################################################
