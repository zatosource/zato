# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.pattern.delivery import CreateForm, DeliveryTargetForm, EditForm, InstanceListForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, get_js_dt_format
from zato.common.model import DeliveryItem

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pattern-delivery'
    template = 'zato/pattern/delivery/index.html'
    service_name = 'zato.pattern.delivery.get-list'
    output_class = DeliveryItem
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'target_type')
        output_required = ('name', 'target', 'target_type', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count',
            'last_updated_utc')
        output_repeated = True
        
    def on_before_append_item(self, item):
        item.last_updated = from_utc_to_user(item.last_updated_utc + '+00:00', self.req.zato.user_profile)
        return item
        
    def handle(self):
        return {
            'delivery_target_form': DeliveryTargetForm(self.req.GET),
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'target_type': self.req.GET.get('target_type'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('zz',)
        output_required = ('id',)
        
    def success_message(self, item):
        return 'Successfully {0} delivery definition [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'pattern-delivery-create'
    service_name = 'zato.pattern.delivery.create'
    
class Edit(_CreateEdit):
    url_name = 'pattern-delivery-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pattern.delivery.edit'

class Delete(_Delete):
    url_name = 'pattern-delivery-delete'
    error_message = 'Could not delete delivery'
    service_name = 'zato.pattern.delivery.delete'

# ##############################################################################

class InDoubtInstanceList(_Index):
    method_allowed = 'GET'
    url_name = 'pattern-delivery-in-doubt-instance-list'
    template = 'zato/pattern/delivery/in-doubt/instance-list.html'
    service_name = 'zato.pattern.delivery.in-doubt.get-instance-list'
    output_class = DeliveryItem
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('name', 'target_type')
        input_optional = ('start', 'stop', 'batch_size', 'current_batch')
        output_required = ('name', 'target_type', 'tx_id', 'creation_time_utc', 'in_doubt_created_at_utc', 
            'source_count', 'target_count', 'retry_repeats', 'check_after', 'retry_seconds')
        output_repeated = True
        
    def on_before_append_item(self, item):
        item.creation_time = from_utc_to_user(item.creation_time_utc + '+00:00', self.req.zato.user_profile)
        item.in_doubt_created_at = from_utc_to_user(item.in_doubt_created_at_utc + '+00:00', self.req.zato.user_profile)
        return item
        
    def handle(self):
        out = {
            'form': InstanceListForm(initial=self.req.GET),
        }
        out.update(get_js_dt_format(self.req.zato.user_profile))

        service = 'zato.pattern.delivery.get-batch-info'
        req = {key:self.input[key] for key in ('name', 'batch_size', 'current_batch', 'start', 'stop') if self.input.get(key)}
        response = self.req.zato.client.invoke(service, req)
        
        out.update(response.data)
        
        return out

class InDoubtDetails(_Delete):
    url_name = 'pattern-delivery-details-in-doubt'
    service_name = 'zato.pattern.delivery.in-doubt.get-details'
    
# ##############################################################################
