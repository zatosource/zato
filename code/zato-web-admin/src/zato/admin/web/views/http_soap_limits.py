# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from traceback import format_exc

# Django
from django.http import HttpResponseServerError, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.security.tier import get_tier_list
from zato.common.json_internal import dumps
from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def rate_limiting(req, id): # type: ignore
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })

    rules_response = req.zato.client.invoke('zato.http-soap.rate-limiting.get', {
        'id': id,
    })

    # Tiers are offered in a select so a channel can reference one instead of carrying its own rules
    tier_list = get_tier_list(req)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'channel_id': id,
        'channel_name': response.data.name,
        'channel_url_path': response.data.url_path,
        'transport': response.data.transport,
        'rules_json': dumps(rules_response.data.rate_limiting),
        'quota_tier': rules_response.data.quota_tier,
        'tier_list': tier_list,
        'zato_template_name': 'zato/http_soap/rate-limiting.html',
    }

    return TemplateResponse(req, 'zato/http_soap/rate-limiting.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rate_limiting_save(req, id): # type: ignore
    try:
        rules_json = req.POST['rules_json']
        quota_tier = req.POST['quota_tier']
        logger.info('rate_limiting_save; channel_id:%s, rules_json:%s, quota_tier:%s', id, rules_json, quota_tier)
        response = req.zato.client.invoke('zato.http-soap.rate-limiting.save', {
            'id': id,
            'rules_json': rules_json,
            'quota_tier': quota_tier,
        })
        logger.info('rate_limiting_save; channel_id:%s, response.ok:%s', id, response.ok)
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        msg = 'Rate limiting rules could not be saved, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

def rate_limiting_clear_counters(req, id): # type: ignore
    try:
        rule_index = req.POST['rule_index']
        response = req.zato.client.invoke('zato.http-soap.rate-limiting.clear-counters', {
            'id': id,
            'rule_index': rule_index,
        })
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        msg = 'Rate limiting counters could not be cleared, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def response_caching(req:'any_', id:'str') -> 'TemplateResponse':
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': id,
    })

    config_response = req.zato.client.invoke('zato.http-soap.response-cache.get', {
        'id': id,
    })

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'channel_id': id,
        'channel_name': response.data.name,
        'channel_url_path': response.data.url_path,
        'transport': response.data.transport,
        'config': config_response.data.response_cache,
        'config_json': dumps(config_response.data.response_cache),
        'zato_template_name': 'zato/http_soap/response-caching.html',
    }

    return TemplateResponse(req, 'zato/http_soap/response-caching.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def response_caching_save(req:'any_', id:'str') -> 'any_':
    try:
        config_json = req.POST['config_json']
        logger.info('response_caching_save; channel_id:%s, config_json:%s', id, config_json)
        response = req.zato.client.invoke('zato.http-soap.response-cache.save', {
            'id': id,
            'config_json': config_json,
        })
        logger.info('response_caching_save; channel_id:%s, response.ok:%s', id, response.ok)
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        exception_details = format_exc()
        msg = f'Response caching config could not be saved, e:`{exception_details}`'
        logger.error(msg)
        return HttpResponseServerError(msg.encode('utf-8'))

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def response_caching_clear(req:'any_', id:'str') -> 'any_':
    try:
        response = req.zato.client.invoke('zato.http-soap.response-cache.clear', {
            'id': id,
        })
        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)
    except Exception:
        exception_details = format_exc()
        msg = f'Response cache could not be cleared, e:`{exception_details}`'
        logger.error(msg)

# ################################################################################################################################
# ################################################################################################################################
