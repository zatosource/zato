# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub import MsgForm
from zato.admin.web.views import django_url_reverse, slugify
from zato.common.api import PUBSUB
from zato.common.util.api import asbool

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

def get_client_html(item, security_id, cluster_id, style='', separator=''):
    """ Client is a string representation of a WebSockets channel, HTTP credentials or a service.
    """
    style = style or 'font-size:smaller'
    separator = separator or '<br/>'

    client = ''
    path_name = ''

    if item.is_internal:
        return 'Internal'

    elif item.endpoint_type == PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id:
        path_name = 'channel-web-socket'
        name = item.ws_channel_name
        protocol = 'WebSockets'

    elif item.endpoint_type == PUBSUB.ENDPOINT_TYPE.REST.id:
        path_name = 'security-basic-auth'
        name = item.sec_name
        protocol = 'REST'

    elif item.endpoint_type == PUBSUB.ENDPOINT_TYPE.SERVICE.id:
        path_name = 'service'
        name = item.service_name
        protocol = 'Service'

    if path_name:
        path = django_url_reverse(path_name)
        client = '<span style="{}">{}</span>{}<a href="{}?cluster={}&amp;query={}">{}</a>'.format(
            style, protocol, separator, path, cluster_id, name, name)

    return client

# ################################################################################################################################

def get_inline_client_html(item, security_id, cluster_id):
    return get_client_html(
        item,
        security_id,
        cluster_id,
        style='font-size:default',
        separator=' : '
    )

# ################################################################################################################################

def get_endpoint_html(item, cluster_id, endpoint_name_attr='endpoint_name'):

    name = getattr(item, endpoint_name_attr, None) or item[endpoint_name_attr]

    path = django_url_reverse('pubsub-endpoint')
    endpoint = '<span style="font-size:smaller"><a href="{}?cluster={}&amp;query={}">{}</a></span>'.format(
        path, cluster_id, name, name)

    return endpoint

# ################################################################################################################################

def get_message(req, cluster_id, object_type, object_id, msg_id):

    return_data = bunchify({
        'action': 'update',
    })

    _has_gd = asbool(req.GET['has_gd'])
    _server_name = req.GET.get('server_name')
    _server_pid = req.GET.get('server_pid')

    _is_topic = object_type=='topic'
    suffix = '-gd' if _has_gd else '-non-gd'

    input_dict = {
        'cluster_id': cluster_id,
        'msg_id': msg_id,
    }

    if not _has_gd:
        input_dict['server_name'] = _server_name
        input_dict['server_pid'] = _server_pid

    return_data.cluster_id = cluster_id
    return_data.object_type = object_type
    return_data['{}_id'.format(object_type)] = object_id
    return_data.msg_id = msg_id
    return_data.server_name = _server_name
    return_data.server_pid = _server_pid
    return_data.has_gd = _has_gd

    if _is_topic:
        object_service_name = 'zato.pubsub.topic.get'
        msg_service_name = 'zato.pubsub.message.get-from-topic' + suffix
    else:
        object_service_name = 'zato.pubsub.endpoint.get-endpoint-queue'
        msg_service_name = 'zato.pubsub.message.get-from-queue' + suffix
        input_dict['sub_key'] = req.GET['sub_key']

    object_service_response = req.zato.client.invoke(
        object_service_name, {
        'cluster_id':cluster_id,
        'id':object_id,
    }).data.response

    return_data.object_name = object_service_response.name

    if object_type=='queue':
        return_data.ws_ext_client_id = object_service_response.ws_ext_client_id

    return_data.object_name_slug = slugify(return_data.object_name)

    try:
        msg_service_response = req.zato.client.invoke(msg_service_name, input_dict).data.response
    except Exception:
        logger.warning(format_exc())
        return_data.has_msg = False
    else:
        if not msg_service_response['msg_id']:
            return_data.has_msg = False
        else:
            return_data.has_msg = True
            return_data.update(msg_service_response)

            if _is_topic:
                hook_pub_endpoint_id = return_data.endpoint_id
                hook_sub_endpoint_id = None
                return_data.object_id = return_data.pop('topic_id')
                return_data.pub_endpoint_html = get_endpoint_html(return_data, cluster_id)
            else:

                # If it's a GD queue, we still need to get metadata about the message's underlying publisher
                if _has_gd:
                    topic_msg_service_response = req.zato.client.invoke(
                        'zato.pubsub.message.get-from-topic' + suffix, {
                        'cluster_id': cluster_id,
                        'msg_id': msg_id,
                        'needs_sub_queue_check': False,
                    }).data.response

                    return_data.topic_id = topic_msg_service_response.topic_id
                    return_data.topic_name = topic_msg_service_response.topic_name
                    return_data.pub_endpoint_id = topic_msg_service_response.endpoint_id
                    return_data.pub_endpoint_name = topic_msg_service_response.endpoint_name
                    return_data.pub_pattern_matched = topic_msg_service_response.pub_pattern_matched
                    return_data.pub_endpoint_html = get_endpoint_html(return_data, cluster_id, 'pub_endpoint_name')
                    return_data.sub_endpoint_html = get_endpoint_html(return_data, cluster_id, 'subscriber_name')
                    return_data.object_id = return_data.pop('queue_id')

                    hook_pub_endpoint_id = return_data.pub_endpoint_id
                    hook_sub_endpoint_id = return_data.subscriber_id

                    hook_pub_service_response = req.zato.client.invoke(
                        'zato.pubsub.hook.get-hook-service', {
                        'cluster_id': cluster_id,
                        'endpoint_id': hook_pub_endpoint_id,
                        'hook_type': PUBSUB.HOOK_TYPE.BEFORE_PUBLISH,
                    }).data.response

                    return_data.hook_pub_service_id = hook_pub_service_response.get('id')
                    return_data.hook_pub_service_name = hook_pub_service_response.get('name')

                    if hook_sub_endpoint_id:
                        hook_sub_service_response = req.zato.client.invoke(
                            'zato.pubsub.hook.get-hook-service', {
                            'cluster_id': cluster_id,
                            'endpoint_id': hook_sub_endpoint_id,
                            'hook_type': PUBSUB.HOOK_TYPE.BEFORE_DELIVERY,
                        }).data.response

                        return_data.hook_sub_service_id = hook_sub_service_response.get('id')
                        return_data.hook_sub_service_name = hook_sub_service_response.get('name')

            return_data.form = MsgForm(return_data)

            for name in('pub_time', 'ext_pub_time', 'expiration_time', 'recv_time'):
                value = return_data.get(name)
                if value:
                    return_data[name] = from_utc_to_user(value+'+00:00', req.zato.user_profile)
                    return_data[name + '_utc'] = value

    return TemplateResponse(req, 'zato/pubsub/message-details.html', return_data)
