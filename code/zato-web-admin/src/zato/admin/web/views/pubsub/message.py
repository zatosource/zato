# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps
from traceback import format_exc

# Bunch
from bunch import bunchify

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub import MsgForm, MsgPublishForm
from zato.admin.web.views import method_allowed, slugify
from zato.admin.web.views.pubsub import get_endpoint_html
from zato.common import PUBSUB
from zato.common.pubsub import new_msg_id
from zato.common.util import asbool

# ################################################################################################################################

@method_allowed('GET')
def get(req, cluster_id, object_type, object_id, msg_id):

    return_data = bunchify({
        'action': 'update',
    })

    return_data.cluster_id = cluster_id
    return_data.object_type = object_type
    return_data['{}_id'.format(object_type)] = object_id
    return_data.msg_id = msg_id

    if object_type=='topic':
        object_service_name = 'zato.pubsub.topic.get'
        msg_service_name = 'zato.pubsub.message.get-from-topic'
    else:
        object_service_name = 'zato.pubsub.endpoint.get-endpoint-queue'
        msg_service_name = 'zato.pubsub.message.get-from-queue'

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
        msg_service_response = req.zato.client.invoke(
            msg_service_name, {
            'cluster_id': cluster_id,
            'msg_id': msg_id,
        }).data.response

    except Exception:
        return_data.has_msg = False

    else:
        return_data.has_msg = True
        return_data.update(msg_service_response)

        if object_type=='topic':
            hook_pub_endpoint_id = return_data.endpoint_id
            hook_sub_endpoint_id = None
            return_data.object_id = return_data.pop('topic_id')
            return_data.pub_endpoint_html = get_endpoint_html(return_data, cluster_id)
        else:

            # If it's a queue, we still need to get metadata about the message's underlying publisher
            topic_msg_service_response = req.zato.client.invoke(
                'zato.pubsub.message.get-from-topic', {
                'cluster_id': cluster_id,
                'msg_id': msg_id,
            }).data.response

            return_data.topic_id = topic_msg_service_response.topic_id
            return_data.topic_name = topic_msg_service_response.topic_name
            return_data.pub_endpoint_id = topic_msg_service_response.endpoint_id
            return_data.pub_endpoint_name = topic_msg_service_response.endpoint_name
            return_data.pub_pattern_matched = topic_msg_service_response.pattern_matched
            return_data.pub_endpoint_html = get_endpoint_html(return_data, cluster_id, 'pub_endpoint_id', 'pub_endpoint_name')
            return_data.sub_endpoint_html = get_endpoint_html(return_data, cluster_id)
            return_data.object_id = return_data.pop('queue_id')

            hook_pub_endpoint_id = return_data.pub_endpoint_id
            hook_sub_endpoint_id = return_data.endpoint_id

        hook_pub_service_response = req.zato.client.invoke(
            'zato.pubsub.hook.get-hook-service', {
            'cluster_id': cluster_id,
            'endpoint_id': hook_pub_endpoint_id,
            'hook_type': PUBSUB.HOOK_TYPE.PUB,
        }).data.response
        return_data.hook_pub_service_id = hook_pub_service_response.id
        return_data.hook_pub_service_name = hook_pub_service_response.name

        if hook_sub_endpoint_id:
            hook_sub_service_response = req.zato.client.invoke(
                'zato.pubsub.hook.get-hook-service', {
                'cluster_id': cluster_id,
                'endpoint_id': hook_sub_endpoint_id,
                'hook_type': PUBSUB.HOOK_TYPE.SUB,
            }).data.response
            return_data.hook_sub_service_id = hook_sub_service_response.id
            return_data.hook_sub_service_name = hook_sub_service_response.name

        return_data.form = MsgForm(return_data)

        for name in('pub_time', 'ext_pub_time', 'expiration_time', 'recv_time'):
            value = return_data.get(name)
            if value:
                return_data[name] = from_utc_to_user(value+'+00:00', req.zato.user_profile)
                return_data[name + '_utc'] = value

    return TemplateResponse(req, 'zato/pubsub/message-details.html', return_data)

# ################################################################################################################################

def _publish_update_action(req, cluster_id, action, msg_id=None, topic_id=None):

    expiration = req.POST.get('expiration')
    correl_id = req.POST.get('correl_id')
    in_reply_to = req.POST.get('in_reply_to')

    priority = req.POST['priority']
    mime_type = req.POST['mime_type']
    data = req.POST['data']

    try:
        expiration_time = None
        size = None

        input = {
            'cluster_id': cluster_id,
            'data': data,
            'expiration': expiration,
            'correl_id': correl_id,
            'in_reply_to': in_reply_to,
            'priority': priority,
            'mime_type': mime_type,
        }

        if msg_id:
            input['msg_id'] = msg_id

        response = req.zato.client.invoke('zato.pubsub.message.{}'.format(action), input).data.response

    except Exception, e:
        is_ok = False
        message = format_exc(e)

    else:
        is_ok = True
        message = 'Message {}'.format('updated' if action=='update' else 'created')
        size = response.size
        if response.expiration_time:
            expiration_time = from_utc_to_user(response.expiration_time+'+00:00', req.zato.user_profile)

    return HttpResponse(dumps({
        'is_ok': is_ok,
        'message': message,
        'expiration_time': expiration_time,
        'size': size
    }))

# ################################################################################################################################

@method_allowed('POST')
def update_action(req, cluster_id, msg_id):
    return _publish_update_action(req, cluster_id, 'update', msg_id)

# ################################################################################################################################

@method_allowed('GET')
def publish(req, cluster_id, topic_id):

    topic_list = []
    publisher_list = []
    topic_id = int(topic_id)
    initial_topic_name = None
    initial_hook_service_name = None
    select_changer_data = {}

    topic_list_response = req.zato.client.invoke('zato.pubsub.topic.get-list', {'cluster_id':cluster_id}).data
    for item in topic_list_response:

        # Initial data for this topic
        if item.id == topic_id:
            initial_topic_name = item.name
            initial_hook_service_name = item.hook_service_name

        # All topics -> hook service names for select changer
        select_changer_data[item.name] = item.hook_service_name or ''

        topic_list.append({'id':item.name, 'name':item.name}) # Topics are identified by their name, not ID

    publisher_list_response = req.zato.client.invoke('zato.pubsub.endpoint.get-list', {'cluster_id':cluster_id}).data
    for item in publisher_list_response:
        for line in (item.topic_patterns or '').splitlines():
            if line.startswith('sub='):
                publisher_list.append({'id':item.id, 'name':item.name})
                break

    return_data = {
        'cluster_id': cluster_id,
        'action': 'publish',
        'form': MsgPublishForm(req, dumps(select_changer_data), initial_topic_name, topic_list,
            initial_hook_service_name, publisher_list)
    }

    return TemplateResponse(req, 'zato/pubsub/message-publish.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def publish_action(req):

    try:

        msg_id = req.POST.get('msg_id') or new_msg_id()
        gd = req.POST['gd']

        if gd == PUBSUB.GD_CHOICE.DEFAULT_PER_TOPIC.id:
            has_gd = None
        else:
            has_gd = asbool(gd)

        service_input = {
            'msg_id': msg_id,
            'has_gd': has_gd,
            'skip_pattern_matching': True,
            'endpoint_id': req.POST['publisher_id'],
        }

        for name in('cluster_id', 'topic_name', 'data'):
            service_input[name] = req.POST[name]

        for name in('correl_id', 'priority', 'ext_client_id', 'position_in_group'):
            service_input[name] = req.POST[name] or None

        req.zato.client.invoke('zato.pubsub.publish.publish', service_input)

    except Exception, e:
        message = e.message
        is_ok = False
    else:
        message = 'Successfully published message `{}`'.format(msg_id)
        is_ok = True

    return HttpResponse(dumps({
        'is_ok': is_ok,
        'message': message,
    }))

# ################################################################################################################################

@method_allowed('POST')
def delete(req, cluster_id, msg_id):

    try:
        req.zato.client.invoke('zato.pubsub.message.delete', {
            'cluster_id': cluster_id,
            'msg_id': msg_id,
        })
    except Exception, e:
        return HttpResponseServerError(format_exc(e))
    else:
        return HttpResponse('Deleted message `{}`'.format(msg_id))

# ################################################################################################################################
