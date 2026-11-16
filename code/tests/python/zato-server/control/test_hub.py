# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from select import poll
from socket import MSG_PEEK

# pytest
import pytest

# Zato
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx
from zato.server.control.envelope import decode, encode, MessageType, ModuleCtx as EnvelopeCtx, new_message
from zato.server.control.hub import ControlHub, EntryStatus

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from socket import socket
    from zato.common.typing_ import any_, anylist, dict_, intlist, list_
    from zato.server.control.envelope import Message

    any_ = any_
    anylist = anylist
    intlist = intlist
    Message = Message
    Path = Path
    socket = socket

    intsocketdict = dict_[int, socket]
    messagelist   = list_[Message]

# ################################################################################################################################
# ################################################################################################################################

# The slots of the worker and of the config process
_worker = WorkerSlotCtx.Worker_Slot
_config = WorkerSlotCtx.Config_Slot

# How long a poll of the hub waits for its descriptors, in milliseconds
_poll_timeout_ms = 100

# How long the end of a process waits for a datagram, in seconds
_receive_timeout = 2.0

# How long a query waits for its response in the tests of its deadline, in seconds
_short_query_timeout = 0.05

# How many events a test sends to a process that reads nothing, and the size of each
_backlog_count = 2000
_backlog_body_size = 1024

# ################################################################################################################################
# ################################################################################################################################

class HubUnderTest:
    """ A hub with the ends of the worker and of the config process, and the slots that reported ready to it.
    """

    def __init__(self, body_dir:'str', query_timeout:'float'=_receive_timeout) -> 'None':
        self.body_dir = body_dir
        self.ready_slots:'intlist' = []
        self.reopened:'anylist' = []
        self.replaced_slots:'intlist' = []
        self.hub = ControlHub(body_dir, query_timeout, self.ready_slots.append, self.on_logs_reopened,
            self.replaced_slots.append)
        self.ends:'intsocketdict' = {}

        for slot in (_worker, _config):
            end = self.hub.open_slot(slot)
            end.settimeout(_receive_timeout)
            self.ends[slot] = end

    def on_logs_reopened(self, slot:'int', rotation_id:'int') -> 'None':
        self.reopened.append((slot, rotation_id))

    def pump(self) -> 'None':
        """ Runs one poll of the hub, as the main loop of the arbiter does.
        """
        poller = poll()

        for fd, events in self.hub.get_poll_requests():
            poller.register(fd, events)

        poll_events = poller.poll(_poll_timeout_ms)
        self.hub.handle_poll_events(poll_events)

    def send(self, slot:'int', message_type:'str', body:'any_', cid:'str'='') -> 'None':
        message = new_message(message_type, body, cid)
        datagram = encode(message, self.body_dir)

        _ = self.ends[slot].send(datagram)
        self.pump()

    def report_ready(self, slot:'int') -> 'None':
        """ Reports a process ready, and reads the loading state that a config process receives ahead of everything else.
        """
        self.send(slot, MessageType.Ready, None)

        if slot == _config:
            message = self.receive(_config)

            assert message.type == MessageType.Loading_State
            assert message.body == []

    def receive(self, slot:'int') -> 'Message':
        datagram = self.ends[slot].recv(EnvelopeCtx.Max_Datagram)
        out = decode(datagram)
        return out

    def has_nothing(self, slot:'int') -> 'bool':
        """ Returns whether the end of a process holds no datagram.
        """
        end = self.ends[slot]
        end.setblocking(False)

        try:
            _ = end.recv(EnvelopeCtx.Max_Datagram, MSG_PEEK)
        except BlockingIOError:
            out = True
        else:
            out = False

        end.settimeout(_receive_timeout)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _assert_in_order(messages:'messagelist') -> 'None':
    for index in range(1, len(messages)):
        assert messages[index].seq > messages[index - 1].seq

# ################################################################################################################################
# ################################################################################################################################

def test_an_event_reaches_the_other_process_in_sequence_order(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_worker)
    test.report_ready(_config)

    assert test.ready_slots == [_worker, _config]

    # The worker publishes events ..
    for body in range(5):
        test.send(_worker, MessageType.Event, body)

    # .. the config process receives all of them in sequence order ..
    received:'messagelist' = []

    for _ in range(5):
        message = test.receive(_config)
        received.append(message)

    _assert_in_order(received)

    for body in range(5):
        assert received[body].body == body
        assert received[body].slot == _worker

    # .. and the event of the config process reaches the worker, which never receives its own.
    test.send(_config, MessageType.Event, 'from-config')
    message = test.receive(_worker)

    assert message.body == 'from-config'
    assert message.slot == _config
    assert test.has_nothing(_worker)

# ################################################################################################################################

def test_events_for_a_starting_process_wait_until_it_reports_ready(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_config)

    # The starting worker receives nothing while the config process publishes ..
    for body in range(3):
        test.send(_config, MessageType.Event, body)

    assert test.has_nothing(_worker)
    assert test.ready_slots == [_config]

    # .. and every event once it reports ready, in order.
    test.report_ready(_worker)
    assert test.ready_slots == [_config, _worker]

    received:'messagelist' = []

    for _ in range(3):
        message = test.receive(_worker)
        received.append(message)

    _assert_in_order(received)

    for body in range(3):
        assert received[body].body == body

# ################################################################################################################################

def test_a_large_event_gives_the_recipient_a_file_of_its_own(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    test = HubUnderTest(body_dir)
    test.report_ready(_worker)
    test.report_ready(_config)

    body_size = EnvelopeCtx.Max_Inline_Body + 1
    body = 'a' * body_size

    # The file of the origin is replaced by one file of the recipient ..
    test.send(_worker, MessageType.Event, body)
    assert len(os.listdir(body_dir)) == 1

    # .. which the recipient removes when it reads the body.
    message = test.receive(_config)

    assert message.body == body
    assert os.listdir(body_dir) == []

# ################################################################################################################################

def test_a_query_of_the_config_process_returns_the_response_of_the_worker(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_worker)
    test.report_ready(_config)

    # The worker receives the query ..
    test.send(_config, MessageType.Query, 'my-query', 'my-cid')
    query = test.receive(_worker)

    assert query.type == MessageType.Query
    assert query.cid == 'my-cid'
    assert query.body == 'my-query'

    # .. and its response reaches the config process.
    test.send(_worker, MessageType.Response, 'from-worker', 'my-cid')
    result = test.receive(_config)

    assert result.type == MessageType.Query_Result
    assert result.cid == 'my-cid'
    assert result.body == {'status': EntryStatus.OK, 'body': 'from-worker'}

# ################################################################################################################################

def test_a_query_without_a_ready_worker_is_unavailable(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_config)

    test.send(_config, MessageType.Query, None, 'my-cid')
    result = test.receive(_config)

    assert result.body == {'status': EntryStatus.Unavailable, 'body': None}
    assert test.has_nothing(_worker)

# ################################################################################################################################

def test_a_query_that_the_worker_does_not_answer_times_out(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), _short_query_timeout)
    test.report_ready(_worker)
    test.report_ready(_config)

    test.send(_config, MessageType.Query, None, 'my-cid')
    _ = test.receive(_worker)

    # The query waits for the worker until its deadline ..
    assert test.hub.get_next_deadline() is not None
    assert test.has_nothing(_config)

    time.sleep(_short_query_timeout)
    test.hub.expire_queries(time.monotonic())

    result = test.receive(_config)
    assert result.body == {'status': EntryStatus.Timeout, 'body': None}

    # .. and the late response belongs to no query any more.
    assert test.hub.get_next_deadline() is None

    test.send(_worker, MessageType.Response, 'from-worker', 'my-cid')
    assert test.has_nothing(_config)

# ################################################################################################################################

def test_closing_the_worker_answers_its_queries(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_worker)
    test.report_ready(_config)

    # A query waits for the worker ..
    test.send(_config, MessageType.Query, None, 'my-cid')
    _ = test.receive(_worker)

    # .. the worker terminates, which completes the query ..
    test.hub.close_slot(_worker)

    result = test.receive(_config)
    assert result.body == {'status': EntryStatus.Unavailable, 'body': None}

    # .. after which the config process learns that the worker terminated.
    message = test.receive(_config)

    assert message.type == MessageType.Worker_Gone
    assert message.body == _worker

# ################################################################################################################################

def test_closing_a_starting_worker_removes_its_undelivered_bodies(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    test = HubUnderTest(body_dir)
    test.report_ready(_config)

    body_size = EnvelopeCtx.Max_Inline_Body + 1
    body = 'a' * body_size

    # The starting worker holds a body in its startup buffer ..
    test.send(_config, MessageType.Event, body)
    assert len(os.listdir(body_dir)) == 1

    # .. and once it closes, no file remains.
    test.hub.close_slot(_worker)
    assert os.listdir(body_dir) == []

# ################################################################################################################################

def test_a_process_that_reads_nothing_does_not_hold_the_hub(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_worker)
    test.report_ready(_config)

    body = 'a' * _backlog_body_size

    # More events than the socket of the recipient holds wait in the queue of its slot ..
    for _ in range(_backlog_count):
        test.send(_worker, MessageType.Event, body)

    assert test.hub.channels[_config].out_queue

    # .. and the recipient receives every one of them in order once it reads.
    received:'messagelist' = []

    # The socket reports that it takes more only once most of its buffer is free, so the hub runs when it is empty.
    while len(received) < _backlog_count:
        if test.has_nothing(_config):
            test.pump()

        message = test.receive(_config)
        received.append(message)

    _assert_in_order(received)
    assert not test.hub.channels[_config].out_queue

# ################################################################################################################################

def test_the_event_of_a_terminated_worker_is_relayed_before_its_slot_closes(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_worker)
    test.report_ready(_config)

    # The worker sends its event and terminates before a poll of the arbiter reports the datagram ..
    message = new_message(MessageType.Event, 'last-event')
    datagram = encode(message, test.body_dir)

    _ = test.ends[_worker].send(datagram)
    test.ends[_worker].close()

    # .. and the arbiter relays it when it closes the slot, ahead of the notice of the termination.
    test.hub.close_slot(_worker)

    received = test.receive(_config)
    assert received.body == 'last-event'

    received = test.receive(_config)
    assert received.type == MessageType.Worker_Gone

# ################################################################################################################################

def test_a_drain_reaches_a_starting_worker(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.hub.send_drain(_worker)

    message = test.receive(_worker)
    assert message.type == MessageType.Drain

# ################################################################################################################################

def test_a_reload_reaches_a_starting_worker_after_it_reports_ready(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_config)

    test.hub.broadcast_reload()

    # The config process commits every change itself and receives no reload ..
    assert test.has_nothing(_config)
    assert test.has_nothing(_worker)

    # .. and the worker receives it once it reports ready.
    test.report_ready(_worker)

    message = test.receive(_worker)
    assert message.type == MessageType.Reload

# ################################################################################################################################

def test_a_closed_end_is_no_longer_polled(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))

    test.ends[_worker].close()
    test.pump()

    requests = test.hub.get_poll_requests()
    assert len(requests) == 1

# ################################################################################################################################

def test_a_reopen_of_logs_reaches_both_processes_a_starting_one_included(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_worker)

    # The command is sent to both processes at once, although the config process has not reported ready ..
    slots = test.hub.broadcast_reopen_logs(7)
    assert slots == {_worker, _config}

    for slot in (_worker, _config):
        message = test.receive(slot)
        assert message.type == MessageType.Reopen_Logs
        assert message.body == 7

    # .. and each acknowledgement reaches the arbiter with its slot and its rotation.
    test.send(_config, MessageType.Logs_Reopened, 7)
    test.send(_worker, MessageType.Logs_Reopened, 7)

    assert test.reopened == [(_config, 7), (_worker, 7)]

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
