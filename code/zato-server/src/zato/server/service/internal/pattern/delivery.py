# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# anyjson
from anyjson import loads

# Zato
from zato.common import DELIVERY_STATE, INVOCATION_TARGET, KVDB, ZatoException
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO

class _DeliveryService(AdminService):
        
    def _validate_input_dict(self, *validation_info):
        """ Checks that input belongs is one of allowed values.
        """
        for key_name, key, source in validation_info:
            if not source.has(key):
                msg = 'Invalid {}:[{}]'.format(key_name, key)
                log_msg = '{} (attrs: {})'.format(msg, source.attrs)
                
                self.logger.warn(log_msg)
                raise ZatoException(self.cid, msg)

class GetList(_DeliveryService):
    """ For a given target type, returns a list of existing deliveries regardless of their states.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_list_request'
        response_elem = 'zato_pattern_delivery_get_list_response'
        input_required = ('cluster_id', 'target_type')
        output_required = ('name', 'last_updated_utc', 'target', 'target_type', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count')
        
    def get_data(self, target_type):
        for name, base_target_info in self.delivery_store.get_by_target_type(target_type).items():
            base_target_info = loads(base_target_info)
            in_progress_count, in_doubt_count, arch_success_count, arch_failed_count = self.delivery_store.get_counts(name)

            yield {
                'name': name,
                'target':base_target_info['target'],
                'target_type': target_type,
                'last_updated_utc':base_target_info['last_updated_utc'],
                'short_def':'todo',
                'total_count':in_progress_count + in_doubt_count + arch_success_count + arch_failed_count,
                'in_progress_count':in_progress_count,
                'in_doubt_count':in_doubt_count,
                'arch_success_count':arch_success_count,
                'arch_failed_count':arch_failed_count
            }

    def handle(self):
        target_type = self.request.input.target_type
        self._validate_input_dict(('target_type', target_type, INVOCATION_TARGET))
            
        self.response.payload[:] = self.get_data(target_type)
        
class GetInstanceList(_DeliveryService):
    """ For a given delivery name, its state and target type, returns a list of instances of that delivery.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_instance_list_request'
        response_elem = 'zato_pattern_delivery_get_instance_list_response'
        input_required = ('name', 'target_type', 'state')
        output_required = ('name', 'target_type', AsIs('tx_id'))
        
    def handle(self):
        target_type = self.request.input.target_type
        state = self.request.input.state
        
        self._validate_input_dict(
            ('target_type', target_type, INVOCATION_TARGET),
            ('state', state, DELIVERY_STATE),)
        
        func_name = '_on_{}'.format(state.replace('-', '_'))
        self.response.payload[:] = getattr(self, func_name)(self.request.input.name, target_type)
        
    def _on_in_doubt(self, name, target_type):
        for item in self.delivery_store.get_in_doubt_instance_list(name):
            item['name'] = name
            item['target_type'] = target_type
            
            yield item
