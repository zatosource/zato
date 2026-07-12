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
from zato.admin.web.views.settings.config import logging_page_config
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

@method_allowed('GET')
def index(req:'HttpRequest') -> 'TemplateResponse':

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
            logging_text = '\n'.join(lines)

        else:
            logging_text = ''
            logger.error('logging index: invoke failed: %s', response)
    except Exception:
        logging_text = ''
        logger.error('logging index: %s', format_exc())

    out = TemplateResponse(req, 'zato/settings/logging/index.html', {
        'page_config': logging_page_config,
        'textarea_content': logging_text,
    })
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def test(req:'HttpRequest') -> 'HttpResponse':

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        text = config_data['text']

        response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'test_logging', 'text': text})

        if response.ok:
            data = response.data
            out = json_response(data, success=data['success'])
        else:
            out = json_response({'success': False, 'error': str(response)}, success=False)

        return out

    except Exception as e:
        logger.error('test exception: %s', format_exc())
        out = json_response({'success': False, 'error': str(e)}, success=False)
        return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save(req:'HttpRequest') -> 'HttpResponse':

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)
        text = config_data['text']

        response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'set_logging', 'text': text})

        if response.ok:
            data = response.data
            out = json_response(data, success=data['success'])
        else:
            out = json_response({'success': False, 'error': str(response)}, success=False)

        return out

    except Exception as e:
        logger.error('save exception: %s', format_exc())
        out = json_response({'success': False, 'error': str(e)}, success=False)
        return out

# ################################################################################################################################
# ################################################################################################################################
