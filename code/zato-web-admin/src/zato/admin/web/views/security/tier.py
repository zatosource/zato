# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _get_limits_summary(rules): # type: ignore
    """ Builds a short human-readable summary of a tier's limits, e.g. '10/sec, 500/month'.
    """
    parts = []

    for rule in rules:
        for slot in rule['time_range']:

            # Rate and burst describe token buckets, limit and limit_unit describe fixed windows -
            # each is genuinely optional in a slot.
            if rate := slot.get('rate'):
                parts.append(f'{rate}/sec')

            if limit := slot.get('limit'):
                limit_unit = slot['limit_unit']
                parts.append(f'{limit}/{limit_unit}')

    out = ', '.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_tier_list(req): # type: ignore
    """ Returns all quota tiers from the server.
    """
    response = req.zato.client.invoke('zato.security.tier.get-list')
    out = response.data
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req): # type: ignore

    tier_list = get_tier_list(req)

    for tier in tier_list:
        tier['limits_summary'] = _get_limits_summary(tier['rules'])

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'tier_list': tier_list,
    }

    return TemplateResponse(req, 'zato/security/tier.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def create(req): # type: ignore

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'tier_id': '',
        'tier_name': '',
        'tier_description': '',
        'rules_json': '[]',
    }

    return TemplateResponse(req, 'zato/security/tier-editor.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def edit(req, id): # type: ignore

    response = req.zato.client.invoke('zato.security.tier.get', {
        'id': id,
    })

    tier = response.data

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'tier_id': id,
        'tier_name': tier.name,
        'tier_description': tier.description,
        'rules_json': dumps(tier.rules),
    }

    return TemplateResponse(req, 'zato/security/tier-editor.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save(req): # type: ignore
    try:
        tier_id = req.POST['id']
        name = req.POST['name']
        description = req.POST['description']
        rules_json = req.POST['rules_json']

        request = {
            'name': name,
            'description': description,
            'rules_json': rules_json,
        }

        # An empty id on input means a new tier is being created
        if tier_id:
            request['id'] = tier_id
            service_name = 'zato.security.tier.edit'
        else:
            service_name = 'zato.security.tier.create'

        logger.info('tier.save; service:%s, request:%s', service_name, request)

        response = req.zato.client.invoke(service_name, request)

        if response.ok:
            return JsonResponse({'status': 'ok', 'id': response.data.id})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)

    except Exception:
        msg = 'Quota tier could not be saved, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete(req, id): # type: ignore
    try:
        response = req.zato.client.invoke('zato.security.tier.delete', {
            'id': id,
        })

        if response.ok:
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'message': response.details}, status=HTTPStatus.BAD_REQUEST)

    except Exception:
        msg = 'Quota tier could not be deleted, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
# ################################################################################################################################
