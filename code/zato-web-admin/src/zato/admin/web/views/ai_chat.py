# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.http import HttpResponse

# Redis
import redis

# Zato
from zato.admin.web.views import method_allowed
from zato.common.ai.models import get_all_models
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

REDIS_KEY_PREFIX = 'zato.ai-chat.api-key.'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_keys(req):

    result = {
        'keys': {
            'anthropic': False,
            'openai': False
        }
    }

    try:
        anthropic_key = redis_client.get(REDIS_KEY_PREFIX + 'anthropic')
        openai_key = redis_client.get(REDIS_KEY_PREFIX + 'openai')

        result['keys']['anthropic'] = bool(anthropic_key)
        result['keys']['openai'] = bool(openai_key)

    except Exception as e:
        logger.warning('get_keys failed: %s', e)

    return HttpResponse(dumps(result), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save_key(req):

    result = {
        'success': False
    }

    try:
        data = loads(req.body)
        provider = data.get('provider')
        api_key = data.get('api_key')

        if provider not in ('anthropic', 'openai'):
            result['error'] = 'Invalid provider'
            return HttpResponse(dumps(result), content_type='application/json', status=400)

        if not api_key:
            result['error'] = 'API key is required'
            return HttpResponse(dumps(result), content_type='application/json', status=400)

        redis_client.set(REDIS_KEY_PREFIX + provider, api_key)
        result['success'] = True

    except Exception as e:
        logger.warning('save_key failed: %s', e)
        result['error'] = str(e)

    return HttpResponse(dumps(result), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_key(req):

    result = {
        'success': False
    }

    try:
        data = loads(req.body)
        provider = data.get('provider')

        if provider not in ('anthropic', 'openai'):
            result['error'] = 'Invalid provider'
            return HttpResponse(dumps(result), content_type='application/json', status=400)

        redis_client.delete(REDIS_KEY_PREFIX + provider)
        result['success'] = True

    except Exception as e:
        logger.warning('delete_key failed: %s', e)
        result['error'] = str(e)

    return HttpResponse(dumps(result), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_models(req):

    result = get_all_models()
    return HttpResponse(dumps(result), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
