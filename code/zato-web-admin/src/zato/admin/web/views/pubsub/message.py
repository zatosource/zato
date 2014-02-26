# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

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
from zato.admin.web import from_utc_to_user, last_hour_start_stop
from zato.admin.web.views import method_allowed
from zato.common import PUB_SUB
from zato.common.pubsub import Message

@method_allowed('GET')
def index_topic(req, cluster_id, topic_name):

    items = []
    input_dict = {
        'cluster_id': cluster_id,
        'source_name':topic_name,
        'source_type': PUB_SUB.MESSAGE_SOURCE.TOPIC.id
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
        'source_type': PUB_SUB.MESSAGE_SOURCE.TOPIC.id
        }
        
    return TemplateResponse(req, 'zato/pubsub/message/index.html', return_data)
    
@method_allowed('GET')
def details_topic(req, cid, service_name):

    item = None
    service = _get_service(req, service_name)
    pretty_print = asbool(req.GET.get('pretty_print'))
    
    input_dict = {
        'cid': cid,
        'name': service_name,
    }
    response = req.zato.client.invoke('zato.service.slow-response.get', input_dict)
    
    if response.has_data:
        cid = response.data.cid
        if cid != ZATO_NONE:
            item = SlowResponse()
            item.cid = response.data.cid
            item.req_ts = from_utc_to_user(response.data.req_ts+'+00:00', req.zato.user_profile)
            item.resp_ts = from_utc_to_user(response.data.resp_ts+'+00:00', req.zato.user_profile)
            item.proc_time = response.data.proc_time
            item.service_name = service_name
            item.threshold = service.slow_threshold
            
            for name in('req', 'resp'):
                value = getattr(response.data, name)
                if value:
                    #value = value.decode('base64')
                    if isinstance(value, dict):
                        value = dumps(value)
                        data_format = 'json'
                    else:
                        data_format = known_data_format(value)
                        
                    if data_format:
                        if pretty_print:
                            value = get_pretty_print(value, data_format)
                        attr_name = name + '_html'
                        setattr(item, attr_name, highlight(value, 
                             data_format_lexer[data_format](), HtmlFormatter(linenos='table')))

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'service': service,
        'item': item,
        'pretty_print': not pretty_print,
        }
        
    return TemplateResponse(req, 'zato/service/slow-response-details.html', return_data)

@method_allowed('POST')
def delete(req):
    try:
        response = req.zato.client.invoke('zato.pubsub.message.delete', {
            'msg_id': req.POST['id'],
            'name': req.POST['name'],
            'source_type': req.POST['source_type'],
        })
        if response.ok:
            return HttpResponse(dumps(''), mimetype='application/javascript')
        else:
            raise Exception(response.details)
    except Exception, e:
        return HttpResponseServerError(format_exc(e))