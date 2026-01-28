# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.utils import json_response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

page_config = {
    'title': 'Rule engine',
    'section_title': 'Rules',
    'containers_title': 'Containers',
    'execute_title': 'Execute rule',
    'execute_button_label': 'Execute',
    'reload_button_label': 'Reload rules',
    'show_sidebar': True,
}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'HttpRequest'):
    context = {
        'page_config': page_config,
        'containers': [],
        'rules': [],
    }

    try:
        response = req.zato.client.invoke('zato.rules.get-rule-list', {})
        if response.ok:
            context['containers'] = response.data.get('containers', [])
            context['rules'] = response.data.get('rules', [])
    except Exception as e:
        logger.warning('Could not load rules: %s', e)

    return TemplateResponse(req, 'zato/rules/index.html', context)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rule_list(req:'HttpRequest'):
    try:
        response = req.zato.client.invoke('zato.rules.get-rule-list', {})
        if response.ok:
            return json_response({
                'containers': response.data.get('containers', []),
                'rules': response.data.get('rules', [])
            })
        else:
            return json_response({'error': 'Failed to get rules'}, success=False)
    except Exception as e:
        logger.warning('get_rule_list error: %s', e)
        return json_response({'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rule(req:'HttpRequest', rule_name:'str'):
    try:
        response = req.zato.client.invoke('zato.rules.get-rule', {'name': rule_name})
        if response.ok:
            return json_response(response.data)
        else:
            return json_response({'error': 'Rule not found'}, success=False)
    except Exception as e:
        logger.warning('get_rule error: %s', e)
        return json_response({'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def execute_rule(req:'HttpRequest'):
    try:
        body = json.loads(req.body)
        rule_name = body.get('rule_name', '')
        data = body.get('data', {})

        response = req.zato.client.invoke('zato.rules.execute-rule', {
            'name': rule_name,
            'data': data
        })

        if response.ok:
            return json_response(response.data)
        else:
            return json_response({'error': 'Execution failed'}, success=False)
    except Exception as e:
        logger.warning('execute_rule error: %s', e)
        return json_response({'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def reload_rules(req:'HttpRequest'):
    try:
        response = req.zato.client.invoke('zato.rules.reload-rules', {})
        if response.ok:
            return json_response({'message': 'Rules reloaded'})
        else:
            return json_response({'error': 'Reload failed'}, success=False)
    except Exception as e:
        logger.warning('reload_rules error: %s', e)
        return json_response({'error': str(e)}, success=False)

# ################################################################################################################################
# ################################################################################################################################
