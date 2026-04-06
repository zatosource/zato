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

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

def _raw_json(response):
    if response.ok:
        raw = response.data
        return raw if isinstance(raw, str) else json.dumps(raw)
    return '{}'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req, stream_name, group_name):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))

    try:
        response = req.zato.client.invoke('zato.broker.queue.get-detail', {
            'stream_name': stream_name,
            'group_name': group_name,
        })
        data_json = _raw_json(response)
    except Exception as e:
        logger.error('EDA queue detail error: %s', e)
        data_json = '{}'

    return TemplateResponse(req, 'zato/eda/queue-detail.html', {
        'cluster_id': cluster_id,
        'stream_name': stream_name,
        'group_name': group_name,
        'queue_data': data_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/queue-detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req):

    stream_name = req.POST.get('stream_name', '')
    group_name = req.POST.get('group_name', '')

    try:
        response = req.zato.client.invoke('zato.broker.queue.get-detail', {
            'stream_name': stream_name,
            'group_name': group_name,
        })
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                return HttpResponse(raw, content_type='application/json')
            return HttpResponse(json.dumps(raw), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('EDA queue poll error: %s', e)
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def purge(req):

    stream_name = req.POST.get('stream_name', '')
    group_name = req.POST.get('group_name', '')

    try:
        response = req.zato.client.invoke('zato.broker.queue.purge', {
            'stream_name': stream_name,
            'group_name': group_name,
        })
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                return HttpResponse(raw, content_type='application/json')
            return HttpResponse(json.dumps(raw), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('EDA queue purge error: %s', e)
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

# ################################################################################################################################
# ################################################################################################################################
