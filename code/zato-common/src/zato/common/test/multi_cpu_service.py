# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services that the live suites of a server with several workers deploy through the pickup directory,
# each of which reports the slot of the worker that ran it.

# stdlib
import json
import logging
import os
import tempfile
from time import monotonic, monotonic_ns, time
from uuid import uuid4

# gevent
from gevent import sleep

# Zato
from zato.common.hl7.mllp.circuit_breaker import SendingStopped
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.test.config_multi_cpu_cache import CacheConfig
from zato.common.test.config_multi_cpu_hl7 import HL7Config
from zato.common.test.config_multi_cpu_scheduler import SchedulerConfig
from zato.common.worker_slot import get_slot_or_single
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

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

class PublishWithID(Service):
    """ Publishes one message under the message ID and with the priority that the caller gives, and returns the slot
    of the worker that published it, the message ID that the publication returned and the name of the exception
    that the publication raised, if any.
    """
    name = 'test.multi-cpu.publish-with-id'

    def handle(self) -> 'None':
        request = self.request.payload

        msg_id = ''
        error = ''

        try:
            result = self.pubsub.publish(request['topic_name'], request['data'], msg_id=request['msg_id'],
                priority=request['priority'])
        except Exception as e:
            error = type(e).__name__
        else:
            msg_id = result.msg_id

        self.response.payload = {
            'slot': get_slot_or_single(),
            'msg_id': msg_id,
            'error': error,
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
    """ Records each invocation with its start time in the file shared by every worker, then returns an ID
    of the invocation after a delay, so that the responses that a cache served can be told apart
    from the ones that an invocation produced.
    """
    name = CacheConfig.Cached_Service

    def handle(self) -> 'None':
        key = self.request.http.GET['key']
        invocation_id = uuid4().hex

        with open(os.environ[CacheConfig.Invocation_Log_Env], 'a') as invocation_log:
            _ = invocation_log.write(f'{key} {invocation_id} {time()}\n')

        sleep(CacheConfig.Service_Duration)

        self.response.payload = {
            'invocation_id': invocation_id,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class RecordFire(Service):
    """ Records the start and the end of each run of a scheduled job, with its nominal fire time, its run number
    and the slot of the worker, in the file shared by every worker, and runs for as long as the job requests.
    """
    name = SchedulerConfig.Record_Service

    def _append(self, entry:'anydict') -> 'None':
        with open(os.environ[SchedulerConfig.Fire_Log_Env], 'a') as fire_log:
            _ = fire_log.write(json.dumps(entry) + '\n')

    def handle(self) -> 'None':
        payload = self.request.payload
        zato_ctx = self.request_ctx[SchedulerConfig.Zato_Ctx_Key]

        entry = {
            'job': payload['job'],
            'nominal': zato_ctx['scheduler_nominal_fire_time'],
            'run': zato_ctx['scheduler_current_run'],
            'slot': get_slot_or_single(),
            'phase': SchedulerConfig.Phase_Start,
            'time': time(),
        }

        # The run is recorded as begun before it does its work ..
        self._append(entry)

        sleep(payload['run_seconds'])

        # .. and as completed once the work is done.
        entry['phase'] = SchedulerConfig.Phase_End
        entry['time'] = time()
        self._append(entry)

# ################################################################################################################################
# ################################################################################################################################

class LogRecords(Service):
    """ Writes the requested number of records to the server log, each with a marker of its own,
    so that a test finds every record that the worker wrote among the log files after their rotation.
    """
    name = 'test.multi-cpu.log-records'

    def handle(self) -> 'None':
        request = self.request.payload
        padding = 'x' * request['padding']

        for index in range(request['count']):
            self.logger.info('%s-%06d %s', request['prefix'], index, padding)

        self.response.payload = {'slot': get_slot_or_single()}

# ################################################################################################################################
# ################################################################################################################################

class EnvChange(Service):
    """ Sets an environment variable through zato.env-variables.save and returns the value that the worker
    reads once the invocation returned, together with the slot of the worker.
    """
    name = 'test.multi-cpu.env-change'

    def handle(self) -> 'None':
        request = self.request.payload
        variable = request['name']

        _ = self.invoke('zato.env-variables.save', {'variables': f'{variable}={request["value"]}'})

        self.response.payload = {
            'value': os.environ[variable],
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class EnvRead(Service):
    """ Returns the value of an environment variable in the worker that serves the request, or None if it is not set.
    """
    name = 'test.multi-cpu.env-read'

    def handle(self) -> 'None':
        variable = self.request.payload['name']

        if variable in os.environ:
            value = os.environ[variable]
        else:
            value = None

        self.response.payload = {
            'value': value,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class Constant(Service):
    """ Returns the same response from every worker, so that the responses of the workers can be compared in full.
    """
    name = 'test.multi-cpu.constant'

    def handle(self) -> 'None':
        self.response.payload = {
            'value': 'multi-cpu',
        }

# ################################################################################################################################
# ################################################################################################################################

class LogLevel(Service):
    """ Returns the name of the level of a logger in the worker that serves the request.
    """
    name = 'test.multi-cpu.log-level'

    def handle(self) -> 'None':
        level = logging.getLogger(self.request.payload['name']).level

        self.response.payload = {
            'level': logging.getLevelName(level),
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class RedisDB(Service):
    """ Returns the database number of the Redis configuration in the worker that serves the request.
    """
    name = 'test.multi-cpu.redis-db'

    def handle(self) -> 'None':
        self.response.payload = {
            'db': self.server.fs_server_config.redis.db,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class OutconnInvoke(Service):
    """ Invokes an outgoing REST connection with a marker in its query string, by which the endpoint's record
    of the request is found, and returns the slot of the worker that invoked it.
    """
    name = 'test.multi-cpu.outconn-invoke'

    def handle(self) -> 'None':
        request = self.request.payload
        _ = self.rest[request['conn_name']].get(params={'marker': request['marker']})

        self.response.payload = {
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class OutconnPublish(Service):
    """ Publishes a message to the queue of an outgoing REST connection and returns the slot of the worker that published it.
    """
    name = 'test.multi-cpu.outconn-publish'

    def handle(self) -> 'None':
        request = self.request.payload
        _ = self.rest[request['conn_name']].publish(request['data'])

        self.response.payload = {
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class HL7Record(Service):
    """ Records each message that an MLLP channel delivers as one file in the directory of its control ID,
    named after the slot of the worker that ran the service, and returns nothing, so the channel acknowledges with AA.
    """
    name = HL7Config.Record_Service

    def handle(self) -> 'None':
        msh_line = self.request.raw_request.splitlines()[0]
        control_id = extract_control_id(msh_line)

        directory = os.path.join(tempfile.gettempdir(), HL7Config.Record_Directory, control_id)
        os.makedirs(directory, exist_ok=True)

        path = os.path.join(directory, f'{get_slot_or_single()}-{uuid4().hex}')

        with open(path, 'w') as file_handle:
            _ = file_handle.write(msh_line)

# ################################################################################################################################
# ################################################################################################################################

class MLLPSend(Service):
    """ Sends a message through an outgoing MLLP connection and returns the outcome and the slot that sent it.
    """
    name = HL7Config.Send_Service

    def handle(self) -> 'None':
        request = self.request.payload
        connection = self.mllp[request['conn_name']]

        try:
            _ = connection.send(request['message'])
        except SendingStopped:
            outcome = HL7Config.Outcome_Stopped
        except Exception:
            outcome = HL7Config.Outcome_Failed
        else:
            outcome = HL7Config.Outcome_Sent

        self.response.payload = {
            'outcome': outcome,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class MLLPConnectionExists(Service):
    """ Returns the slot of the worker that ran it if that worker has the outgoing MLLP connection, sending nothing.
    """
    name = HL7Config.Exists_Service

    def handle(self) -> 'None':
        _ = self.mllp[self.request.payload['conn_name']]

        self.response.payload = {
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class LogStreamingHandler(Service):
    """ Returns whether the worker that ran it streams its log records, according to its own handlers,
    and the slot of that worker.
    """
    name = 'test.multi-cpu.log-streaming-handler'

    def handle(self) -> 'None':
        manager = self.server.log_streaming_manager
        redis_handler = manager.redis_handler

        self.response.payload = {
            'is_handler_added': redis_handler is not None and redis_handler in manager.logger.handlers,
            'slot': get_slot_or_single(),
        }

# ################################################################################################################################
# ################################################################################################################################

class LockHold(Service):
    """ Acquires one named lock a given number of times, yielding to other greenlets while it holds the lock,
    and returns the start and the end of each hold on the monotonic clock of the host, with the slot that held it.
    """
    name = 'test.multi-cpu.lock-hold'

    def handle(self) -> 'None':
        request = self.request.payload
        slot = get_slot_or_single()
        holds:'list[list[int]]' = []

        for _ in range(request['hold_count']):
            with self.lock(request['lock_name'], request['ttl'], request['block']):
                start = monotonic_ns()
                sleep(request['hold_time'])
                end = monotonic_ns()

            holds.append([start, end, slot])

        self.response.payload = {
            'holds': holds,
        }

# ################################################################################################################################
# ################################################################################################################################

class AuditEcho(Service):
    """ Returns the correlation ID of the request and the slot of the worker that served it, by which a test finds
    the audit events of the request.
    """
    name = 'test.multi-cpu.audit-echo'

    def handle(self) -> 'None':
        self.response.payload = {
            'cid': self.cid,
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
