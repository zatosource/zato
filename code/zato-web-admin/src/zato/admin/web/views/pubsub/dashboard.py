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
    "delivery_rate_per_min": float,
    "prev_delivery_rate_per_min": float | None,
    "topics": [
        {
            "name": str,
            "is_active": bool,
            "depth": int,
            "subscriber_count": int,
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
        "publishes": [{"ts": int (epoch ms), "count": int}],
        "deliveries": [{"ts": int (epoch ms), "count": int}],
        "depth": [{"ts": int (epoch ms), "value": int}]
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

_Dashboard_Base_Url = '/zato/pubsub/dashboard/'

# Metrics not yet available from the backend - depth, rates, and age
# will be populated once the corresponding services are implemented.
_No_Depth         = 0
_No_Rate          = 0
_No_Age           = 0

# ################################################################################################################################
# ################################################################################################################################

def _get_dashboard_data(req:'any_') -> 'str':

    # Get the list of topics ..
    try:
        response = req.zato.client.invoke('zato.pubsub.topic.get-list', {
            'cluster_id': default_cluster_id,
        })
        if response.ok:
            topics = response.data
        else:
            topics = []
    except Exception as error:
        logger.warning('Pub/sub dashboard - could not get topics: %s', error)
        topics = []

    # .. get the list of subscriptions ..
    try:
        sub_response = req.zato.client.invoke('zato.pubsub.subscription.get-list', {
            'cluster_id': default_cluster_id,
        })
        if sub_response.ok:
            subscriptions = sub_response.data
        else:
            subscriptions = []
    except Exception as error:
        logger.warning('Pub/sub dashboard - could not get subscriptions: %s', error)
        subscriptions = []

    # .. build the topic list ..
    topic_count = len(topics)
    total_subscribers = len(subscriptions)

    topic_list = []

    for item in topics:
        topic_list.append({
            'name': item['name'],
            'is_active': item['is_active'],
            'depth': _No_Depth,
            'subscriber_count': item['subscriber_count'],
            'pub_rate': _No_Rate,
        })

    # .. build the queue list ..
    queue_list = []

    for subscription in subscriptions:
        queue_list.append({
            'name': subscription['sub_key'],
            'depth': _No_Depth,
            'oldest_msg_age_seconds': _No_Age,
            'delivery_rate': _No_Rate,
        })

    # .. find the oldest unacked message age across all queues ..
    oldest_unacked_age_seconds = _No_Age

    for queue in queue_list:
        queue_age = queue['oldest_msg_age_seconds']
        if queue_age > oldest_unacked_age_seconds:
            oldest_unacked_age_seconds = queue_age

    # .. get the publish timeline from Redis streams ..
    try:
        timeline_response = req.zato.client.invoke('zato.pubsub.topic.get-publish-timeline', {
            'since_minutes': 60,
        })
        if timeline_response.ok:
            publishes_timeline = timeline_response.data
            if isinstance(publishes_timeline, str):
                publishes_timeline = json.loads(publishes_timeline)
        else:
            publishes_timeline = []
    except Exception as error:
        logger.warning('Pub/sub dashboard - could not get timeline: %s', error)
        publishes_timeline = []

    # .. and return the combined data.
    data = {
        'topic_count': topic_count,
        'total_subscribers': total_subscribers,
        'total_depth': _No_Depth,
        'oldest_unacked_age_seconds': oldest_unacked_age_seconds,
        'delivery_rate_per_min': _No_Rate,
        'prev_delivery_rate_per_min': None,
        'topics': topic_list,
        'queues': queue_list,
        'history_timeline': {
            'publishes': publishes_timeline,
            'deliveries': [],
            'depth': [],
        },
    }

    out = json.dumps(data)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':

    data_json = _get_dashboard_data(req)

    return TemplateResponse(req, 'zato/pubsub/dashboard.html', {
        'cluster_id': default_cluster_id,
        'dashboard_data': data_json,
        'dashboard_base_url': _Dashboard_Base_Url,
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
    except Exception as error:
        logger.error('Pub/sub dashboard poll error: %s', error)
        error_json = json.dumps({'error': str(error)})
        return HttpResponse(
            error_json.encode('utf-8'),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def import_demo_config(req:'any_') -> 'HttpResponse':

    try:
        response = req.zato.client.invoke('zato.server.invoker', {
            'func_name': 'import_demo_pubsub',
        })

        content = str(response.data)

        out = HttpResponse()
        out.content = content

        return out

    except Exception as error:
        logger.error('Pub/sub import demo config error: %s', error)
        error_message = str(error)
        return HttpResponse(
            error_message.encode('utf-8'),
            content_type='text/plain',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################
