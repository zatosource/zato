# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
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
from zato.common.util.json_ import dumps

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################


@method_allowed('GET')
def get(req, cluster_id, object_type, object_id, msg_id):

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
        logger.warn(format_exc())
        return_data.has_msg = False
    else:
        if not msg_service_response['msg_id']:
            return_data.has_msg = False
        else:
            return_data.has_msg = True
            return_data.update(msg_service_response)

            return_data.pub_endpoint_html = get_endpoint_html(return_data, cluster_id, 'published_by_id', 'published_by_name')
            return_data.sub_endpoint_html = get_endpoint_html(return_data, cluster_id, 'subscriber_id', 'subscriber_name')

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
                    return_data.pub_endpoint_html = get_endpoint_html(
                        return_data, cluster_id, 'pub_endpoint_id', 'pub_endpoint_name')
                    return_data.sub_endpoint_html = get_endpoint_html(
                        return_data, cluster_id, 'subscriber_id', 'subscriber_name')
                    return_data.object_id = return_data.pop('queue_id')

                    hook_pub_endpoint_id = return_data.pub_endpoint_id
                    hook_sub_endpoint_id = return_data.subscriber_id

                    hook_pub_service_response = req.zato.client.invoke(
                        'zato.pubsub.hook.get-hook-service', {
                        'cluster_id': cluster_id,
                        'endpoint_id': hook_pub_endpoint_id,
                        'hook_type': PUBSUB.HOOK_TYPE.BEFORE_PUBLISH,
                    }).data.response
                    return_data.hook_pub_service_id = hook_pub_service_response.id
                    return_data.hook_pub_service_name = hook_pub_service_response.name

                    if hook_sub_endpoint_id:
                        hook_sub_service_response = req.zato.client.invoke(
                            'zato.pubsub.hook.get-hook-service', {
                            'cluster_id': cluster_id,
                            'endpoint_id': hook_sub_endpoint_id,
                            'hook_type': PUBSUB.HOOK_TYPE.BEFORE_DELIVERY,
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

    has_gd = asbool(req.POST['has_gd'])
    expiration = req.POST.get('expiration')
    exp_from_now = asbool(req.POST.get('exp_from_now'))

    correl_id = req.POST.get('correl_id')
    in_reply_to = req.POST.get('in_reply_to')

    priority = req.POST['priority']
    mime_type = req.POST['mime_type']
    data = req.POST['data']

    server_name = req.POST['server_name']
    server_pid = req.POST['server_pid']

    try:
        expiration_time = None
        size = None

        input = {
            'cluster_id': cluster_id,
            'data': data,
            'expiration': expiration,
            'exp_from_now': exp_from_now,
            'correl_id': correl_id,
            'in_reply_to': in_reply_to,
            'priority': priority,
            'mime_type': mime_type,
            'server_name': server_name,
            'server_pid': server_pid,
        }

        if msg_id:
            input['msg_id'] = msg_id

        if action == 'update':
            suffix = '-gd' if has_gd else '-non-gd'
            action += suffix

        response = req.zato.client.invoke('zato.pubsub.message.{}'.format(action), input).data.response

    except Exception:
        is_ok = False
        message = format_exc()

    else:

        if not response.found:
            is_ok = False
            message = 'Could not find message `{}`'.format(response.msg_id)
        else:
            is_ok = True
            message = 'Message {}'.format('updated' if action.startswith('update') else 'created')
            size = response.size
            if response.expiration_time:

                expiration_time = """
                <a
                    id="a_expiration_time"
                    href="javascript:$.fn.zato.pubsub.message.details.toggle_time('expiration_time', '{expiration_time_user}', '{expiration_time_utc}')">{expiration_time_user}
                </a>
                """.format(**{
                       'expiration_time_utc': response.expiration_time,
                       'expiration_time_user': from_utc_to_user(response.expiration_time+'+00:00', req.zato.user_profile),
                })

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

    topic_list_response = req.zato.client.invoke('zato.pubsub.topic.get-list', {
        'cluster_id': cluster_id,
        'needs_details': False,
    }).data

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

        for name in('reply_to_sk', 'deliver_to_sk'):
            value = req.POST.get(name, '')
            if value:
                value = value.split(',')
                value = [elem.strip() for elem in value]
                service_input[name] = value

        for name in('cluster_id', 'topic_name', 'data'):
            service_input[name] = req.POST[name]

        for name in('correl_id', 'priority', 'ext_client_id', 'position_in_group', 'expiration', 'in_reply_to'):
            service_input[name] = req.POST.get(name, None) or None # Always use None instead of ''

        req.zato.client.invoke('zato.pubsub.publish.publish', service_input)

    except Exception as e:
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

    input_dict = {
        'cluster_id': cluster_id,
        'msg_id': msg_id,
    }

    object_type = req.POST['object_type']

    if object_type == 'queue':
        input_dict['sub_key'] = req.POST['sub_key']

    if req.POST['has_gd']:
        service_name = 'zato.pubsub.message.{}-delete-gd'.format(object_type)
    else:
        service_name = 'zato.pubsub.message.{}-delete-non-gd'.format(object_type)

    if service_name == 'zato.pubsub.message.queue-delete-non-gd':

        # This is an in-RAM message so it needs additional information
        input_dict['server_name'] = req.POST['server_name']
        input_dict['server_pid'] = req.POST['server_pid']

    try:
        req.zato.client.invoke(service_name, input_dict)
    except Exception:
        return HttpResponseServerError(format_exc())
    else:
        return HttpResponse('Deleted message `{}`'.format(msg_id))

# ################################################################################################################################
