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
from zato.admin.web.views import django_url_reverse, method_allowed

# ################################################################################################################################

def get_client_html(item, security_id, cluster_id):
    """ Client is a string representation of a WebSockets channel, HTTP credentials or a service.
    """
    client = ''

    if security_id:
        path_name = 'security-basic-auth'
        id_value = security_id
        name = item.sec_name
        protocol = 'HTTP'

    elif item.ws_channel_id:
        path_name = 'channel-web-socket'
        id_value = item.ws_channel_id
        name = item.ws_channel_name
        protocol = 'WebSockets'

    elif item.service_id:
        path_name = 'service'
        id_value = item.service_id
        name = item.service_name
        protocol = 'Service'

    path = django_url_reverse(path_name)
    client = '<span style="font-size:smaller">{}</span><br/><a href="{}?cluster={}&amp;highlight={}">{}</a>'.format(
        protocol, path, cluster_id, id_value, name)

    return client

# ################################################################################################################################

def get_endpoint_html(item, cluster_id):
    path_name = 'endpoint'
    id_value = item.endpoint_id
    name = item.endpoint_name

    path = django_url_reverse('pubsub-endpoint')
    endpoint = '<span style="font-size:smaller"><a href="{}?cluster={}&amp;highlight={}">{}</a>'.format(
        path, cluster_id, id_value, name)

    return endpoint

# ################################################################################################################################

@method_allowed('GET')
def message(req, cluster_id, object_type, object_id, msg_id):

    return_data = req.zato.client.invoke('zato.pubsub.message.get', {
        'cluster_id': cluster_id,
        'msg_id': msg_id,
    }).data.response

    return_data.pub_time = from_utc_to_user(return_data.pub_time+'+00:00', req.zato.user_profile)

    if return_data.ext_pub_time:
        return_data.ext_pub_time = from_utc_to_user(return_data.ext_pub_time+'+00:00', req.zato.user_profile)

    if return_data.expiration_time:
        return_data.expiration_time = from_utc_to_user(return_data.expiration_time+'+00:00', req.zato.user_profile)

    return_data.cluster_id = cluster_id
    return_data.object_type = object_type
    return_data['{}_id'.format(object_type)] = object_id
    return_data.form = MsgForm(return_data)
    return_data.endpoint_html = get_endpoint_html(return_data, cluster_id)

    return TemplateResponse(req, 'zato/pubsub/message-details.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def update_message(req, cluster_id, msg_id):

    expiration = req.POST.get('expiration')
    correl_id = req.POST.get('correl_id')
    in_reply_to = req.POST.get('in_reply_to')

    priority = req.POST['priority']
    mime_type = req.POST['mime_type']
    data = req.POST['data']

    try:
        expiration_time = None
        size = None

        response = req.zato.client.invoke('zato.pubsub.message.update', {
            'cluster_id': cluster_id,
            'msg_id': msg_id,
            'data': data,
            'expiration': expiration,
            'correl_id': correl_id,
            'in_reply_to': in_reply_to,
            'priority': priority,
            'mime_type': mime_type,
        }).data.response

    except Exception, e:
        is_ok = False
        message = format_exc(e)

    else:
        is_ok = True
        message = 'Message updated'
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
