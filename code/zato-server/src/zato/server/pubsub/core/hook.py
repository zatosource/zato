# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, redefined-builtin, unused-variable

# stdlib
import logging

# gevent
from zato.common.api import PUBSUB
from zato.common.util.hook import HookTool
from zato.server.pubsub.model import HookCtx

# ################################################################################################################################
# ################################################################################################################################

hook_type_to_method = {
    PUBSUB.HOOK_TYPE.BEFORE_PUBLISH: 'before_publish',
    PUBSUB.HOOK_TYPE.BEFORE_DELIVERY: 'before_delivery',
    PUBSUB.HOOK_TYPE.ON_OUTGOING_SOAP_INVOKE: 'on_outgoing_soap_invoke',
    PUBSUB.HOOK_TYPE.ON_SUBSCRIBED: 'on_subscribed',
    PUBSUB.HOOK_TYPE.ON_UNSUBSCRIBED: 'on_unsubscribed',
}

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import RLock
    from zato.common.typing_ import callable_, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class HookAPI:
    def __init__(
        self,
        *,
        lock,               # type: RLock
        server,             # type: ParallelServer
        invoke_service_func # type: callable_
    ) -> 'None':

        self.lock = lock
        self.server = server
        self.invoke_service_func = invoke_service_func

        # Manages access to service hooks
        self.hook_tool = HookTool(self.server, HookCtx, hook_type_to_method, self.invoke_service_func)

# ################################################################################################################################

    def set_topic_config_hook_data(self, config:'stranydict') -> 'None':

        hook_service_id = config.get('hook_service_id')

        if hook_service_id:

            if not config['hook_service_name']:
                config['hook_service_name'] = self.server.service_store.get_service_name_by_id(hook_service_id)

            # Invoked when a new subscription to topic is created
            config['on_subscribed_service_invoker'] = self.hook_tool.get_hook_service_invoker(
                config['hook_service_name'], PUBSUB.HOOK_TYPE.ON_SUBSCRIBED)

            # Invoked when an existing subscription to topic is deleted
            config['on_unsubscribed_service_invoker'] = self.hook_tool.get_hook_service_invoker(
                config['hook_service_name'], PUBSUB.HOOK_TYPE.ON_UNSUBSCRIBED)

            # Invoked before messages are published
            config['before_publish_hook_service_invoker'] = self.hook_tool.get_hook_service_invoker(
                config['hook_service_name'], PUBSUB.HOOK_TYPE.BEFORE_PUBLISH)

            # Invoked before messages are delivered
            config['before_delivery_hook_service_invoker'] = self.hook_tool.get_hook_service_invoker(
                config['hook_service_name'], PUBSUB.HOOK_TYPE.BEFORE_DELIVERY)

            # Invoked for outgoing SOAP connections
            config['on_outgoing_soap_invoke_invoker'] = self.hook_tool.get_hook_service_invoker(
                config['hook_service_name'], PUBSUB.HOOK_TYPE.ON_OUTGOING_SOAP_INVOKE)
        else:
            config['hook_service_invoker'] = None

# ################################################################################################################################
# ################################################################################################################################
