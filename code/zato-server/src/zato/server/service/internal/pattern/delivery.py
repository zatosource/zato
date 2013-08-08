# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import INVOCATION_TARGET, ZatoException
from zato.server.service.internal import AdminService, AdminSIO

class GetList(AdminService):
    """ Returns a list of existing deliveries regardless of their states.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pattern_delivery_get_list_request'
        response_elem = 'zato_pattern_delivery_get_list_response'
        input_required = ('cluster_id', 'target_type')
        output_required = ('name', 'target', 'short_def', 'total_count', 
            'in_progress_count', 'in_doubt_count', 'arch_success_count', 'arch_failed_count')
        
    def get_data(self):
        return [{'z':'a'}]

    def handle(self):
        if not INVOCATION_TARGET.has(self.request.input.target_type):
            msg = 'Invalid target_type:[{}]'.format(self.request.input.target_type)
            log_msg = '{} (attrs: {})'.format(msg, INVOCATION_TARGET.attrs)
            
            self.logger.warn(log_msg)
            raise ZatoException(self.cid,msg)
            
        self.response.payload[:] = self.get_data()