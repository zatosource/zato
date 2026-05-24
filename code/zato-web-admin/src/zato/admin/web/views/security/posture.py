# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'object') -> 'TemplateResponse':

    scan_data = {
        'check_states': {},
    }

    try:
        response = req.zato.client.invoke('zato.security.posture.get-check-states', {})
        if response.ok:
            scan_data['check_states'] = response.data
    except Exception as e:
        logger.warning('Security posture dashboard error: %s', e)

    return TemplateResponse(req, 'zato/security/posture.html', {
        'cluster_id': default_cluster_id,
        'scan_data': json.dumps(scan_data),
        'zato_clusters': True,
        'zato_template_name': 'zato/security/posture.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def run_scan(req:'object') -> 'HttpResponse':

    try:
        body = json.loads(req.body)
        response = req.zato.client.invoke('zato.security.posture.run-scan', body)
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Security posture scan error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save(req:'object') -> 'HttpResponse':

    try:
        body = json.loads(req.body)
        response = req.zato.client.invoke('zato.security.posture.save-check-states', body)
        if response.ok:
            return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Security posture save error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req:'object') -> 'HttpResponse':

    try:
        response = req.zato.client.invoke('zato.security.posture.get-results', {})
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Security posture poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################
