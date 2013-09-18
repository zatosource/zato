# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from hashlib import sha1, sha256
from json import dumps, loads

# Zato
from zato.common import DATA_FORMAT, DELIVERY_STATE, INVOCATION_TARGET, KVDB
from zato.common.odb.model import DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ
from zato.common.odb.query import delivery_count_by_state, delivery_definition_list, \
     delivery_history_list
from zato.common.util import dotted_getattr, validate_input_dict
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService, AdminSIO

dispatch_dict = {
    INVOCATION_TARGET.OUTCONN_AMQP: 'outgoing.amqp.send',
    INVOCATION_TARGET.OUTCONN_WMQ: 'outgoing.jms_wmq.send',
    INVOCATION_TARGET.OUTCONN_ZMQ: 'outgoing.zmq.send',
    INVOCATION_TARGET.SERVICE: 'invoke'
}

target_def_class = {
    INVOCATION_TARGET.OUTCONN_WMQ: DeliveryDefinitionOutconnWMQ
}

class _Base(AdminService):
    def _validate_get_state(self, input):
        if input.state != DELIVERY_STATE.IN_PROGRESS_ANY:
            validate_input_dict(('state', input.state, DELIVERY_STATE))
            return [input.state]
        else:
            return [DELIVERY_STATE.IN_PROGRESS_STARTED, DELIVERY_STATE.IN_PROGRESS_TARGET_OK, DELIVERY_STATE.IN_PROGRESS_TARGET_FAILURE]

# ##############################################################################

class Dispatch(AdminService):
    """ Dispatches a guaranteed delivery to a concrete target.
    """
    class SimpleIO(AdminSIO):
        input_required = (AsIs('task_id'), 'payload', 'target', 'target_type', 'args', 'kwargs')

    def handle(self):
        invoke_func = dotted_getattr(self, dispatch_dict[self.request.input.target_type])
        invoke_func(
            self.request.input.payload,
            self.request.input.target,
            *loads(self.request.input.args),
            task_id=self.request.input.task_id,
            **loads(self.request.input.kwargs)
        )

# ##############################################################################

class UpdateDeliveryCounters(AdminService):
    """ Update counters of a delivery definition given on input.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_update_delivery_counters_request'
        response_elem = 'zato_pattern_delivery_update_delivery_counters_response'
        input_required = ('def_id', 'def_name')
        
    def handle(self):
        counters = {}
        with closing(self.odb.session()) as session:
            for state, count in delivery_count_by_state(session, self.request.input.def_id):
                counters[state] = count
                
        in_progress = 0 
        for name in (DELIVERY_STATE.IN_PROGRESS_STARTED, DELIVERY_STATE.IN_PROGRESS_TARGET_FAILURE, DELIVERY_STATE.IN_PROGRESS_TARGET_OK):
            in_progress += counters.get(name, 0)
            
        self.delivery_store.update_counters(
            self.request.input.def_name,
            in_progress,
            counters.get(DELIVERY_STATE.IN_DOUBT, 0),
            counters.get(DELIVERY_STATE.CONFIRMED, 0),
            counters.get(DELIVERY_STATE.FAILED, 0))
        
class UpdateCounters(AdminService):
    """ Asynchronously invokes a services to update counters for each delivery definition in the ODB.
    """
    def handle(self):
        with closing(self.odb.session()) as session:
            for d_def in delivery_definition_list(session, self.server.cluster_id):
                self.invoke_async(
                    UpdateDeliveryCounters.get_name(),
                    dumps({'def_id':d_def.id, 'def_name':d_def.name}),
                    data_format=DATA_FORMAT.JSON)

class GetCounters(AdminService):
    """ Returns usage counters for a given delivery definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_counters_request'
        response_elem = 'zato_pattern_delivery_get_counters_response'
        input_required = ('def_name',)
        output_required = ('total', 'in_progress', 'in_doubt', 'confirmed', 'failed')

    def handle(self):
        counters = self.delivery_store.get_counters(self.request.input.def_name)
        
        counters['in_progress'] = counters['in-progress']
        counters['in_doubt'] = counters['in-doubt']
        
        del counters['in-doubt']
        del counters['in-progress']
        
        self.response.payload = counters

# ##############################################################################

class GetBatchInfo(_Base):
    """ Returns pagination information for instances of a given delivery definition
    in a specified state and between from/to dates.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_batch_info_request'
        response_elem = 'zato_pattern_delivery_get_batch_info_response'
        input_required = ('def_name', 'state')
        input_optional = ('batch_size', 'current_batch', 'start', 'stop')
        output_required = ('total_results', 'num_batches', 'has_previous', 'has_next', 'next_batch_number', 'previous_batch_number')

    def handle(self):
        input = self.request.input
        state = self._validate_get_state(input)
        
        input['batch_size'] = input['batch_size'] or 25
        input['current_batch'] = input['current_batch'] or 1
        
        self.response.payload = self.delivery_store.get_batch_info(self.server.cluster_id, input, state)

# ##############################################################################

class Resubmit(AdminService):
    """ Resubmits a delivery task.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_resubmit_request'
        response_elem = 'zato_pattern_delivery_resubmit_response'
        input_required = (AsIs('task_id'),)
        input_optional = ('payload', 'args', 'kwargs')

    def handle(self):
        with closing(self.odb.session()) as session:
            delivery = session.merge(self.delivery_store.get_delivery(self.request.input.task_id))

            payload = loads(self.request.input.payload) if self.request.input.get('payload') else delivery.payload.payload
            args = self.request.input.args if self.request.input.get('args') else delivery.args
            kwargs = self.request.input.kwargs if self.request.input.get('kwargs') else delivery.kwargs

            kwargs = loads(kwargs)
            kwargs['is_resubmit'] = True

            self.deliver(delivery.definition.name, payload.encode('utf-8'), self.request.input.task_id, *loads(args), **kwargs)

# ##############################################################################

class GetHistoryList(AdminService):
    """ Returns a delivery's history log.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_history_list_request'
        response_elem = 'zato_pattern_delivery_get_history_list_response'
        input_required = (AsIs('task_id'),)
        output_required = ('entry_type', 'entry_time', 'entry_ctx', 'resubmit_count', 'delta')
        output_repeated = True
        
    def _get_delta(self, start, stop):
        delta = stop - start
        fract = round(float('0.{}'.format(delta.microseconds)), 2)
        delta = str(timedelta(days=delta.days, seconds=delta.seconds + fract))
        
        # 0:00:00
        if '.' not in delta:
            return delta + '.00'
        
        delta = delta.rstrip('0')
        split = delta.split('.')
        
        # 0:05:56.4
        if len(split[1]) == 1: 
            return delta + '0'
        
        # 0:41:48.14
        return delta

    def handle(self):
        with closing(self.odb.session()) as session:
            creation_time = session.merge(self.delivery_store.get_delivery(self.request.input.task_id)).creation_time
            
            history = list(delivery_history_list(session, self.request.input.task_id))
            columns = [elem.name for elem in history.pop()]
            for item in history:
                for elem in item:
                    elem = dict(zip(columns, elem))
                    elem['delta'] = self._get_delta(creation_time, elem['entry_time'])
                    elem['entry_time'] = elem['entry_time'].isoformat()
                    self.response.payload.append(elem)

# ##############################################################################

class GetDetails(AdminService):
    """ Returns details of a particular delivery definition that is in-doubt.
    """
    class SimpleIO(object):
        request_elem = 'zato_pattern_delivery_in_doubt_get_list_request'
        response_elem = 'zato_pattern_delivery_in_doubt_get_list_response'
        input_required = (AsIs('task_id'),)
        output_required = ('def_name', 'target_type', AsIs('task_id'), 'creation_time_utc', 'last_used_utc', 
            'source_count', 'target_count', 'resubmit_count', 'state', 'retry_repeats', 'check_after', 'retry_seconds')
        output_optional = ('payload', 'args', 'kwargs', 'target', 'payload_sha1', 'payload_sha256')
        output_repeated = True

    def handle(self):
        with closing(self.odb.session()) as session:
            instance = session.merge(self.delivery_store.get_delivery(self.request.input.task_id))
            self.response.payload = self.delivery_store.get_delivery_instance(self.request.input.task_id, instance.definition.__class__)
            if self.response.payload.payload:
                self.response.payload.payload_sha1 = sha1(self.response.payload.payload).hexdigest()
                self.response.payload.payload_sha256 = sha256(self.response.payload.payload).hexdigest()

# ##############################################################################

class GetList(_Base):
    """ Returns a batch of instances that are in the in-doubt state.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_in_doubt_get_list_request'
        response_elem = 'zato_pattern_delivery_in_doubt_get_list_response'
        input_required = ('def_name', 'state')
        input_optional = ('batch_size', 'current_batch', 'start', 'stop',)
        output_required = ('def_name', 'target_type', AsIs('task_id'), 'creation_time_utc', 'last_used_utc', 
            'source_count', 'target_count', 'resubmit_count', 'retry_repeats', 'check_after', 'retry_seconds')
        output_repeated = True

    def handle(self):
        input = self.request.input
        state = self._validate_get_state(input)
        input['batch_size'] = input['batch_size'] or 25
        input['current_batch'] = input['current_batch'] or 1
        
        self.response.payload[:] = self.delivery_store.get_delivery_instance_list(self.server.cluster_id, input, state)

# ##############################################################################
    
class Delete(AdminService):
    """ Deletes a delivery task.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_delete_request'
        response_elem = 'zato_pattern_delivery_delete_response'
        input_required = (AsIs('task_id'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            delivery = session.merge(self.delivery_store.get_delivery(self.request.input.task_id))
            session.delete(delivery)
            session.commit()
            
# ##############################################################################

class Edit(AdminService):
    """ Updates a delivery task.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_edit_request'
        response_elem = 'zato_pattern_delivery_edit_response'
        input_required = (AsIs('task_id'),)
        input_optional = ('payload', 'args', 'kwargs')

    def handle(self):
        self.delivery_store.update_delivery(self.request.input.task_id,
            self.request.input.get('payload', '').encode('utf-8'),
            self.request.input.get('args', '').encode('utf-8'),
            self.request.input.get('kwargs', '').encode('utf-8'))

# ##############################################################################

class AutoResubmit(AdminService):
    """ Dispatches as many async requests for auto-resubmitting delivery tasks
    as there are delivery definitions.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_edit_request'
        response_elem = 'zato_pattern_delivery_edit_response'
        input_required = ('def_id', 'def_name', Integer('retry_seconds'))
    
    def handle(self):
        now = datetime.utcnow()
        multiplier = int(self.server.fs_server_config.patterns.delivery_retry_threshold_multiplier)
        stop = now - timedelta(seconds=multiplier*self.request.input.retry_seconds)
        lock_name = '{}{}'.format(KVDB.LOCK_DELIVERY_AUTO_RESUBMIT, self.request.input.def_name)
        
        timeout = int(self.server.fs_server_config.patterns.delivery_auto_lock_timeout)
        with self.lock(lock_name, timeout):
            for item in self.delivery_store.get_delivery_list_for_auto_resubmit(self.server.cluster_id, self.request.input.def_name, stop):
                
                kwargs = loads(item['kwargs'])
                kwargs['is_resubmit'] = True
                kwargs['is_auto'] = True
                
                self.deliver(item['def_name'], item['payload'], item['task_id'], *loads(item['args']), **kwargs)
    
class DispatchAutoResubmit(AdminService):
    """ Dispatches as many async requests for auto-resubmitting delivery tasks
    as there are delivery definitions.
    """
    def handle(self):
        with closing(self.odb.session()) as session:
            for def_id, def_name, retry_seconds in session.query(
                DeliveryDefinitionBase.id, 
                DeliveryDefinitionBase.name,
                DeliveryDefinitionBase.retry_seconds,)\
                .all():
                self.invoke_async(
                    AutoResubmit.get_name(), 
                        {'def_id':def_id, 'def_name':def_name, 'retry_seconds':retry_seconds})

# ##############################################################################
