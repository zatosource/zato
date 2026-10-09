# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The service of the Dashboard's Invoke dialog for an outgoing SMS connection - sends one message to one number
# through the connection.

# stdlib
from time import monotonic

# Zato
from zato.common.api import SMS
from zato.common.exception import NotFound
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.generic.api.outconn_sms import OutconnSMSWrapper

# ################################################################################################################################
# ################################################################################################################################

# How many decimal places the response time is rounded to
_response_time_precision = 3

# ################################################################################################################################
# ################################################################################################################################

class Invoke(AdminService):
    """ Sends one message through an outgoing SMS connection, identified by its ID, and returns the provider's answer.
    """
    name = SMS.Invoke_Service

    input = Int('id'), 'to', 'body', '-from_'
    output = AsIs('-id'), '-status', AsIs('-raw'), '-response_time_ms'
    response_elem = None

    def handle(self) -> 'None':

        input = self.request.input
        wrapper = self._get_wrapper(input.id)

        from_ = input.from_
        if not from_:
            from_ = wrapper.config[SMS.Field_Sender]

        start = monotonic()
        result = wrapper.send(input.to, input.body, from_=from_, cid=self.cid)
        response_time_ms = round((monotonic() - start) * 1000, _response_time_precision)

        # A send through the connection's queue returns the queue's result, not the provider's
        if hasattr(result, 'to_dict'):
            payload = result.to_dict()
        else:
            payload = {'id': '', 'status': '', 'raw': result}

        self.response.payload.id = payload['id']
        self.response.payload.status = payload['status']
        self.response.payload.raw = payload['raw']
        self.response.payload.response_time_ms = response_time_ms

# ################################################################################################################################

    def _get_wrapper(self, conn_id:'int') -> 'OutconnSMSWrapper':
        """ The wrapper of the outgoing SMS connection with that ID.
        """
        for item in self.server.config_manager.outconn_sms.values():
            if item['id'] == conn_id:
                return item.conn

        raise NotFound(self.cid, f'No such outgoing SMS connection, id:`{conn_id}`')

# ################################################################################################################################
# ################################################################################################################################
