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

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ['name', 'target', 'target_type', 'expire_after',
            'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after', 
            'retry_repeats', 'retry_seconds']
        output_required = []

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pattern-delivery-in-doubt-index'
    template = 'zato/pattern/delivery/in-doubt/index.html'
    service_name = 'zato.pattern.delivery.in-doubt.get-list'
    output_class = DeliveryItem
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('def_name',)
        input_optional = ('batch_size', 'current_batch', 'start', 'stop',)
        output_required = ('def_name', 'target_type', 'task_id', 'creation_time_utc', 'in_doubt_created_at_utc', 
            'source_count', 'target_count', 'resubmit_count', 'retry_repeats', 'check_after', 'retry_seconds')
        output_repeated = True
        
    def on_before_append_item(self, item):
        return _drop_utc(item, self.req)
    
    def on_after_set_input(self):
        for name in('start', 'stop'):
            if self.input.get(name):
                self.input[name] = from_user_to_utc(self.input[name], self.req.zato.user_profile)
        
    def handle(self):
        out = {'form': InstanceListForm(initial=self.req.GET)}
        out.update(get_js_dt_format(self.req.zato.user_profile))

        service = 'zato.pattern.delivery.get-batch-info'
        req = {key:self.input[key] for key in ('def_name', 'batch_size', 'current_batch', 'start', 'stop') if self.input.get(key)}
        req['state'] = DELIVERY_STATE.IN_DOUBT
        response = self.req.zato.client.invoke(service, req)

        if response.ok:
            out.update(response.data)
        else:
            logger.warn(response.details)
        
        return out

# ##############################################################################
