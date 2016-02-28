# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps, loads
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# lxml
from lxml import etree

# Paste
from paste.util.converters import asbool

# Pygments
from pygments.lexers.web import JSONLexer
from pygments.lexers import MakoXmlLexer

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import method_allowed
from zato.common import PUB_SUB
from zato.common.pubsub import Message

data_format_lexer = {
    'json': JSONLexer,
    'xml': MakoXmlLexer
}

def known_data_format(data):
    data_format = None
    try:
        etree.fromstring(data)
        data_format = 'xml'
    except etree.XMLSyntaxError:
        try:
            loads(data)
            data_format = 'json'
        except ValueError:
            pass

    return data_format

# ################################################################################################################################

def _index(req, cluster_id, topic_name, source_name, source_type):
    items = []
    input_dict = {
        'cluster_id': cluster_id,
        'source_name':source_name,
        'source_type': source_type
    }

    for _item in req.zato.client.invoke('zato.pubsub.message.get-list', input_dict):
        _item = Message(**_item)
        _item.creation_time = from_utc_to_user(_item.creation_time_utc+'+00:00', req.zato.user_profile)
        _item.expire_at = from_utc_to_user(_item.expire_at_utc+'+00:00', req.zato.user_profile)
        _item.id = _item.msg_id
        items.append(_item)

    return_data = {
        'topic_name': topic_name,
        'cluster_id': req.zato.cluster_id,
        'items': items,
        'source_type': source_type,
        'source_name': source_name
        }

    return TemplateResponse(req, 'zato/pubsub/message/index.html', return_data)

# ################################################################################################################################

@method_allowed('GET')
def index_topic(req, cluster_id, topic_name):
    return _index(req, cluster_id, topic_name, topic_name, PUB_SUB.MESSAGE_SOURCE.TOPIC.id)

# ################################################################################################################################

@method_allowed('GET')
def index_consumer_queue(req, cluster_id, sub_key, topic_name):
    return _index(req, cluster_id, topic_name, sub_key, PUB_SUB.MESSAGE_SOURCE.CONSUMER_QUEUE.id)

# ################################################################################################################################

@method_allowed('GET')
def details(req, source_type, cluster_id, msg_id, topic_name):

    item = None
    pretty_print = asbool(req.GET.get('pretty_print'))

    input_dict = {
        'cluster_id': cluster_id,
        'msg_id': msg_id,
    }
    response = req.zato.client.invoke('zato.pubsub.message.get', input_dict)

    if response.has_data:
        item = Message()
        for name in('topic', 'producer', 'priority', 'mime_type', 'expiration', 'creation_time_utc', 'expire_at_utc', 'payload'):
            setattr(item, name, getattr(response.data, name, None))

        item.creation_time = from_utc_to_user(item.creation_time_utc+'+00:00', req.zato.user_profile)
        item.expire_at = from_utc_to_user(item.expire_at_utc+'+00:00', req.zato.user_profile)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'item': item,
        'pretty_print': not pretty_print,
        'msg_id': msg_id,
        'topic_name': topic_name,
        'source_type': source_type,
        'sub_key': req.GET.get('sub_key')
        }

    return TemplateResponse(req, 'zato/pubsub/message/details.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def delete(req):
    try:
        response = req.zato.client.invoke('zato.pubsub.message.delete', {
            'cluster_id': req.zato.cluster_id,
            'msg_id': req.POST['id'],
            'source_name': req.POST['source_name'],
            'source_type': req.POST['source_type'],
        })
        if response.ok:
            return HttpResponse(dumps(''), content_type='application/javascript')
        else:
            raise Exception(response.details)
    except Exception, e:
        return HttpResponseServerError(format_exc(e))

# ################################################################################################################################
