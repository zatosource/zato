# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Poll JSON contract returned by _get_dashboard_data:
{
    "topic_count": int,
    "total_subscribers": int,
    "total_depth": int,
    "oldest_unacked_age_seconds": int,
    "topics": [
        {
            "name": str,
            "is_active": bool,
            "depth": int,
            "subscriber_count": int,
            "total_published": int,
            "last_pub_ts": int (epoch ms, 0 if never),
            "pub_rate": float (messages/s)
        }
    ],
    "queues": [
        {
            "name": str,
            "depth": int,
            "oldest_msg_age_seconds": int,
            "delivery_rate": float (messages/s)
        }
    ],
    "history_timeline": {
        "publishes": [{ts: int (epoch ms), count: int}],
        "deliveries": [{ts: int (epoch ms), count: int}],
        "depth": [{ts: int (epoch ms), value: int}]
    }
}
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

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

dashboard_base_url = '/zato/pubsub/dashboard/'

# ################################################################################################################################
# ################################################################################################################################

def _get_dashboard_data(req:'any_') -> 'str':

    try:
        response = req.zato.client.invoke('zato.pubsub.topic.get-list', {
            'cluster_id': default_cluster_id,
        })
        if response.ok:
            topics = response.data if isinstance(response.data, list) else []
        else:
            topics = []
    except Exception as e:
        logger.warning('Pub/sub dashboard - could not get topics: %s', e)
        topics = []

    try:
        sub_response = req.zato.client.invoke('zato.pubsub.subscription.get-list', {
            'cluster_id': default_cluster_id,
        })
        if sub_response.ok:
            subscriptions = sub_response.data if isinstance(sub_response.data, list) else []
        else:
            subscriptions = []
    except Exception as e:
        logger.warning('Pub/sub dashboard - could not get subscriptions: %s', e)
        subscriptions = []

    topic_count = len(topics)
    total_subscribers = len(subscriptions)

    topic_list = []
    for item in topics:
        subscriber_count = item.get('subscriber_count', 0) or 0
        topic_list.append({
            'name': item['name'],
            'is_active': item.get('is_active', True),
            'depth': 0,
            'subscriber_count': subscriber_count,
            'pub_rate': 0,
        })

    queue_list = []
    for sub in subscriptions:
        queue_list.append({
            'name': sub.get('sub_key', ''),
            'depth': 0,
            'oldest_msg_age_seconds': 0,
            'delivery_rate': 0,
        })

    data = {
        'topic_count': topic_count,
        'total_subscribers': total_subscribers,
        'total_depth': 0,
        'topics': topic_list,
        'queues': queue_list,
        'oldest_unacked_age_seconds': 0,
        'history_timeline': {
            'publishes': [],
            'deliveries': [],
            'depth': [],
        },
    }

    return json.dumps(data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    data_json = _get_dashboard_data(req)

    return TemplateResponse(req, 'zato/pubsub/dashboard.html', {
        'cluster_id': default_cluster_id,
        'dashboard_data': data_json,
        'dashboard_base_url': dashboard_base_url,
        'zato_clusters': True,
        'zato_template_name': 'zato/pubsub/dashboard.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req:'any_') -> 'HttpResponse':

    try:
        data_json = _get_dashboard_data(req)
        return HttpResponse(data_json.encode('utf-8'), content_type='application/json')
    except Exception as e:
        logger.error('Pub/sub dashboard poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}).encode('utf-8'),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def import_demo_config(req:'any_') -> 'HttpResponse':

    response = req.zato.client.invoke('zato.server.invoker', {
        'func_name': 'import_demo_pubsub',
    })

    out = HttpResponse()
    out.content = str(response.data)

    return out

# ################################################################################################################################
# ################################################################################################################################
