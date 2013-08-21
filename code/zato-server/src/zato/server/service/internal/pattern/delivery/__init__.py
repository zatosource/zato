# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common import INVOCATION_TARGET
from zato.common.util import dotted_getattr
from zato.server.service import AsIs
from zato.server.service.internal import AdminService

dispatch_dict = {
    INVOCATION_TARGET.OUTCONN_AMQP: 'outgoing.amqp.send',
    INVOCATION_TARGET.OUTCONN_WMQ: 'outgoing.jms_wmq.send',
    INVOCATION_TARGET.OUTCONN_ZMQ: 'outgoing.zmq.send',
    INVOCATION_TARGET.SERVICE: 'invoke'
}

class Dispatch(AdminService):
    """ Dispatches a guaranteed delivery to a concrete target.
    """
    class SimpleIO(object):
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

class Confirm(AdminService):
    """ Confirms a guaranteed delivery by its task_id.
    """
    class SimpleIO(object):
        input_required = (AsIs('task_id'), 'target', 'target_type')

    def handle(self):
        self.logger.error(self.request.input)
