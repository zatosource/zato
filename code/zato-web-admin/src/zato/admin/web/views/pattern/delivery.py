# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.pattern.delivery import CreateForm, DeliveryTargetForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
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
        output_required = ('name', 'target', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count')
        output_repeated = True
        
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
