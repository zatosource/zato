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

# Zato
from zato.common import DEFAULT_DELIVERY_INSTANCE_LIST_BATCH_SIZE, DELIVERY_STATE, INVOCATION_TARGET, KVDB, ZatoException
from zato.common.odb.model import DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ, OutgoingWMQ, to_json
from zato.common.odb.query import delivery_definition_list, out_jms_wmq, out_jms_wmq_by_name
from zato.common.util import datetime_to_seconds, validate_input_dict
from zato.server.service import AsIs, Boolean, CSV, Integer, UTC
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.internal.pattern.delivery import target_def_class

_target_query_by_id = {
    INVOCATION_TARGET.OUTCONN_WMQ: out_jms_wmq
}

_target_query_by_name = {
    INVOCATION_TARGET.OUTCONN_WMQ: out_jms_wmq_by_name
}

# ##############################################################################

class _DeliveryService(AdminService):
    """ Base class with code common to multiple guaranteed delivery-related services.
    """
    _is_edit = None
            
    def _validate_times(self):
        """ Checks whether times specified constitute at least one second.
        """
        for name in ('expire_after', 'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after',
                'retry_repeats', 'retry_seconds'):
            value = int(self.request.input[name])
            if value < 1:
                msg = '[{}] should be at least 1 instead of [{}]'.format(name, self.request.input[name])
                self.logger.warn(msg)
                raise ValueError(msg)
            
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
        
# ##############################################################################
    
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
            'in_progress_count', 'in_doubt_count', 'confirmed_count', 'failed_count')
        output_optional = (UTC('last_updated_utc'), UTC('last_used_utc'), 'callback_list')

    def get_data(self, session, cluster_id, target_type):
        for item in delivery_definition_list(session, cluster_id, target_type):
            
            target_query = _target_query_by_id[target_type]
            target = target_query(session, cluster_id, item.target_id)
           
            out = {
                'target': target.name,
                'target_type': target_type
            }
            
            for name in ('id', 'name', 'expire_after', 'expire_arch_succ_after', 
                  'expire_arch_fail_after', 'check_after', 'retry_repeats', 'retry_seconds', 'short_def',
                  'callback_list', 'last_used_utc'):
                out[name] = getattr(item, name, None)
                
            last_used = getattr(item, 'last_used', None)
            if last_used:
                out['last_used_utc'] = last_used.isoformat()
            
            basic_data = self.delivery_store.get_target_basic_data(item.name)
            for name in ('last_updated_utc', 'total_count', 'in_progress_count', 
                             'in_doubt_count', 'confirmed_count', 'failed_count'):
                out[name] = basic_data.get(name)
            
            yield out

    def handle(self):
        target_type = self.request.input.target_type
        validate_input_dict(('target_type', target_type, INVOCATION_TARGET))
        
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session, self.request.input.cluster_id, target_type)

# ##############################################################################

class _CreateEdit(_DeliveryService):
    """ A common class for both Create and Edit actions.
    """
    _error_msg = None
    
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'target', 'target_type', 'expire_after', 
            'expire_arch_succ_after', 'expire_arch_fail_after', 'check_after', 
            'retry_repeats', 'retry_seconds',)
        input_optional = ('callback_list',)
        output_required = ('id', 'name')
        
    def _get_item(self, session, target_def_class, input):
        raise NotImplementedError('Should be defined by subclasses')
        
    def handle(self):
        with closing(self.odb.session()) as session:
            
            target_type = self.request.input.target_type
            validate_input_dict(('target_type', target_type, INVOCATION_TARGET))
            self._validate_times()
        
            input = self.request.input
            
            if not self._is_edit:
                self._check_def_name(session, input)
            
            target_query = _target_query_by_name[target_type]
            target = target_query(session, input.cluster_id, input.target)
            if not target:
                raise Exception('Target [{}] ({}) does not exist on this cluster'.format(
                    input.target, input.target_type))
                
            try:
                item = self._get_item(session, target_def_class[target_type], input)
                        
                item.target_id = target.id
                item.short_def = '{}-{}-{}'.format(input.check_after, input.retry_repeats, input.retry_seconds)
            
                if not self._is_edit:
                    item.name = input.name
                    
                item.target_type = input.target_type
                item.expire_after = input.expire_after
                item.expire_arch_succ_after = input.expire_arch_succ_after
                item.expire_arch_fail_after = input.expire_arch_fail_after
                item.check_after = input.check_after
                item.retry_repeats = input.retry_repeats
                item.retry_seconds = input.retry_seconds
                item.cluster_id = input.cluster_id
                item.callback_list = input.callback_list.encode('utf-8')
                
                session.add(item)
                session.commit()
                
                self.delivery_store.set_deleted(item.name, False)

                if self._is_edit:
                    self.delivery_store.set_deleted(item.name, True)
                
                self.response.payload.id = item.id
                self.response.payload.name = item.name
                
            except Exception, e:
                msg = self._error_msg.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise 

# ##############################################################################

class Create(_CreateEdit):
    """ Creates a new delivery definition.
    """
    _is_edit = False
    _error_msg = 'Could not create the definition, e:[{}]'
    
    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_pattern_delivery_definition_create_request'
        response_elem = 'zato_pattern_delivery_definition_create_response'
        input_required = ('name',) + _CreateEdit.SimpleIO.input_required
        
    def _get_item(self, _ignored1, target_def_class, _ignored2):
        return target_def_class()

# ##############################################################################

class Edit(_CreateEdit):
    """ Updates an existing delivery definition.
    """
    _is_edit = True
    _error_msg = 'Could not update the definition, e:[{}]'
    
    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_pattern_delivery_definition_edit_request'
        response_elem = 'zato_pattern_delivery_definition_edit_response'
        input_required = ('id',) + _CreateEdit.SimpleIO.input_required
        
    def _get_item(self, session, target_def_class, input):
        return session.query(target_def_class).\
            filter(target_def_class.id==input.id).\
            one()

# ##############################################################################

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

# ##############################################################################
