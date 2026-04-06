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
def index(req, topic_name):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))

    try:
        response = req.zato.client.invoke('zato.broker.topic.get-detail', {
            'topic_name': topic_name,
        })
        data = response.data if response.ok else {}
    except Exception as e:
        logger.error('EDA topic detail error: %s', e)
        data = {}

    return TemplateResponse(req, 'zato/eda/topic-detail.html', {
        'cluster_id': cluster_id,
        'topic_name': topic_name,
        'topic_data': json.dumps(data) if data else '{}',
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/topic-detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req):

    topic_name = req.POST.get('topic_name', '')

    try:
        response = req.zato.client.invoke('zato.broker.topic.get-detail', {
            'topic_name': topic_name,
        })
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('EDA topic poll error: %s', e)
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def purge(req):

    topic_name = req.POST.get('topic_name', '')

    try:
        response = req.zato.client.invoke('zato.broker.topic.purge', {
            'topic_name': topic_name,
        })
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('EDA topic purge error: %s', e)
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

# ################################################################################################################################
# ################################################################################################################################
