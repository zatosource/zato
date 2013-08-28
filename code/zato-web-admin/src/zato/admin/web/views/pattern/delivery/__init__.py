# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from json import dumps, loads
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web import from_utc_to_user, from_user_to_utc, TARGET_TYPE_HUMAN
from zato.admin.web.forms.pattern.delivery.definition import CreateForm, DeliveryTargetForm, EditForm, InstanceListForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, get_js_dt_format, method_allowed
from zato.common import DELIVERY_STATE
from zato.common.model import DeliveryItem

logger = logging.getLogger(__name__)

def _drop_utc(item, req):
    item.creation_time = from_utc_to_user(item.creation_time_utc + '+00:00', req.zato.user_profile)
    item.in_doubt_created_at = from_utc_to_user(item.in_doubt_created_at_utc + '+00:00', req.zato.user_profile)
    
    return item

class Details(_Index):
    url_name = 'pattern-delivery-details'
    template = 'zato/pattern/delivery/details.html'
    service_name = 'zato.pattern.delivery.get-details'
    output_class = DeliveryItem
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('task_id',)
        output_required = ('def_name', 'target_type', 'task_id', 'creation_time_utc', 'in_doubt_created_at_utc', 
                    'source_count', 'target_count', 'resubmit_count', 'state', 'retry_repeats', 'check_after', 'retry_seconds')
        output_optional = ('payload', 'args', 'kwargs', 'payload_sha1', 'payload_sha256')
        output_repeated = False
        
    def _handle_item(self, item):
        self.item = _drop_utc(item, self.req)
        self.item.args = '\n'.join('{}'.format(elem) for elem in loads(self.item.args))
        self.item.kwargs = '\n'.join('{}={}'.format(k,v) for k, v in loads(self.item.kwargs).items())
        if self.item.payload:
            self.item.payload_len = len(self.item.payload)
    
    def handle(self):
        
        out = {}
        service = 'zato.pattern.delivery.get-history-list'
        req = {'task_id': self.input['task_id']}
        response = self.req.zato.client.invoke(service, req)

        if response.ok:
            for item in response.data:
                item.entry_time = from_utc_to_user(item.entry_time + '+00:00', self.req.zato.user_profile)
                
            return {'history': response.data}
        else:
            logger.warn(response.details)
