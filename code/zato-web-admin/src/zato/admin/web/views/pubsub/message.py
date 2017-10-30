# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pubsub import MsgForm
from zato.admin.web.views import method_allowed
from zato.admin.web.views.pubsub import get_endpoint_html

# ################################################################################################################################

@method_allowed('GET')
def get(req, cluster_id, object_type, object_id, msg_id):

    return_data = {
        'action': 'update',
    }

    return_data['cluster_id'] = cluster_id
    return_data['object_type'] = object_type
    return_data['{}_id'.format(object_type)] = object_id
    return_data['endpoint_html'] = get_endpoint_html(return_data, cluster_id)

    return_data.update(req.zato.client.invoke('zato.pubsub.message.get', {
        'cluster_id': cluster_id,
        'msg_id': msg_id,
    }).data.response)

    return_data['form'] = MsgForm(return_data)
    return_data.pub_time = from_utc_to_user(return_data.pub_time+'+00:00', req.zato.user_profile)

    if return_data.ext_pub_time:
        return_data.ext_pub_time = from_utc_to_user(return_data.ext_pub_time+'+00:00', req.zato.user_profile)

    if return_data.expiration_time:
        return_data.expiration_time = from_utc_to_user(return_data.expiration_time+'+00:00', req.zato.user_profile)

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
        message = 'Message {}'.format
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
    _publish_update_action(req, cluster_id, 'update', msg_id)

# ################################################################################################################################

@method_allowed('GET')
def publish(req, cluster_id, topic_id):
    return_data = {
        'action': 'publish',
        'form': MsgForm()
    }
    return TemplateResponse(req, 'zato/pubsub/message-details.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def publish_action(req, cluster_id, topic_id):
    _publish_update_action(req, cluster_id, 'publish', topic_id=topic_id)

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
