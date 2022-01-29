# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent import spawn

# orjson
from orjson import dumps

# Requests
from requests import post as requests_post

# Zato
from zato.common.broker_message import code_to_name, SCHEDULER
from zato.common.util.platform_ import is_non_windows

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.client import AnyServiceInvoker
    from zato.common.typing_ import any_, anydict, optional
    from zato.server.connection.server.rpc.api import ServerRPC

    AnyServiceInvoker = AnyServiceInvoker
    ServerRPC = ServerRPC

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
has_debug = False

use_tls = is_non_windows

# ################################################################################################################################
# ################################################################################################################################

to_scheduler_actions = {
    SCHEDULER.CREATE.value,
    SCHEDULER.EDIT.value,
    SCHEDULER.DELETE.value,
    SCHEDULER.EXECUTE.value,
}

from_scheduler_actions = {
    SCHEDULER.JOB_EXECUTED.value,
    SCHEDULER.DELETE.value,
}

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:
    """ Simulates previous Redis-based RPC.
    """
    def __init__(
        self,
        *,
        server_rpc:  'optional[ServerRPC]',
        zato_client: 'optional[AnyServiceInvoker]',
        scheduler_config: 'optional[Bunch]',
        ) -> 'None':

        # This is used to invoke services
        self.server_rpc = server_rpc

        self.zato_client = zato_client
        self.scheduler_url = ''

        # We are a server so we will have configuration needed to set up the scheduler's details ..
        if scheduler_config:

            # Introduced after 3.2 was released, hence optional
            scheduler_use_tls = scheduler_config.get('scheduler_use_tls', True)

            self.scheduler_url = 'http{}://{}:{}/'.format(
                's' if scheduler_use_tls else '',
                scheduler_config.scheduler_host,
                scheduler_config.scheduler_port,
            )

        # .. otherwise, we are a scheduler so we have a client to invoke servers with.
        else:
            self.zato_client = zato_client

# ################################################################################################################################

    def run(self):
        # type: () -> None
        raise NotImplementedError()

# ################################################################################################################################

    def _invoke_scheduler_from_server(self, msg:'anydict') -> 'None':
        msg_bytes = dumps(msg)
        requests_post(self.scheduler_url, msg_bytes, verify=False)

# ################################################################################################################################

    def _invoke_server_from_scheduler(self, msg:'anydict') -> 'None':
        if self.zato_client:
            self.zato_client.invoke_async(msg.get('service'), msg['payload'])
        else:
            logger.warn('Scheduler -> server invocation failure -> self.zato_client is not configured (%r)', self.zato_client)

# ################################################################################################################################

    def _rpc_invoke(self, msg:'Bunch', from_scheduler:'bool'=False) -> 'None':

        # Local aliases ..
        from_server = not from_scheduler
        action = msg['action']

        try:

            # Special cases messages that are actually destined to the scheduler, not to servers ..
            if from_server and action in to_scheduler_actions:
                try:
                    self._invoke_scheduler_from_server(msg)
                except Exception as e:
                    logger.warn('Invocation error; server -> scheduler -> %s', e)
                return

            # .. special-case messages from the scheduler to servers ..
            elif from_scheduler and action in from_scheduler_actions:
                try:
                    self._invoke_server_from_scheduler(msg)
                except Exception as e:
                    logger.warn('Invocation error; scheduler -> server -> %s', e)
                return

            # .. otherwise, we invoke servers.
            code_name = code_to_name[action]
            if has_debug:
                logger.info('Invoking %s %s', code_name, msg)

            if self.server_rpc:
                self.server_rpc.invoke_all('zato.service.rpc-service-invoker', msg, ping_timeout=10)
            else:
                logger.warn('RPC invocation failure -> self.server_rpc is not configured (%r)', self.server_rpc)

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def publish(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'None':
        spawn(self._rpc_invoke, msg, **kwargs)

# ################################################################################################################################

    def invoke_async(self, msg, *ignored_args, **kwargs):
        # type: (dict, object, object) -> None
        spawn(self._rpc_invoke, msg, **kwargs)

# ################################################################################################################################

    def on_message(self, msg):
        # type: (object) -> None
        raise NotImplementedError()

# ################################################################################################################################

    def close(self):
        # type: () -> None
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################
