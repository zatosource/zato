# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import signal
import sqlite3
import unittest
from threading import Event, Lock, Thread
from time import monotonic, sleep

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditEvent, AuditSource
from zato.common.test.client import PublishClient
from zato.common.test.conftest_base_multi_cpu import get_parent_pid, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     new_connection, WorkerControl
from zato.common.test.receiver import wait_until_receivers_quiet
from zato.common.typing_ import cast_

# Test helpers
from _suite import MigrationConfig, restart_server, set_delivery_active

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http.client import HTTPConnection
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import any_, anydict, anylist, intset, strlist, strlistdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_migration.graceful_stop')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Several_Worker_Count = 4

    # How many threads publish and send REST requests, and for how long they run before the server is stopped, in seconds
    Publisher_Count = 2
    REST_Client_Count = 4
    Load_Duration = 5.0

    # How many requests are in progress when the arbiter receives SIGTERM, and how long they have to reach the workers,
    # in seconds
    In_Flight_Count = 8
    In_Flight_Settle_Time = 0.3

    # How long each receiver holds a delivery, which keeps delivery rounds in progress when the server stops, in seconds
    Receiver_Hang = 0.5

    # The stop grace period of an active-standby node, which a graceful stop completes within, in seconds
    Stop_Deadline = 10.0

    # How long the subscribers have to receive every acknowledged message after the next start, in seconds
    Delivery_Timeout = 120.0

    # The message that the arbiter logs for a worker that it terminates after the grace period
    Worker_Terminated_Message = 'did not exit within'

    Event_Query = """
        select cid, event_type
        from event
        where source = :source and object_name = :object_name
    """

# ################################################################################################################################
# ################################################################################################################################

def _get_seq(message:'anydict') -> 'int':
    data:'any_' = message['data']

    if isinstance(data, str):
        data = json.loads(data)

    out = data['seq']
    return out

# ################################################################################################################################

def _get_seqs(receiver:'WebhookReceiver') -> 'intset':
    out:'intset' = set()

    for message in receiver.get_delivered_messages():
        out.add(_get_seq(message))

    return out

# ################################################################################################################################

def _read_event_types() -> 'strlistdict':
    """ Returns the types of the audit events of the drain channel by the correlation ID of their request,
    from the audit database of the server, which is read without becoming a writer of it.
    """
    params = {
        'source': AuditSource.REST_Channel,
        'object_name': MigrationConfig.Drain_Sleep_Channel,
    }

    path = os.environ[AuditLogCtx.Env_Name]
    out:'strlistdict' = {}

    with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as connection:
        cursor = connection.execute(ModuleCtx.Event_Query, params)

        for cid, event_type in cursor.fetchall():
            out.setdefault(cid, []).append(event_type)

    return out

# ################################################################################################################################

def _read_drain_response(connection:'HTTPConnection') -> 'tuple[int, str]':
    """ Returns the status of a response of the drain channel and the correlation ID of its request.
    """
    response = connection.getresponse()
    body = response.read()
    connection.close()

    cid = ''

    if response.status == MultiCPUCtx.Status_OK:
        cid = json.loads(body)['cid']

    out = (response.status, cid)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGracefulStopUnderLoad(unittest.TestCase):
    """ SIGTERM of the arbiter during sustained REST and pub/sub traffic completes the requests in progress within
    the grace period, interrupts delivery rounds without terminating a worker, writes the audit events
    of every completed request, and the next start delivers every acknowledged message.
    """

    def test_sigterm_under_load(self) -> 'None':

        restart_server(ModuleCtx.Several_Worker_Count)
        set_delivery_active(True)

        for receiver in MigrationConfig.receivers:
            receiver.behavior.set_hang(ModuleCtx.Receiver_Hang)

        control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        rows = control.wait_for_all_ready()
        arbiter_pid = get_parent_pid(rows[0]['pid'])

        lock = Lock()
        load_ended = Event()

        acknowledged:'intset' = set()
        completed_cids:'strlist' = []
        state:'anydict' = {'next_seq': 0, 'publish_failures': 0, 'rest_failures': 0}

        def _next_seq() -> 'int':
            with lock:
                out = state['next_seq']
                state['next_seq'] += 1
            return out

        # Each publisher publishes numbered messages until the load ends, and only an acknowledged one is counted ..
        def _publish() -> 'None':
            publisher = PublishClient(MultiCPUTestConfig.base_url, MigrationConfig.Publisher_Name,
                MultiCPUTestConfig.sec_password)

            while not load_ended.is_set():
                seq = _next_seq()

                try:
                    _ = publisher.publish(MigrationConfig.Topic_Name, {'seq': seq})
                except Exception:
                    with lock:
                        state['publish_failures'] += 1
                    continue

                with lock:
                    acknowledged.add(seq)

        # .. and each REST client invokes the drain channel and keeps the correlation ID of every completed request.
        def _rest() -> 'None':
            while not load_ended.is_set():
                try:
                    connection = new_connection()
                    connection.request('GET', MigrationConfig.Drain_Sleep_Path)
                    status, cid = _read_drain_response(connection)
                except Exception:
                    with lock:
                        state['rest_failures'] += 1
                    continue

                if status == MultiCPUCtx.Status_OK:
                    with lock:
                        completed_cids.append(cid)

        threads:'anylist' = []

        for _ in range(ModuleCtx.Publisher_Count):
            threads.append(Thread(target=_publish, daemon=True))

        for _ in range(ModuleCtx.REST_Client_Count):
            threads.append(Thread(target=_rest, daemon=True))

        for thread in threads:
            thread.start()

        sleep(ModuleCtx.Load_Duration)

        # The requests in progress when the arbiter receives SIGTERM ..
        in_flight:'anylist' = []

        for _ in range(ModuleCtx.In_Flight_Count):
            connection = new_connection()
            connection.request('GET', MigrationConfig.Drain_Sleep_Path)
            in_flight.append(connection)

        sleep(ModuleCtx.In_Flight_Settle_Time)

        os.kill(arbiter_pid, signal.SIGTERM)
        stop_started = monotonic()

        # .. each complete ..
        for connection in in_flight:
            status, cid = _read_drain_response(connection)
            self.assertEqual(status, MultiCPUCtx.Status_OK)
            completed_cids.append(cid)

        # .. and the server terminates within the grace period ..
        server_process = cast_('any_', MigrationConfig.state.server_process)
        _ = server_process.wait(timeout=ModuleCtx.Stop_Deadline)

        while os.path.exists(f'/proc/{arbiter_pid}'):
            self.assertLess(monotonic() - stop_started, ModuleCtx.Stop_Deadline)
            sleep(MultiCPUCtx.Poll_Interval)

        stop_duration = monotonic() - stop_started

        load_ended.set()

        for thread in threads:
            thread.join()

        logger.info('Stopped in %.2fs -> acknowledged %s, completed %s, %s', stop_duration, len(acknowledged),
            len(completed_cids), state)

        # .. without terminating a worker that did not drain ..
        server_log_path = os.path.join(MultiCPUTestConfig.server_directory, 'logs', 'server.log')

        with open(server_log_path) as server_log:
            server_log_text = server_log.read()

        self.assertNotIn(ModuleCtx.Worker_Terminated_Message, server_log_text)

        # .. and every completed request has its request and response events in the audit log.
        event_types_by_cid = _read_event_types()

        for cid in completed_cids:
            event_types = sorted(event_types_by_cid[cid])
            self.assertEqual(event_types, [AuditEvent.Request_Received, AuditEvent.Response_Sent], cid)

        # The next start delivers every acknowledged message.
        for receiver in MigrationConfig.receivers:
            receiver.behavior.set_accept()

        restart_server(ModuleCtx.Several_Worker_Count)

        deadline = monotonic() + ModuleCtx.Delivery_Timeout

        for index, receiver in enumerate(MigrationConfig.receivers):
            received = _get_seqs(receiver)

            while not acknowledged <= received:
                if monotonic() > deadline:
                    break

                sleep(MultiCPUCtx.Poll_Interval)
                received = _get_seqs(receiver)

            missing = acknowledged - received
            self.assertEqual(missing, set(), f'Subscriber {index} did not receive {len(missing)} messages')

        wait_until_receivers_quiet(MigrationConfig.receivers)

# ################################################################################################################################
# ################################################################################################################################
