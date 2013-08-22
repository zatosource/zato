# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps, loads

# Zato
from zato.server.service import AsIs
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a batch of instances that are in the in-doubt state.
    """
    class SimpleIO(object):
        request_elem = 'zato_pattern_delivery_in_doubt_get_list_request'
        response_elem = 'zato_pattern_delivery_in_doubt_get_list_response'
        input_required = ('def_name',)
        input_optional = ('batch_size', 'current_batch', 'start', 'stop')
        output_required = ('def_name', 'target_type', AsIs('task_id'), 'creation_time_utc', 'in_doubt_created_at_utc', 
            'source_count', 'target_count', 'retry_repeats', 'check_after', 'retry_seconds')
        output_repeated = True

    def handle(self):
        input = self.request.input
        input['batch_size'] = input['batch_size'] or 100
        input['current_batch'] = input['current_batch'] or 1
        
        self.response.payload[:] = self.delivery_store.get_in_doubt_instance_list(self.server.cluster_id, input)
