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
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'any_', success:'bool') -> 'HttpResponse':
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    out = response_class(response_json, content_type='application/json')
    return out

# ################################################################################################################################

def _invoke(req:'any_', service_name:'str') -> 'HttpResponse':
    """ Forwards the JSON body of a request to a Redis configuration service and returns its response as JSON.
    """
    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        response = req.zato.client.invoke(service_name, config_data)

        if response.ok:
            data = response.data
            out = _json_response(data, success=data['success'])
        else:
            error = str(response)
            payload = {'success': False, 'error': error}
            out = _json_response(payload, success=False)

    except Exception as e:
        details = format_exc()
        logger.error('Redis configuration service `%s` failed: %s', service_name, details)

        error = str(e)
        payload = {'success': False, 'error': error}
        out = _json_response(payload, success=False)

    return out

# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    # The current values of the default Redis connection
    redis_values = {}

    try:
        response = req.zato.client.invoke('zato.config-db.redis.get', {})
        if response.ok:
            redis_values = response.data['values']
        else:
            logger.error('redis index: invoke failed: %s', response)
    except Exception:
        logger.error('redis index: %s', format_exc())

    return TemplateResponse(req, 'zato/redis.html', {
        'config': redis_values,
        'config_json': dumps(redis_values),
    })

# ################################################################################################################################

@method_allowed('POST')
def test(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.redis.test')
    return out

# ################################################################################################################################

@method_allowed('POST')
def save(req:'any_') -> 'HttpResponse':
    out = _invoke(req, 'zato.config-db.redis.save')
    return out

# ################################################################################################################################
# ################################################################################################################################
