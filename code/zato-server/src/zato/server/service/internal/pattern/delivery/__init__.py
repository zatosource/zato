# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps, loads

# Zato
from zato.common import DATA_FORMAT, DELIVERY_STATE, INVOCATION_TARGET
from zato.common.odb.query import delivery_count_by_state, delivery_definition_list
from zato.common.util import dotted_getattr
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO

dispatch_dict = {
    INVOCATION_TARGET.OUTCONN_AMQP: 'outgoing.amqp.send',
    INVOCATION_TARGET.OUTCONN_WMQ: 'outgoing.jms_wmq.send',
    INVOCATION_TARGET.OUTCONN_ZMQ: 'outgoing.zmq.send',
    INVOCATION_TARGET.SERVICE: 'invoke'
}

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

class GetBatchInfo(AdminService):
    """ Returns pagination information for instances of a given delivery definition
    in a specified state and between from/to dates.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_batch_info_request'
        response_elem = 'zato_pattern_delivery_get_batch_info_response'
        input_required = ('def_name',)
        input_optional = ('batch_size', 'current_batch', 'start', 'stop')
        output_required = ('total_results', 'num_batches', 'has_previous', 'has_next', 'next_batch_number', 'previous_batch_number')

    def handle(self):
        input = self.request.input
        input['batch_size'] = input['batch_size'] or 25
        input['current_batch'] = input['current_batch'] or 1
        
        self.response.payload = self.delivery_store.get_batch_info(self.server.cluster_id, input)

# ##############################################################################

class Resubmit(AdminService):
    """ Resubmits a delivery task.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_resubmit_request'
        response_elem = 'zato_pattern_delivery_resubmit_response'
        input_required = (AsIs('task_id'),)

    def handle(self):
        with closing(self.odb.session()) as session:
            delivery = session.merge(self.delivery_store.get_delivery(self.request.input.task_id))
            kwargs = loads(delivery.kwargs)
            kwargs['is_resubmit'] = True
            self.deliver(delivery.definition.name, delivery.payload.payload, delivery.task_id, *loads(delivery.args), **kwargs)
