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

def _json_response(data:'any_', success:'bool'=True) -> 'HttpResponse':
    response_json = dumps(data)
    response_class = HttpResponse if success else HttpResponseServerError
    return response_class(response_json, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    # Which demo config sets are present and which of their objects exist
    demo_config_sets = {}

    try:
        response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'get_demo_config'})
        if response.ok:
            demo_config_sets = response.data['sets']
        else:
            logger.error('demo_config index: invoke failed: %s', response)
    except Exception:
        logger.error('demo_config index: %s', format_exc())

    # The sliders render in their correct positions from the very first paint,
    # so nothing visibly slides once the page shows up
    demo_config_all_on = bool(demo_config_sets)

    for set_info in demo_config_sets.values():
        if not set_info['is_present']:
            demo_config_all_on = False

    return TemplateResponse(req, 'zato/demo-config/index.html', {
        'demo_config_sets': demo_config_sets,
        'demo_config_all_on': demo_config_all_on,
    })

# ################################################################################################################################

@method_allowed('POST')
def save(req:'any_') -> 'HttpResponse':

    try:
        body = req.body.decode('utf-8')
        config_data = loads(body)

        response = req.zato.client.invoke('zato.server.invoker', {
            'func_name': 'save_demo_config',
            'states': config_data['states'],
        })

        if response.ok:
            data = response.data
            return _json_response(data, success=data['success'])
        else:
            return _json_response({'success': False, 'error': str(response)}, success=False)

    except Exception as e:
        logger.error('demo_config save: %s', format_exc())
        return _json_response({'success': False, 'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################
