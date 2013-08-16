# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# anyjson
from traceback import format_exc

# datetutil
from dateutil.parser import parse

from memory_profiler import profile

# Zato
from zato.common import DEFAULT_DELIVERY_INSTANCE_LIST_BATCH_SIZE, DELIVERY_STATE, INVOCATION_TARGET, KVDB, ZatoException
from zato.common.odb.model import DeliveryDefinitionBase
from zato.common.odb.query import delivery_definition_list
from zato.common.util import datetime_to_seconds
from zato.server.service import AsIs, Boolean, CSV, Integer
from zato.server.service.internal import AdminService, AdminSIO

class _DeliveryService(AdminService):
    """ Base class with code common to multiple guaranteed delivery-related services.
    """
    def _validate_input_dict(self, *validation_info):
        """ Checks that input belongs is one of allowed values.
        """
        for key_name, key, source in validation_info:
            if not source.has(key):
                msg = 'Invalid {}:[{}]'.format(key_name, key)
                log_msg = '{} (attrs: {})'.format(msg, source.attrs)
                
                self.logger.warn(log_msg)
                raise ZatoException(self.cid, msg)
            
    def _batch_size_from_input(self):
        """ Returns a batch size taking into account handling of invalid input values.
        """
        try:
            batch_size = self.request.input.get('batch_size')
            batch_size = int(batch_size) or DEFAULT_DELIVERY_INSTANCE_LIST_BATCH_SIZE
        except(TypeError, ValueError), e:
            self.logger.debug('Invalid batch_size in:[%s], e:[%s]', batch_size, format_exc(e))
            batch_size = DEFAULT_DELIVERY_INSTANCE_LIST_BATCH_SIZE
            
        return batch_size
    
class GetList(_DeliveryService):
    """ Returns a list of delivery definitions for a given target type on a cluster.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_definition_get_list_request'
        response_elem = 'zato_pattern_delivery_definition_get_list_response'
        input_required = ('cluster_id', 'target_type')
        output_required = ('name', 'last_updated_utc', 'target', 'target_type', 
            'expire_after', 'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after', 
            'retry_repeats', 'retry_seconds', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count')

    def get_data(self, session, cluster_id, target_type):
        return delivery_definition_list(session, cluster_id, target_type)

    def handle(self):
        target_type = self.request.input.target_type
        self._validate_input_dict(('target_type', target_type, INVOCATION_TARGET))
        
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session, self.request.input.cluster_id, target_type)

class Create(AdminService):
    """ Creates a new delivery definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_definition_create_request'
        response_elem = 'zato_pattern_delivery_definition_create_response'
        input_required = ('cluster_id', 'name', 'target', 'target_type', 'expire_after', 
            'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after', 
            'retry_repeats', 'retry_seconds',)
        output_required = ('id', 'name')
        
        
    def handle(self):
        with closing(self.odb.session()) as session:
            input = self.request.input
            
            # Both raise an Exception if a check fails
            self._check_def_name(input)
            self._check_target_name(input)
            
            target_class = self._get_target_class(input)
            
            try:
                item = target_class()
                
                session.add(item)
                session.commit()
                
                self.response.payload.id = item.id
                self.response.payload.name = item.name
                
            except Exception, e:
                msg = 'Could not create the definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
    def _check_def_name(self, input):
        
        # Let's see if we already have a definition of that name before committing
        # any stuff into the database.
        existing_one = session.query(DeliveryDefinitionBase.id).\
            filter(DeliveryDefinitionBase.cluster_id==input.cluster_id).\
            filter(DeliveryDefinitionBase.name==input.name).\
            first()
        
        if existing_one:
            raise Exception('Definition [{0}] already exists on this cluster'.format(input.name))
        
    def _check_target_name(self, input):
        pass
    
    def _get_short_def(self, input):
        pass