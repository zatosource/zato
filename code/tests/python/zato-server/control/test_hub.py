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
from zato.server.control.envelope import decode, encode, MessageType, ModuleCtx as EnvelopeCtx, new_message
from zato.server.control.hub import ControlHub, EntryStatus

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from socket import socket
    from zato.common.typing_ import any_, anylist, intlist, list_
    from zato.server.control.envelope import Message

    any_ = any_
    anylist = anylist
    intlist = intlist
    Message = Message
    Path = Path
    socket = socket

    socketlist  = list_[socket]
    messagelist = list_[Message]

# ################################################################################################################################
# ################################################################################################################################

# How long a poll of the hub waits for its descriptors, in milliseconds
_poll_timeout_ms = 100

# How long a worker end waits for a datagram, in seconds
_receive_timeout = 2.0

# How long a query waits for its responses in the tests of its deadline, in seconds
_short_query_timeout = 0.05

# How many events a test sends to a worker that reads nothing, and the size of each
_backlog_count = 2000
_backlog_body_size = 1024

# ################################################################################################################################
# ################################################################################################################################

class HubUnderTest:
    """ A hub with the worker ends of its slots and the slots that reported ready to it.
    """

    def __init__(self, body_dir:'str', slot_count:'int', query_timeout:'float'=_receive_timeout) -> 'None':
        self.body_dir = body_dir
        self.ready_slots:'intlist' = []
        self.reopened:'anylist' = []
        self.replaced_slots:'intlist' = []
        self.hub = ControlHub(body_dir, slot_count, query_timeout, self.ready_slots.append, self.on_logs_reopened,
            self.replaced_slots.append)
        self.worker_ends:'socketlist' = []

        for slot in range(slot_count):
            worker_end = self.hub.open_slot(slot)
            worker_end.settimeout(_receive_timeout)
            self.worker_ends.append(worker_end)

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

        _ = self.worker_ends[slot].send(datagram)
        self.pump()

    def report_ready(self, slot:'int') -> 'None':
        self.send(slot, MessageType.Ready, None)

    def receive(self, slot:'int') -> 'Message':
        datagram = self.worker_ends[slot].recv(EnvelopeCtx.Max_Datagram)
        out = decode(datagram)
        return out

    def has_nothing(self, slot:'int') -> 'bool':
        """ Returns whether the worker end of a slot holds no datagram.
        """
        worker_end = self.worker_ends[slot]
        worker_end.setblocking(False)

        try:
            _ = worker_end.recv(EnvelopeCtx.Max_Datagram, MSG_PEEK)
        except BlockingIOError:
            out = True
        else:
            out = False

        worker_end.settimeout(_receive_timeout)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _assert_in_order(messages:'messagelist') -> 'None':
    for index in range(1, len(messages)):
        assert messages[index].seq > messages[index - 1].seq

# ################################################################################################################################
# ################################################################################################################################

def test_an_event_reaches_every_other_slot_in_sequence_order(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 3)

    for slot in range(3):
        test.report_ready(slot)

    assert test.ready_slots == [0, 1, 2]

    # Two slots publish events ..
    for body in range(5):
        test.send(0, MessageType.Event, body)

    test.send(1, MessageType.Event, 'from-1')

    # .. the third slot receives all of them in sequence order ..
    received:'messagelist' = []

    for _ in range(6):
        message = test.receive(2)
        received.append(message)

    _assert_in_order(received)

    for body in range(5):
        assert received[body].body == body
        assert received[body].slot == 0

    assert received[5].body == 'from-1'
    assert received[5].slot == 1

    # .. and an origin receives the events of the other slot, never its own.
    message = test.receive(0)

    assert message.body == 'from-1'
    assert test.has_nothing(0)

# ################################################################################################################################

def test_events_for_a_starting_slot_wait_until_it_reports_ready(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)
    test.report_ready(0)

    # The starting slot receives nothing while the other publishes ..
    for body in range(3):
        test.send(0, MessageType.Event, body)

    assert test.has_nothing(1)
    assert test.ready_slots == [0]

    # .. and every event once it reports ready, in order.
    test.report_ready(1)
    assert test.ready_slots == [0, 1]

    received:'messagelist' = []

    for _ in range(3):
        message = test.receive(1)
        received.append(message)

    _assert_in_order(received)

    for body in range(3):
        assert received[body].body == body

# ################################################################################################################################

def test_a_large_event_gives_each_recipient_a_file_of_its_own(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    test = HubUnderTest(body_dir, 3)

    for slot in range(3):
        test.report_ready(slot)

    body_size = EnvelopeCtx.Max_Inline_Body + 1
    body = 'a' * body_size

    # The origin's file is replaced by one file for each recipient ..
    test.send(0, MessageType.Event, body)
    assert len(os.listdir(body_dir)) == 2

    # .. and each recipient removes its own file when it reads the body.
    first = test.receive(1)
    assert len(os.listdir(body_dir)) == 1

    second = test.receive(2)
    assert os.listdir(body_dir) == []

    assert first.body == body
    assert second.body == body

# ################################################################################################################################

def test_a_query_returns_an_entry_for_every_slot(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 3)
    test.report_ready(0)
    test.report_ready(1)

    # The ready slots receive the query, the origin included, and the starting slot does not ..
    test.send(0, MessageType.Query, 'my-query', 'my-cid')

    for slot in (0, 1):
        query = test.receive(slot)

        assert query.type == MessageType.Query
        assert query.cid == 'my-cid'
        assert query.body == 'my-query'

    assert test.has_nothing(2)

    # .. and once both respond, the origin receives an entry for each slot, in the order of the slots.
    test.send(1, MessageType.Response, 'from-1', 'my-cid')
    test.send(0, MessageType.Response, 'from-0', 'my-cid')

    result = test.receive(0)

    assert result.type == MessageType.Query_Result
    assert result.cid == 'my-cid'
    assert result.body == [
        {'slot': 0, 'status': EntryStatus.OK, 'body': 'from-0'},
        {'slot': 1, 'status': EntryStatus.OK, 'body': 'from-1'},
        {'slot': 2, 'status': EntryStatus.Unavailable, 'body': None},
    ]

# ################################################################################################################################

def test_a_slot_that_awaits_its_respawn_has_an_entry(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)

    # The worker of slot 1 terminated and its slot is closed until the respawn ..
    test.hub.close_slot(1)
    test.report_ready(0)

    test.send(0, MessageType.Query, None, 'my-cid')
    _ = test.receive(0)

    test.send(0, MessageType.Response, 'from-0', 'my-cid')

    # .. which the result still reports.
    result = test.receive(0)

    assert result.body == [
        {'slot': 0, 'status': EntryStatus.OK, 'body': 'from-0'},
        {'slot': 1, 'status': EntryStatus.Unavailable, 'body': None},
    ]

# ################################################################################################################################

def test_a_slot_that_does_not_respond_has_a_timeout_entry(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2, _short_query_timeout)
    test.report_ready(0)
    test.report_ready(1)

    test.send(0, MessageType.Query, None, 'my-cid')
    _ = test.receive(0)

    test.send(0, MessageType.Response, 'from-0', 'my-cid')

    # The query waits for the slot that did not respond until its deadline ..
    assert test.hub.get_next_deadline() is not None
    assert test.has_nothing(0)

    time.sleep(_short_query_timeout)
    test.hub.expire_queries(time.monotonic())

    result = test.receive(0)

    assert result.body == [
        {'slot': 0, 'status': EntryStatus.OK, 'body': 'from-0'},
        {'slot': 1, 'status': EntryStatus.Timeout, 'body': None},
    ]

    # .. and its late response belongs to no query any more.
    assert test.hub.get_next_deadline() is None

    test.send(1, MessageType.Response, 'from-1', 'my-cid')
    assert test.has_nothing(0)

# ################################################################################################################################

def test_closing_a_slot_removes_its_undelivered_bodies_and_answers_its_queries(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    test = HubUnderTest(body_dir, 3)
    test.report_ready(0)
    test.report_ready(1)

    body_size = EnvelopeCtx.Max_Inline_Body + 1
    body = 'a' * body_size

    # The starting slot holds a body in its startup buffer, and the other recipient reads its own ..
    test.send(0, MessageType.Event, body)
    _ = test.receive(1)

    assert len(os.listdir(body_dir)) == 1

    # .. a query waits for a slot that does not respond ..
    test.send(0, MessageType.Query, None, 'my-cid')
    test.send(0, MessageType.Response, 'from-0', 'my-cid')

    # .. the starting slot closes, and no file remains ..
    test.hub.close_slot(2)
    assert os.listdir(body_dir) == []

    # .. and the slot that does not respond closes, which completes the query.
    test.hub.close_slot(1)
    _ = test.receive(0)

    result = test.receive(0)

    assert result.body == [
        {'slot': 0, 'status': EntryStatus.OK, 'body': 'from-0'},
        {'slot': 1, 'status': EntryStatus.Unavailable, 'body': None},
        {'slot': 2, 'status': EntryStatus.Unavailable, 'body': None},
    ]

# ################################################################################################################################

def test_a_worker_that_reads_nothing_does_not_hold_the_hub(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)
    test.report_ready(0)
    test.report_ready(1)

    body = 'a' * _backlog_body_size

    # More events than the socket of the recipient holds wait in the queue of its slot ..
    for _ in range(_backlog_count):
        test.send(0, MessageType.Event, body)

    assert test.hub.channels[1].out_queue

    # .. and the recipient receives every one of them in order once it reads.
    received:'messagelist' = []

    # The socket reports that it takes more only once most of its buffer is free, so the hub runs when it is empty.
    while len(received) < _backlog_count:
        if test.has_nothing(1):
            test.pump()

        message = test.receive(1)
        received.append(message)

    _assert_in_order(received)
    assert not test.hub.channels[1].out_queue

# ################################################################################################################################

def test_the_event_of_a_terminated_worker_is_relayed_before_its_slot_closes(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)
    test.report_ready(0)
    test.report_ready(1)

    # The worker sends its event and terminates before a poll of the arbiter reports the datagram ..
    message = new_message(MessageType.Event, 'last-event')
    datagram = encode(message, test.body_dir)

    _ = test.worker_ends[1].send(datagram)
    test.worker_ends[1].close()

    # .. and the arbiter relays it when it closes the slot.
    test.hub.close_slot(1)

    received = test.receive(0)
    assert received.body == 'last-event'

# ################################################################################################################################

def test_a_drain_reaches_a_starting_slot(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 1)
    test.hub.send_drain(0)

    message = test.receive(0)
    assert message.type == MessageType.Drain

# ################################################################################################################################

def test_a_reload_reaches_a_starting_slot_after_it_reports_ready(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)
    test.report_ready(0)

    test.hub.broadcast_reload()

    message = test.receive(0)
    assert message.type == MessageType.Reload
    assert test.has_nothing(1)

    test.report_ready(1)

    message = test.receive(1)
    assert message.type == MessageType.Reload

# ################################################################################################################################

def test_a_closed_worker_end_is_no_longer_polled(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)

    test.worker_ends[1].close()
    test.pump()

    requests = test.hub.get_poll_requests()
    assert len(requests) == 1

# ################################################################################################################################

def test_a_reopen_of_logs_reaches_every_slot_a_starting_one_included(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path), 2)
    test.report_ready(0)

    # The command is sent to both slots at once, although one has not reported ready ..
    slots = test.hub.broadcast_reopen_logs(7)
    assert slots == {0, 1}

    for slot in range(2):
        message = test.receive(slot)
        assert message.type == MessageType.Reopen_Logs
        assert message.body == 7

    # .. and each acknowledgement reaches the arbiter with its slot and its rotation.
    test.send(1, MessageType.Logs_Reopened, 7)
    test.send(0, MessageType.Logs_Reopened, 7)

    assert test.reopened == [(1, 7), (0, 7)]

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
