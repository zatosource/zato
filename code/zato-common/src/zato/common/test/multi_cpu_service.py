# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The service that the live suites of a server with several workers deploy through the pickup directory,
# which returns the slot and the process ID of the worker that served the request.

# stdlib
import os
from time import monotonic
from uuid import uuid4

# gevent
from gevent import sleep

# Zato
from zato.common.test.config_multi_cpu_cache import CacheConfig
from zato.common.worker_slot import get_slot_or_single
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class WorkerSlot(Service):
    """ Returns the slot and the process ID of the worker that serves the request.
    """
    name = 'test.multi-cpu.worker-slot'

    def handle(self) -> 'None':
        self.response.payload = {
            'slot': get_slot_or_single(),
            'pid': os.getpid(),
        }

# ################################################################################################################################
# ################################################################################################################################

class WorkerSleep(Service):
    """ Returns the slot and the process ID of the worker after a delay, which keeps the request in progress
    while a test signals the worker.
    """
    name = 'test.multi-cpu.worker-sleep'

    # How long the request stays in progress, in seconds
    Duration = 5.0

    def handle(self) -> 'None':
        sleep(self.Duration)

        self.response.payload = {
            'slot': get_slot_or_single(),
            'pid': os.getpid(),
        }

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publishes one message to a topic and returns the slot of the worker that published it.
    """
    name = 'test.multi-cpu.publish'

    def handle(self) -> 'None':
        request = self.request.payload
        result = self.pubsub.publish(request['topic_name'], request['data'])

        self.response.payload = {
            'slot': get_slot_or_single(),
            'msg_id': result.msg_id,
        }

# ################################################################################################################################
# ################################################################################################################################

class BlockingPull(Service):
    """ Waits for the messages of a subscription key in the worker that serves the request, which a publication
    through any other worker wakes, and returns how many arrived and how long the wait took.
    """
    name = 'test.multi-cpu.blocking-pull'

    def handle(self) -> 'None':
        request = self.request.payload
        started_at = monotonic()

        messages = self.server.pubsub_backend.fetch_messages(request['sub_key'], block_ms=request['block_ms'])

        self.response.payload = {
            'slot': get_slot_or_single(),
            'count': len(messages),
            'elapsed': monotonic() - started_at,
        }

# ################################################################################################################################
# ################################################################################################################################

class WorkerError(Service):
    """ Raises an exception whose message names the slot of the worker, so the error response of every worker can be compared.
    """
    name = 'test.multi-cpu.worker-error'

    def handle(self) -> 'None':
        slot = get_slot_or_single()
        raise Exception(f'Raised by the worker of slot {slot}')

# ################################################################################################################################
# ################################################################################################################################

class ChannelName(Service):
    """ Returns the name of the channel that the request arrived through and the slot of the worker that served it.
    """
    name = 'test.multi-cpu.channel-name'

    def handle(self) -> 'None':
        self.response.payload = {
            'channel': self.channel.name,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class OutgoingInvoke(Service):
    """ Sends a GET request through an outgoing REST connection and returns the JSON response together with
    the slot of the worker that sent it.
    """
    name = 'test.multi-cpu.outgoing-invoke'

    def handle(self) -> 'None':
        request = self.request.payload
        connection = self.out.rest[request['outconn_name']].conn

        response = connection.get(self.cid)

        self.response.payload = {
            'response': response.json(),
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class CachedSlow(Service):
    """ Records each invocation in the file shared by every worker, then returns an ID of the invocation after a delay,
    so that the responses that a cache served can be told apart from the ones that an invocation produced.
    """
    name = CacheConfig.Cached_Service

    def handle(self) -> 'None':
        key = self.request.http.GET['key']
        invocation_id = uuid4().hex

        with open(os.environ[CacheConfig.Invocation_Log_Env], 'a') as invocation_log:
            _ = invocation_log.write(f'{key} {invocation_id}\n')

        sleep(CacheConfig.Service_Duration)

        self.response.payload = {
            'invocation_id': invocation_id,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class InvalidateResponse(Service):
    """ Invalidates the cached responses of a channel.
    """
    name = CacheConfig.Invalidate_Service

    def handle(self) -> 'None':
        self._config_manager.cache_api.invalidate_response(self.request.payload['channel_name'])

# ################################################################################################################################
# ################################################################################################################################
