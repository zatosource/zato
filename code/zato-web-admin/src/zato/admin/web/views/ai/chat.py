# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST
from logging import getLogger

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.common import delete_api_key, get_all_api_key_status, is_valid_provider, set_api_key
from zato.common.ai.models import get_all_models
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_keys(req) -> 'HttpResponse':
    """ Returns API key status for all providers.
    """
    out = {
        'keys': get_all_api_key_status()
    }

    response = dumps(out)
    return HttpResponse(response, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_key(req) -> 'HttpResponse':
    """ Saves an API key for a provider.
    """
    out = {
        'success': False
    }

    try:
        data = loads(req.body)
        provider = data.get('provider')
        api_key = data.get('api_key')

        if not is_valid_provider(provider):
            out['error'] = 'Invalid provider'
            response = dumps(out)
            return HttpResponse(response, content_type='application/json', status=BAD_REQUEST)

        if not api_key:
            out['error'] = 'API key is required'
            response = dumps(out)
            return HttpResponse(response, content_type='application/json', status=BAD_REQUEST)

        set_api_key(provider, api_key)
        out['success'] = True

    except Exception as e:
        logger.warning('save_key failed: %s', e)
        out['error'] = str(e)

    response = dumps(out)
    return HttpResponse(response, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_key(req) -> 'HttpResponse':
    """ Deletes an API key for a provider.
    """
    out = {
        'success': False
    }

    try:
        data = loads(req.body)
        provider = data.get('provider')

        if not is_valid_provider(provider):
            out['error'] = 'Invalid provider'
            response = dumps(out)
            return HttpResponse(response, content_type='application/json', status=BAD_REQUEST)

        delete_api_key(provider)
        out['success'] = True

    except Exception as e:
        logger.warning('delete_key failed: %s', e)
        out['error'] = str(e)

    response = dumps(out)
    return HttpResponse(response, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_models(req) -> 'HttpResponse':
    """ Returns all available models grouped by provider.
    """
    out = get_all_models()
    response = dumps(out)
    return HttpResponse(response, content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
