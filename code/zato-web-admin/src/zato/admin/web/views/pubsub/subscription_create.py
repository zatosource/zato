# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from json import dumps
from operator import itemgetter
from traceback import format_exc

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.util import get_pubsub_security_definitions, get_service_list
from zato.admin.web.views import get_outconn_rest_list, method_allowed
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anyset, strlist
    any_ = any_
    anydict = anydict
    anyset = anyset
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Pattern_Prefix_Pub = 'pub='
_Pattern_Prefix_Sub = 'sub='

_Subscriber_Access_Types = PubSub.API_Client.Subscriber, PubSub.API_Client.Publisher_Subscriber

_get_name = itemgetter('name')

# ################################################################################################################################
# ################################################################################################################################

def _get_subscribe_patterns_by_sec_base_id(request:'any_') -> 'anydict':
    """ Returns the subscription patterns of each security definition, keyed by the definition's ID.
    """

    # Our response to produce
    out = {}

    # Get all the permissions ..
    response = request.zato.client.invoke('zato.pubsub.permission.get-list', {})

    # .. and collect the patterns of each permission that allows subscriptions, without the publication-only ones.
    for permission in response.data:

        if permission.access_type not in _Subscriber_Access_Types:
            continue

        if permission.sec_base_id not in out:
            out[permission.sec_base_id] = []

        patterns = out[permission.sec_base_id]

        for line in permission.pattern.splitlines():

            pattern = line.strip()

            if not pattern:
                continue

            if pattern.startswith(_Pattern_Prefix_Pub):
                continue

            pattern = pattern.removeprefix(_Pattern_Prefix_Sub)
            patterns.append(pattern)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_topic_names_for_pattern(request:'any_', pattern:'str') -> 'strlist':
    """ Returns the names of all the topics a subscription pattern matches.
    """

    # Our response to produce
    out = []

    response = request.zato.client.invoke('zato.pubsub.topic.get-matches', {
        'pattern': pattern
    })

    for item in response.data:
        out.append(item.name)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_subscribed_service_names(request:'any_') -> 'anyset':
    """ Returns the names of the services that are subscribers on their own, without a security definition.
    """

    # Our response to produce
    out = set()

    response = request.zato.client.invoke('zato.pubsub.subscription.get-list', {})

    for item in response.data:
        if item.sec_base_id is None:
            out.add(item.push_service_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_create_form_data(request:'any_') -> 'HttpResponse':
    """ Returns the topics, the services, the API clients with the topics each of them may subscribe to,
    and the REST endpoints that the form creating a subscription offers.
    """

    try:

        # Get all the topics ..
        topics_response = request.zato.client.invoke('zato.pubsub.topic.get-list', {})
        topics = []

        for item in topics_response.data:
            topics.append(item.name)

        topics.sort()

        # .. the services without a subscription ..
        subscribed_services = _get_subscribed_service_names(request)
        service_list = get_service_list(request)
        services = []

        for item in service_list:
            service_name = item['service_name']
            if service_name not in subscribed_services:
                services.append(service_name)

        services.sort()

        # .. the API clients without a subscription, each with the topics its permissions cover ..
        sec_def_list = get_pubsub_security_definitions(request, 'create', 'subscription')
        patterns_by_sec_base_id = _get_subscribe_patterns_by_sec_base_id(request)
        topic_names_by_pattern = {}
        clients = []

        for item in sec_def_list:

            client_topics = set()

            if patterns := patterns_by_sec_base_id.get(item['id']):
                for pattern in patterns:

                    if pattern not in topic_names_by_pattern:
                        topic_names_by_pattern[pattern] = _get_topic_names_for_pattern(request, pattern)

                    pattern_topics = topic_names_by_pattern[pattern]
                    client_topics.update(pattern_topics)

            topic_names = sorted(client_topics)

            clients.append({
                'id': item['id'],
                'name': item['name'],
                'topics': topic_names,
            })

        clients.sort(key=_get_name)

        # .. and the REST endpoints.
        rest_endpoints = get_outconn_rest_list(request)
        endpoints = []

        for endpoint_id, endpoint_name in rest_endpoints.items():
            endpoints.append({
                'id': endpoint_id,
                'name': endpoint_name,
            })

        endpoints.sort(key=_get_name)

        response_json = dumps({
            'topics': topics,
            'services': services,
            'clients': clients,
            'endpoints': endpoints,
        })
        response_bytes = response_json.encode('utf-8')

        out = HttpResponse(response_bytes, content_type='application/json')

    except Exception as error:
        logger.error('VIEW get_create_form_data: error=%s', format_exc())

        error_json = dumps({
            'error': str(error)
        })
        error_bytes = error_json.encode('utf-8')

        out = HttpResponse(error_bytes, content_type='application/json', status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return out

# ################################################################################################################################
# ################################################################################################################################
