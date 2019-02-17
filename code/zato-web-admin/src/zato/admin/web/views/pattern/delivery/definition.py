# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user, TARGET_TYPE_HUMAN
from zato.admin.web.forms.pattern.delivery.definition import CreateForm, DeliveryTargetForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.model import DeliveryItem

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pattern-delivery'
    template = 'zato/pattern/delivery/definition/index.html'
    service_name = 'zato.pattern.delivery.definition.get-list'
    output_class = DeliveryItem

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'target_type')
        output_required = ('id', 'name', 'callback_list', 'last_updated_utc', 'last_used_utc', 'target', 'target_type',
            'expire_after', 'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after',
            'retry_repeats', 'retry_seconds', 'short_def', 'total_count',
            'in_progress_count', 'in_doubt_count', 'confirmed_count', 'failed_count')
        output_repeated = True

    def on_before_append_item(self, item):
        if getattr(item, 'callback_list', None):
            item.callback_list = '\n'.join(item.callback_list.split(','))

        for name_utc in('last_updated_utc', 'last_used_utc'):
            value = getattr(item, name_utc, None)
            if value:
                name = name_utc.replace('_utc', '')
                setattr(item, name, from_utc_to_user(value + '+00:00', self.req.zato.user_profile))

        return item

    def handle(self):
        target_type = self.req.GET.get('target_type')
        return {
            'delivery_target_form': DeliveryTargetForm(self.req.GET),
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'target_type': target_type,
            'target_type_human': TARGET_TYPE_HUMAN[target_type] if target_type else '',
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ['name', 'target', 'target_type', 'expire_after',
            'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after',
            'retry_repeats', 'retry_seconds', 'callback_list']
        output_required = ['id', 'name', 'target', 'short_def']

    def __call__(self, req, initial_input_dict={}, initial_return_data={}, *args, **kwargs):
        self.set_input(req)
        initial_input_dict['callback_list'] = ','.join(elem for elem in (self.input.get('callback_list', None) or '').split())
        initial_return_data['name'] = self.input.name
        initial_return_data['target'] = self.input.target
        initial_return_data['short_def'] = '{}-{}-{}'.format(
            self.input.check_after, self.input.retry_repeats, self.input.retry_seconds)

        return super(_CreateEdit, self).__call__(req, initial_input_dict, initial_return_data, args, kwargs)

class Create(_CreateEdit):
    url_name = 'pattern-delivery-create'
    service_name = 'zato.pattern.delivery.definition.create'

    def success_message(self, item):
        return 'Definition [{}] created successfully'.format(item.name)

class Edit(_CreateEdit):
    url_name = 'pattern-delivery-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pattern.delivery.definition.edit'

    def success_message(self, item):
        return 'Definition [{}] updated successfully'.format(item.name)

class Delete(_Delete):
    url_name = 'pattern-delivery-delete'
    error_message = 'Could not delete delivery'
    service_name = 'zato.pattern.delivery.definition.delete'
