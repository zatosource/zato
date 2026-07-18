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
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, strlist
    HttpRequest = HttpRequest
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def json_response(data:'any_', success:'bool'=True) -> 'HttpResponse':
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError

    out = response_class(response_json, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_logging_text(req:'HttpRequest') -> 'str':
    """ Returns the current logger levels, one logger per line.
    """
    try:
        response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'get_logging'})
        if response.ok:

            # Turn the list of loggers into one logger per line ..
            lines:'strlist' = []

            for item in response.data['items']:
                name = item['name']
                level = item['level']
                lines.append(f'{name}={level}')

            # .. and this is what the textarea will show.
            out = '\n'.join(lines)

        else:
            out = ''
            logger.error('logging index: invoke failed: %s', response)
    except Exception:
        out = ''
        logger.error('logging index: %s', format_exc())

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_destinations(req:'HttpRequest') -> 'any_':
    """ Returns all the configured log destinations, grouped by vendor.
    """
    try:
        response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'get_log_destinations'})
        if response.ok:
            out = response.data['destinations']
        else:
            out = {}
            logger.error('logging destinations: invoke failed: %s', response)
    except Exception:
        out = {}
        logger.error('logging destinations: %s', format_exc())

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'HttpRequest') -> 'TemplateResponse':

    active_tab = req.GET['tab']

    page_data = {
        'logging_text': _get_logging_text(req),
        'destinations': _get_destinations(req),
    }

    out = TemplateResponse(req, 'zato/settings/logging/index.html', {
        'active_tab': active_tab,
        'page_data': dumps(page_data),
    })
    return out

# ################################################################################################################################
# ################################################################################################################################

def _invoke_with_text(req:'HttpRequest', func_name:'str') -> 'HttpResponse':
    """ Passes the text from the request to a server function and relays the result.
    """
    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        text = config_data['text']

        response = req.zato.client.invoke('zato.server.invoker', {'func_name': func_name, 'text': text})

        if response.ok:
            data = response.data
            out = json_response(data, success=data['success'])
        else:
            out = json_response({'success': False, 'error': str(response)}, success=False)

        return out

    except Exception as e:
        logger.error('%s exception: %s', func_name, format_exc())
        out = json_response({'success': False, 'error': str(e)}, success=False)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def test(req:'HttpRequest') -> 'HttpResponse':
    out = _invoke_with_text(req, 'test_logging')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save(req:'HttpRequest') -> 'HttpResponse':
    out = _invoke_with_text(req, 'set_logging')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def destination_save(req:'HttpRequest') -> 'HttpResponse':

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        response = req.zato.client.invoke('zato.server.invoker', {
            'func_name': 'set_log_destination',
            'vendor': config_data['vendor'],
            'destination': config_data['destination'],
        })

        if response.ok:
            out = json_response(response.data)
        else:
            out = json_response({'error': str(response)}, success=False)

        return out

    except Exception as e:
        logger.error('destination_save exception: %s', format_exc())
        out = json_response({'error': str(e)}, success=False)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _invoke_with_destination_id(req:'HttpRequest', func_name:'str') -> 'HttpResponse':
    """ Passes a vendor and a destination id to a server function and relays the result.
    """
    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        response = req.zato.client.invoke('zato.server.invoker', {
            'func_name': func_name,
            'vendor': config_data['vendor'],
            'destination_id': config_data['destination_id'],
        })

        if response.ok:
            out = json_response(response.data)
        else:
            out = json_response({'error': str(response)}, success=False)

        return out

    except Exception as e:
        logger.error('%s exception: %s', func_name, format_exc())
        out = json_response({'error': str(e)}, success=False)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def destination_delete(req:'HttpRequest') -> 'HttpResponse':
    out = _invoke_with_destination_id(req, 'delete_log_destination')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def destination_ping(req:'HttpRequest') -> 'HttpResponse':
    out = _invoke_with_destination_id(req, 'ping_log_destination')
    return out

# ################################################################################################################################
# ################################################################################################################################
