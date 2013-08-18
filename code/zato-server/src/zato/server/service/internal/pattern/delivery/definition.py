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
from zato.common.odb.model import DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ, OutgoingWMQ
from zato.common.odb.query import delivery_definition_list, out_jms_wmq, out_jms_wmq_by_name
from zato.common.util import datetime_to_seconds
from zato.server.service import AsIs, Boolean, CSV, Integer
from zato.server.service.internal import AdminService, AdminSIO

_target_query_by_id = {
    INVOCATION_TARGET.OUTCONN_WMQ: out_jms_wmq
}

_target_query_by_name = {
    INVOCATION_TARGET.OUTCONN_WMQ: out_jms_wmq_by_name
}

_target_def_class = {
    INVOCATION_TARGET.OUTCONN_WMQ: DeliveryDefinitionOutconnWMQ
}

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
        output_required = ('id', 'name', 'target', 'target_type', 
            'expire_after', 'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after', 
            'retry_repeats', 'retry_seconds', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count')
        output_optional = ('last_updated_utc',)

    def get_data(self, session, cluster_id, target_type):
        for item in delivery_definition_list(session, cluster_id, target_type):
            
            target_query = _target_query_by_id[target_type]
            target = target_query(session, cluster_id, item.target_id)
           
            out = {
                'target': target.name,
                'target_type': target_type
            }
            
            for name in ('id', 'name', 'expire_after', 'expire_arch_succ_after', 
                  'expire_arch_fail_after', 'check_after', 'retry_repeats', 'retry_seconds', 'short_def'):
                out[name] = getattr(item, name)
            
            basic_data = self.delivery_store.get_target_basic_data(target.name)
            for name in ('last_updated_utc', 'total_count', 'in_progress_count', 
                             'in_doubt_count', 'arch_success_count', 'arch_failed_count'):
                out[name] = basic_data[name]
            
            yield out

    def handle(self):
        target_type = self.request.input.target_type
        self._validate_input_dict(('target_type', target_type, INVOCATION_TARGET))
        
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session, self.request.input.cluster_id, target_type)

class Create(_DeliveryService):
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
        target_type = self.request.input.target_type
        self._validate_input_dict(('target_type', target_type, INVOCATION_TARGET))
        
        with closing(self.odb.session()) as session:
            input = self.request.input
            self._check_def_name(session, input)
            
            target_query = _target_query_by_name[target_type]
            target = target_query(session, input.cluster_id, input.target)
            if not target:
                raise Exception('Target [{}] ({}) does not exist on this cluster'.format(
                    input.target, input.target_type))
                
            target_def_class = _target_def_class[target_type]
            
            try:
                item = target_def_class()
                item.target_id = target.id
                item.short_def = '{}-{}-{}'.format(input.check_after, input.retry_repeats, input.retry_seconds)
                
                item.name = input.name
                item.target_type = input.target_type
                item.expire_after = input.expire_after
                item.expire_arch_succ_after = input.expire_arch_succ_after
                item.expire_arch_fail_after = input.expire_arch_fail_after
                item.check_after = input.check_after
                item.retry_repeats = input.retry_repeats
                item.retry_seconds = input.retry_seconds
                item.cluster_id = input.cluster_id
                
                session.add(item)
                session.commit()
                
                self.delivery_store.set_deleted(item.name, False)
                
                self.response.payload.id = item.id
                self.response.payload.name = item.name
                
            except Exception, e:
                msg = 'Could not create the definition, e:[{}]'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 
            
    def _check_def_name(self, session, input):
        """ Let's see if we already have a definition of that name before committing
        any stuff into the database.
        """
        existing_one = session.query(DeliveryDefinitionBase.id).\
            filter(DeliveryDefinitionBase.cluster_id==input.cluster_id).\
            filter(DeliveryDefinitionBase.name==input.name).\
            first()
        
        if existing_one:
            raise Exception('Definition [{}] already exists on this cluster'.format(input.name))

class Delete(AdminService):
    """ Deletes a guaranteed delivery definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_definition_delete_request'
        response_elem = 'zato_pattern_delivery_definition_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(DeliveryDefinitionBase).\
                    filter(DeliveryDefinitionBase.id==self.request.input.id).\
                    one()
                
                item_name = item.name
                
                session.delete(item)
                session.commit()
                
                self.delivery_store.set_deleted(item_name, True)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
