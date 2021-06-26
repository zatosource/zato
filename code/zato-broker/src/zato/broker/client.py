# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import time
from json import dumps, loads
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep, spawn

# orjson
from orjson import dumps

# Requests
from requests import post as requests_post

# Zato
from zato.common.broker_message import code_to_name, SCHEDULER

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.client import AnyServiceInvoker
    from zato.server.connection.server.rpc.api import ServerRPC

    AnyServiceInvoker = AnyServiceInvoker
    ServerRPC = ServerRPC

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)
has_debug = True

# ################################################################################################################################
# ################################################################################################################################

to_scheduler_actions = set([
    SCHEDULER.CREATE.value,
    SCHEDULER.EDIT.value,
    SCHEDULER.DELETE.value,
    SCHEDULER.EXECUTE.value,
])

from_scheduler_actions = set([
    SCHEDULER.JOB_EXECUTED.value,
    SCHEDULER.SET_JOB_INACTIVE,
])

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient(object):
    """ Simulates previous Redis-based RPC.
    """
    def __init__(self, server_rpc=None, scheduler_config=None, zato_client=None):
        # type: (ServerRPC, Bunch) -> None

        # This is used to invoke services
        self.server_rpc = server_rpc

        self.zato_client = None # type: AnyServiceInvoker
        self.scheduler_url = ''

        # We are a server so we will have configuration needed to set up the scheduler's details ..
        if scheduler_config:
            self.scheduler_url = 'https://{}:{}/'.format(
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

    def _invoke_scheduler_from_server(self, msg):
        msg = dumps(msg)
        requests_post(self.scheduler_url, msg, verify=False)

# ################################################################################################################################

    def _invoke_server_from_scheduler(self, msg):
        self.zato_client.invoke_async(msg['service'], msg['payload'])

# ################################################################################################################################

    def _rpc_invoke(self, msg):

        # Local aliases ..
        action = msg['action']

        try:

            # Special cases messages that are actually destined to the scheduler, not to servers ..
            if action in to_scheduler_actions:
                self._invoke_scheduler_from_server(msg)
                return

            # .. special-case messages from the scheduler to servers ..
            elif action in from_scheduler_actions:
                self._invoke_server_from_scheduler(msg)
                return

            # .. otherwise, we invoke servers.
            code_name = code_to_name[action]
            if has_debug:
                logger.info('Invoking %s %s', code_name, msg)

            self.server_rpc.invoke_all('zato.service.rpc-service-invoker', msg, ping_timeout=10)

        except Exception:
            logger.warn(format_exc())

# ################################################################################################################################

    def publish(self, msg, *ignored_args, **ignored_kwargs):
        # type: (dict, str, object, object) -> None
        spawn(self._rpc_invoke, msg)

# ################################################################################################################################

    def invoke_async(self, msg, *ignored_args, **ignored_kwargs):
        # type: (dict, object, object) -> None
        spawn(self._rpc_invoke, msg)

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
