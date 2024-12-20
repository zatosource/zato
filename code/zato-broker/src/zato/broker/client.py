# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# orjson
from orjson import dumps

# Requests
from requests import post as requests_post

# Zato
from zato.common.broker_message import code_to_name, SCHEDULER
from zato.common.api import URLInfo
from zato.common.util.config import get_url_protocol_from_config_item
from zato.common.util.platform_ import is_non_windows

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests.models import Response
    from zato.client import AnyServiceInvoker
    from zato.common.typing_ import any_, anydict, strdict, strdictnone
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
    SCHEDULER.SET_SERVER_ADDRESS.value,
}

from_scheduler_actions = {
    SCHEDULER.JOB_EXECUTED.value,
    SCHEDULER.DELETE.value,
    SCHEDULER.DELETE_PUBSUB_SUBSCRIBER.value,
}

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:
    """ Simulates previous Redis-based RPC.
    """
    def __init__(
        self,
        *,
        scheduler_config: 'strdictnone'              = None,
        server_rpc:       'ServerRPC | None'         = None,
        zato_client:      'AnyServiceInvoker | None' = None,
        ) -> 'None':

        # This is used to invoke services
        self.server_rpc = server_rpc

        self.zato_client = zato_client
        self.scheduler_address = ''
        self.scheduler_auth = None

        # We are a server so we will have configuration needed to set up the scheduler's details ..
        if scheduler_config:
            self.set_scheduler_config(scheduler_config)

        # .. otherwise, we are a scheduler so we have a client to invoke servers with.
        else:
            self.zato_client = zato_client

# ################################################################################################################################

    def set_scheduler_config(self, scheduler_config:'strdict') -> 'None':

        # Branch-local variables
        scheduler_host = scheduler_config['scheduler_host']
        scheduler_port = scheduler_config['scheduler_port']

        if not (scheduler_api_username := scheduler_config.get('scheduler_api_username')):
            scheduler_api_username = 'scheduler_api_username_missing'

        if not (scheduler_api_password := scheduler_config.get('scheduler_api_password')):
            scheduler_api_password = 'scheduler_api_password_missing'

        # Make sure both parts are string objects
        scheduler_api_username = str(scheduler_api_username)
        scheduler_api_password = str(scheduler_api_password)

        self.scheduler_auth = (scheduler_api_username, scheduler_api_password)

        # Introduced after 3.2 was released, hence optional
        scheduler_use_tls = scheduler_config.get('scheduler_use_tls', False)

        # Decide whether to use HTTPS or HTTP
        api_protocol = get_url_protocol_from_config_item(scheduler_use_tls)

        # Set a full URL for later use
        scheduler_address = f'{api_protocol}://{scheduler_host}:{scheduler_port}'
        self.set_scheduler_address(scheduler_address)

# ################################################################################################################################

    def set_zato_client_address(self, url:'URLInfo') -> 'None':
        self.zato_client.set_address(url)

# ################################################################################################################################

    def set_scheduler_address(self, scheduler_address:'str') -> 'None':
        self.scheduler_address = scheduler_address

# ################################################################################################################################

    def run(self) -> 'None':
        raise NotImplementedError()

# ################################################################################################################################

    def _invoke_scheduler_from_server(self, msg:'anydict') -> 'any_':

        idx = 0
        response = None
        msg_bytes = dumps(msg)

        while not response:

            # Increase the loop counter
            idx += 1

            try:
                response = requests_post(
                    self.scheduler_address,
                    msg_bytes,
                    auth=self.scheduler_auth,
                    verify=False,
                    timeout=5,
                )
            except Exception as e:

                # .. log what happened ..
                logger.warn('Scheduler invocation error -> %s (%s)', e, self.scheduler_address)

            # .. keep retrying or return the response ..
            finally:

                # .. we can return the response if we have it ..
                if response:
                    return response

                # .. otherwise, wait until the scheduler responds ..
                else:

                    # .. The first time around, wait a little longer ..
                    # .. because the scheduler may be only starting now ..
                    if idx == 1:
                        logger.info('Waiting for the scheduler to respond (1)')
                        sleep(5)

                    # .. log what is happening ..
                    logger.info('Waiting for the scheduler to respond (2)')

                    # .. wait for a moment ..
                    sleep(3)

# ################################################################################################################################

    def _invoke_server_from_scheduler(self, msg:'anydict') -> 'any_':
        if self.zato_client:
            response = self.zato_client.invoke_async(msg.get('service'), msg['payload'])
            return response
        else:
            logger.warning('Scheduler -> server invocation failure; self.zato_client is not configured (%r)', self.zato_client)

# ################################################################################################################################

    def _rpc_invoke(self, msg:'anydict', from_scheduler:'bool'=False) -> 'any_':

        # Local aliases ..
        from_server = not from_scheduler
        action = msg['action']

        try:

            # Special-case messages that are actually destined to the scheduler, not to servers ..
            if from_server and action in to_scheduler_actions:
                try:
                    response = self._invoke_scheduler_from_server(msg)
                    return response
                except Exception as e:
                    logger.warning('Invocation error; server -> scheduler -> %s (%d:%r)', e, from_server, action)
                return

            # .. special-case messages from the scheduler to servers ..
            elif from_scheduler and action in from_scheduler_actions:
                try:
                    response = self._invoke_server_from_scheduler(msg)
                    return response
                except Exception as e:
                    logger.warning('Invocation error; scheduler -> server -> %s (%d:%r)', e, from_server, action)
                return

            # .. otherwise, we invoke servers.
            code_name = code_to_name[action]
            if has_debug:
                logger.info('Invoking %s %s', code_name, msg)

            if self.server_rpc:
                return self.server_rpc.invoke_all('zato.service.rpc-service-invoker', msg, ping_timeout=10)
            else:
                logger.warning('Server-to-server RPC invocation failure -> self.server_rpc is not configured (%r) (%d:%r)',
                    self.server_rpc, from_server, action)

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def publish(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        spawn(self._rpc_invoke, msg, **kwargs)

# ################################################################################################################################

    def invoke_async(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        spawn(self._rpc_invoke, msg, **kwargs)

# ################################################################################################################################

    def invoke_sync(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        response:'Response' = self._rpc_invoke(msg, **kwargs)
        if response.text:
            out = loads(response.text)
            return out
        else:
            return response.text

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
