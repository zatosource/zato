# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many messages a test publishes, spread over every slot in turn
    Message_Count = 12

    # How long the receiver may hold the first delivery, which keeps every other message in the queue, in seconds
    Hold_Timeout = 60.0

    # How long every slot has to report a value and how long the receiver has to receive every message, in seconds
    Deadline = 60.0

    Host = '127.0.0.1'
    URL_Path = '/multi-cpu/outgoing-queue'

    Publish_Service = 'test.multi-cpu.outconn-publish'
    Queue_List_Service = 'zato.pubsub.outgoing.get-queue-list'
    Message_List_Service = 'zato.pubsub.outgoing.get-message-list'

    Kind_Queue = 'queue'

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHandler(BaseHTTPRequestHandler):
    """ Records the body of each request in the order of arrival, holding each response until the receiver is released.
    """
    protocol_version = 'HTTP/1.1'

    def do_POST(self) -> 'None':
        server:'any_' = self.server

        body = self.rfile.read(int(self.headers['Content-Length']))
        _ = server.release.wait(ModuleCtx.Hold_Timeout)

        server.bodies.append(json.loads(body))

        # The thread of a connection that the pool of a worker kept open would outlive the receiver
        self.send_response(200)
        self.send_header('Content-Length', '0')
        self.send_header('Connection', 'close')
        self.end_headers()

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class _Receiver(ThreadingHTTPServer):

    daemon_threads = True

    def __init__(self) -> 'None':
        super().__init__((ModuleCtx.Host, 0), _ReceiverHandler)
        self.bodies:'anylist' = []
        self.release = Event()

# ################################################################################################################################
# ################################################################################################################################

def _invoke(slot:'int', service_name:'str', payload:'anydict') -> 'anydict':
    status, body = invoke_on_slot(slot, service_name, payload)

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{service_name} returned {status} -> {body}')

    out = json.loads(body)
    return out

# ################################################################################################################################

def _get_queue_row(slot:'int', conn_name:'str') -> 'anydict | None':
    """ Returns the row of the queue of the connection that the worker of a slot lists, or None if it lists no such row.
    """
    for row in _invoke(slot, ModuleCtx.Queue_List_Service, {})['items']:
        if row['name'] == conn_name:
            return row

# ################################################################################################################################

def _publish(slot:'int', payload:'anydict') -> 'None':
    """ Publishes a message through the worker of a slot, once that worker has the connection that the import created.
    """
    deadline = monotonic() + ModuleCtx.Deadline

    while True:
        status, body = invoke_on_slot(slot, ModuleCtx.Publish_Service, payload)

        if status == MultiCPUCtx.Status_OK:
            return

        if monotonic() > deadline:
            raise Exception(f'Message not published through slot {slot} -> {status} {body}')

        sleep(MultiCPUCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingQueuesAcrossWorkers(unittest.TestCase):
    """ The queue of an outgoing connection, published to through every slot, reports one depth and one content
    through every slot and delivers its messages in the order of publication, whichever worker owns its delivery.
    """

    def test_depth_browse_and_order(self) -> 'None':

        receiver = _Receiver()
        Thread(target=receiver.serve_forever, daemon=True).start()

        conn_name = f'test.multi-cpu.outgoing-queue.{uuid4().hex[:12]}'

        try:
            enmasse_import({
                'outgoing_rest': [{
                    'name': conn_name,
                    'host': f'http://{ModuleCtx.Host}:{receiver.server_address[1]}',
                    'url_path': ModuleCtx.URL_Path,
                    'method': 'POST',
                    'data_format': 'json',
                    'timeout': ModuleCtx.Hold_Timeout,
                }],
            })

            # Each message is published through the next slot, so every worker publishes to the queue ..
            for seq in range(ModuleCtx.Message_Count):
                slot = seq % MultiCPUTestConfig.worker_count
                _publish(slot, {'conn_name': conn_name, 'data': {'seq': seq}})

            # The receiver holds the first delivery, so every slot reports the same depth ..
            def _reports_depth(slot:'int') -> 'bool':
                row = _get_queue_row(slot, conn_name)
                out = row is not None and row['queue_depth'] == ModuleCtx.Message_Count
                return out

            wait_for_every_slot(_reports_depth, f'depth {ModuleCtx.Message_Count}', ModuleCtx.Deadline)

            # .. and the same content, browsed through each slot, whichever worker owns the delivery ..
            row = _get_queue_row(0, conn_name)
            assert row is not None

            browse_request = {'conn_type': row['conn_type'], 'conn_id': row['conn_id'], 'kind': ModuleCtx.Kind_Queue}

            totals:'dict[int, int]' = {}

            for slot in range(MultiCPUTestConfig.worker_count):
                totals[slot] = _invoke(slot, ModuleCtx.Message_List_Service, browse_request)['total']

            self.assertEqual(len(set(totals.values())), 1, totals)

            # .. after which every message is delivered in the order of its publication ..
            receiver.release.set()

            deadline = monotonic() + ModuleCtx.Deadline

            while len(receiver.bodies) < ModuleCtx.Message_Count:
                if monotonic() > deadline:
                    raise Exception(f'Received {len(receiver.bodies)} of {ModuleCtx.Message_Count} messages')
                sleep(MultiCPUCtx.Poll_Interval)

            received = [body['seq'] for body in receiver.bodies]
            self.assertEqual(received, list(range(ModuleCtx.Message_Count)))

            # .. and every slot reports an empty queue.
            def _reports_empty(slot:'int') -> 'bool':
                row = _get_queue_row(slot, conn_name)
                out = row is not None and row['queue_depth'] == 0
                return out

            wait_for_every_slot(_reports_empty, 'depth 0', ModuleCtx.Deadline)

        finally:
            receiver.release.set()
            receiver.shutdown()
            receiver.server_close()

# ################################################################################################################################
# ################################################################################################################################
