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

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'object') -> 'TemplateResponse':

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))
    initial_topic_name = req.GET.get('topic_name', '')

    topics = [] # type: list

    try:
        response = req.zato.client.invoke('zato.pubsub.topic.get-list', {
            'cluster_id': cluster_id,
        })
        if response.ok:
            for item in response.data:
                topics.append({'id': item.id, 'name': item.name})
    except Exception as e:
        logger.error('EDA publish - error loading topics: %s', e)

    return TemplateResponse(req, 'zato/eda/publish.html', {
        'cluster_id': cluster_id,
        'topics': json.dumps(topics),
        'initial_topic_name': initial_topic_name,
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/publish.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def submit(req:'object') -> 'HttpResponse':

    topic_name = req.POST.get('topic_name', '')
    data = req.POST.get('data', '')
    priority = req.POST.get('priority', '5')
    expiration = req.POST.get('expiration', '86400')

    try:
        response = req.zato.client.invoke('zato.broker.topic.publish', {
            'topic_name': topic_name,
            'data': data,
            'priority': priority,
            'expiration': expiration,
        })
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                return HttpResponse(raw, content_type='application/json')
            return HttpResponse(json.dumps(raw), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error publishing message'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('EDA publish error: %s', e)
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

# ################################################################################################################################
# ################################################################################################################################
