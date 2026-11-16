# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import count
from threading import Event, Lock, Thread
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the publications run before and after a connection is changed, in seconds
    Publish_Before = 1.0
    Publish_After = 1.0

    # How long each publisher waits between its publications, in seconds
    Publish_Interval = 0.01

    # How long the receiver takes to answer each delivery, which keeps a backlog in the queue while it is changed, in seconds
    Answer_Delay = 0.02

    # How long a request sent before the deletion returned may take to reach the receiver, in seconds
    Arrival_Margin = 0.02

    # How long the receiver is observed for deliveries after the deletion returned, in seconds
    Quiet_Period = 3.0

    # How long every slot has to report a value and how long the receiver has to receive every message, in seconds
    Deadline = 60.0

    Host = '127.0.0.1'
    URL_Path = '/multi-cpu/outgoing-queue-change'

    Publish_Service = 'test.multi-cpu.outconn-publish'
    Rename_Service = 'test.multi-cpu.outconn-rename'
    Queue_List_Service = 'zato.pubsub.outgoing.get-queue-list'

    Method = 'POST'
    Data_Format = 'json'

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHandler(BaseHTTPRequestHandler):
    """ Records the time of arrival and the body of each request, and answers each after a delay.
    """
    protocol_version = 'HTTP/1.1'

    def do_POST(self) -> 'None':
        server:'any_' = self.server
        arrived_at = monotonic()

        body = self.rfile.read(int(self.headers['Content-Length']))

        with server.lock:
            server.arrivals.append(arrived_at)
            server.bodies.append(json.loads(body))

        sleep(ModuleCtx.Answer_Delay)

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
        self.lock = Lock()
        self.arrivals:'anylist' = []
        self.bodies:'anylist' = []

    def get_seqs(self) -> 'intset':
        with self.lock:
            out = {body['seq'] for body in self.bodies}
        return out

# ################################################################################################################################
# ################################################################################################################################

class _Publishers:
    """ Publishes to the queue of a connection through every slot at once, each publisher under the name
    that the connection has at the time, and records the sequence number of each publication that was accepted.
    """
    def __init__(self, conn_name:'str') -> 'None':
        self.conn_name = conn_name
        self.lock = Lock()
        self.seq = count()
        self.accepted:'intset' = set()
        self.stopped = Event()
        self.threads:'anylist' = []

    def _publish(self, slot:'int') -> 'None':
        while not self.stopped.is_set():

            with self.lock:
                seq = next(self.seq)
                conn_name = self.conn_name

            status, _ = invoke_on_slot(slot, ModuleCtx.Publish_Service, {'conn_name': conn_name, 'data': {'seq': seq}})

            # A publication through a worker that does not know the name of the connection is refused,
            # and only an accepted one is expected to be delivered.
            if status == MultiCPUCtx.Status_OK:
                with self.lock:
                    self.accepted.add(seq)

            sleep(ModuleCtx.Publish_Interval)

    def start(self) -> 'None':
        for slot in range(MultiCPUTestConfig.worker_count):
            thread = Thread(target=self._publish, args=(slot,), name=f'publisher-{slot}', daemon=True)
            thread.start()
            self.threads.append(thread)

    def rename(self, new_name:'str') -> 'None':
        with self.lock:
            self.conn_name = new_name

    def stop(self) -> 'None':
        self.stopped.set()
        for thread in self.threads:
            thread.join()

# ################################################################################################################################
# ################################################################################################################################

def _get_queue_row(slot:'int', conn_name:'str') -> 'anydict | None':
    """ Returns the row of the queue of the connection that the worker of a slot lists, or None if it lists no such row.
    """
    status, body = invoke_on_slot(slot, ModuleCtx.Queue_List_Service, {})

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{ModuleCtx.Queue_List_Service} returned {status} -> {body}')

    for row in json.loads(body)['items']:
        if row['name'] == conn_name:
            return row

# ################################################################################################################################

def _create_connection(receiver:'_Receiver') -> 'str':
    """ Creates an outgoing REST connection to the receiver and returns its name once every slot lists its queue.
    """
    out = f'test.multi-cpu.outgoing-change.{uuid4().hex[:12]}'

    enmasse_import({
        'outgoing_rest': [{
            'name': out,
            'host': f'http://{ModuleCtx.Host}:{receiver.server_address[1]}',
            'url_path': ModuleCtx.URL_Path,
            'method': ModuleCtx.Method,
            'data_format': ModuleCtx.Data_Format,
        }],
    })

    def _lists_queue(slot:'int') -> 'bool':
        row = _get_queue_row(slot, out)
        return row is not None

    wait_for_every_slot(_lists_queue, f'queue of {out}', ModuleCtx.Deadline)

    return out

# ################################################################################################################################

def _rename_connection(conn_name:'str', new_name:'str') -> 'None':
    status, body = invoke_on_slot(0, ModuleCtx.Rename_Service, {'conn_name': conn_name, 'new_name': new_name})

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{ModuleCtx.Rename_Service} returned {status} -> {body}')

# ################################################################################################################################

def _delete_connection(conn_name:'str') -> 'None':
    enmasse_import({
        'outgoing_rest': [{
            'name': conn_name,
            'should_delete': True,
        }],
    })

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingQueueChangesAcrossWorkers(unittest.TestCase):
    """ A connection renamed or deleted while every slot publishes to its queue loses no publication that was accepted
    and delivers nothing after its deletion returned, whichever worker owns the delivery of its queue.
    """

    def setUp(self) -> 'None':
        self.receiver = _Receiver()
        self.receiver_thread = Thread(target=self.receiver.serve_forever, name='outgoing-change-receiver', daemon=True)
        self.receiver_thread.start()

    def tearDown(self) -> 'None':
        self.receiver.shutdown()
        self.receiver.server_close()
        self.receiver_thread.join()

# ################################################################################################################################

    def test_rename_under_publication(self) -> 'None':

        conn_name = _create_connection(self.receiver)
        new_name = f'{conn_name}.renamed'

        publishers = _Publishers(conn_name)
        publishers.start()

        try:
            sleep(ModuleCtx.Publish_Before)

            # The connection is renamed the way the Dashboard renames it ..
            _rename_connection(conn_name, new_name)

            # .. after which the publishers use the new name.
            publishers.rename(new_name)
            sleep(ModuleCtx.Publish_After)

        finally:
            publishers.stop()

        # Every publication that was accepted, under either name, is delivered ..
        deadline = monotonic() + ModuleCtx.Deadline

        while not publishers.accepted <= self.receiver.get_seqs():
            if monotonic() > deadline:
                missing = sorted(publishers.accepted - self.receiver.get_seqs())
                raise Exception(f'Accepted publications not delivered -> {missing}')
            sleep(MultiCPUCtx.Poll_Interval)

        # .. and every slot lists the queue under the new name only.
        def _lists_new_name_only(slot:'int') -> 'bool':
            out = _get_queue_row(slot, conn_name) is None and _get_queue_row(slot, new_name) is not None
            return out

        wait_for_every_slot(_lists_new_name_only, f'queue of {new_name} only', ModuleCtx.Deadline)

        _delete_connection(new_name)

# ################################################################################################################################

    def test_delete_under_publication(self) -> 'None':

        conn_name = _create_connection(self.receiver)

        publishers = _Publishers(conn_name)
        publishers.start()

        try:
            sleep(ModuleCtx.Publish_Before)

            _delete_connection(conn_name)
            deleted_at = monotonic()

        finally:
            publishers.stop()

        sleep(ModuleCtx.Quiet_Period)

        # No delivery started after the deletion returned ..
        with self.receiver.lock:
            late_arrivals = [arrived_at - deleted_at for arrived_at in self.receiver.arrivals \
                if arrived_at > deleted_at + ModuleCtx.Arrival_Margin]

        self.assertEqual(late_arrivals, [])

        # .. and no slot lists the queue.
        def _lists_no_queue(slot:'int') -> 'bool':
            out = _get_queue_row(slot, conn_name) is None
            return out

        wait_for_every_slot(_lists_no_queue, 'no queue', ModuleCtx.Deadline)

# ################################################################################################################################
# ################################################################################################################################
