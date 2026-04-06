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

def _parse_response(response):
    if response.ok:
        raw = response.data
        if isinstance(raw, str):
            return json.loads(raw)
        elif isinstance(raw, dict):
            return raw
    return {'messages': [], 'total': 0}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))
    topic_name = req.GET.get('topic_name', '')
    page = int(req.GET.get('page', 1))
    page_size = 50
    offset = (page - 1) * page_size

    try:
        invoke_input = {
            'offset': offset,
            'limit': page_size,
        }
        if topic_name:
            invoke_input['topic_name'] = topic_name

        response = req.zato.client.invoke('zato.broker.message.get-list', invoke_input)
        data = _parse_response(response)
    except Exception as e:
        logger.error('EDA messages error: %s', e)
        data = {'messages': [], 'total': 0}

    messages = data.get('messages', [])
    total = data.get('total', 0)
    total_pages = max(1, (total + page_size - 1) // page_size)

    return TemplateResponse(req, 'zato/eda/messages.html', {
        'cluster_id': cluster_id,
        'messages': json.dumps(messages),
        'total': total,
        'page': page,
        'total_pages': total_pages,
        'topic_name_filter': topic_name,
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/messages.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def detail(req, topic_name, msg_id):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))

    try:
        response = req.zato.client.invoke('zato.broker.message.get-detail', {
            'topic_name': topic_name,
            'msg_id': msg_id,
        })
        if response.ok:
            raw = response.data
            data_json = raw if isinstance(raw, str) else json.dumps(raw)
        else:
            data_json = '{}'
    except Exception as e:
        logger.error('EDA message detail error: %s', e)
        data_json = '{}'

    return TemplateResponse(req, 'zato/eda/message-detail.html', {
        'cluster_id': cluster_id,
        'topic_name': topic_name,
        'msg_id': msg_id,
        'message_data': data_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/message-detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################
