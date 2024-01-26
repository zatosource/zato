# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub import MsgPublishForm
from zato.admin.web.views import method_allowed
from zato.admin.web.views.pubsub import get_message
from zato.common.api import PUBSUB
from zato.common.json_internal import dumps
from zato.common.pubsub import new_msg_id
from zato.common.util.api import asbool

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

@method_allowed('GET')
def get(req, cluster_id, object_type, object_id, msg_id):
    return get_message(req, cluster_id, object_type, object_id, msg_id)

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
                    href="javascript:$.fn.zato.pubsub.message.details.toggle_time('expiration_time', '{exp_time_user}', '{exp_time_utc}')">{exp_time_user}
                </a>
                """.format(**{
                       'exp_time_utc': response.expiration_time,
                       'exp_time_user': from_utc_to_user(response.expiration_time+'+00:00', req.zato.user_profile),
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

    initial_publisher_id = None

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
                if item.name == PUBSUB.DEFAULT.INTERNAL_ENDPOINT_NAME:
                    initial_publisher_id = item.id
                break

    return_data = {
        'cluster_id': cluster_id,
        'action': 'publish',
        'default_message': PUBSUB.DEFAULT.Dashboard_Message_Body,
        'form': MsgPublishForm(
            req,
            dumps(select_changer_data),
            initial_topic_name, topic_list,
            initial_hook_service_name,
            publisher_list,
            initial={'publisher_id': initial_publisher_id}
        )}

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
        message = e.args[0]
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
