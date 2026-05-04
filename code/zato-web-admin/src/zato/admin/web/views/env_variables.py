# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

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
from zato.admin.web.views.settings.config import env_variables_page_config
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def json_response(data, success=True):
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    try:
        response = req.zato.client.invoke('zato.env-variables.get-list', {})
        if response.ok:
            items = response.data.get('items', []) if isinstance(response.data, dict) else []
            env_text = '\n'.join('{}={}'.format(item['key'], item['value']) for item in items)
        else:
            env_text = ''
            logger.error('env_variables index: invoke failed: %s', response)
    except Exception:
        env_text = ''
        logger.error('env_variables index: %s', format_exc())

    return TemplateResponse(req, 'zato/settings/env-variables/index.html', {
        'page_config': env_variables_page_config,
        'textarea_content': env_text,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def test(req):

    try:
        body = req.body.decode('utf-8')
        from zato.common.json_internal import loads
        config_data = loads(body)

        response = req.zato.client.invoke('zato.env-variables.test', config_data)

        if response.ok:
            data = response.data if isinstance(response.data, dict) else {}
            return json_response(data, success=data.get('success', False))
        else:
            return json_response({'success': False, 'error': str(response)}, success=False)

    except Exception as e:
        logger.error('test exception: %s', format_exc())
        return json_response({'success': False, 'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save(req):

    try:
        body = req.body.decode('utf-8')
        from zato.common.json_internal import loads
        config_data = loads(body)

        response = req.zato.client.invoke('zato.env-variables.save', config_data)

        if response.ok:
            data = response.data if isinstance(response.data, dict) else {}
            return json_response(data, success=data.get('success', False))
        else:
            return json_response({'success': False, 'error': str(response)}, success=False)

    except Exception as e:
        logger.error('save exception: %s', format_exc())
        return json_response({'success': False, 'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################
