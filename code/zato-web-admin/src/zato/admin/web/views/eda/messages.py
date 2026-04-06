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
def index(req):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))
    stream_name = req.GET.get('stream_name', '')
    page = int(req.GET.get('page', 1))
    page_size = 50
    offset = (page - 1) * page_size

    try:
        invoke_input = {
            'offset': offset,
            'limit': page_size,
        }
        if stream_name:
            invoke_input['stream_name'] = stream_name

        response = req.zato.client.invoke('zato.broker.message.get-list', invoke_input)
        data = response.data if response.ok else {'messages': [], 'total': 0}
    except Exception as e:
        logger.error('EDA messages error: %s', e)
        data = {'messages': [], 'total': 0}

    messages = data.get('messages', []) if isinstance(data, dict) else []
    total = data.get('total', 0) if isinstance(data, dict) else 0
    total_pages = max(1, (total + page_size - 1) // page_size)

    return TemplateResponse(req, 'zato/eda/messages.html', {
        'cluster_id': cluster_id,
        'messages': json.dumps(messages),
        'total': total,
        'page': page,
        'total_pages': total_pages,
        'stream_name_filter': stream_name,
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/messages.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def detail(req, stream_name, msg_id):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))

    try:
        response = req.zato.client.invoke('zato.broker.message.get-detail', {
            'stream_name': stream_name,
            'msg_id': msg_id,
        })
        data = response.data if response.ok else {}
    except Exception as e:
        logger.error('EDA message detail error: %s', e)
        data = {}

    return TemplateResponse(req, 'zato/eda/message-detail.html', {
        'cluster_id': cluster_id,
        'stream_name': stream_name,
        'msg_id': msg_id,
        'message_data': json.dumps(data) if data else '{}',
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/message-detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################
