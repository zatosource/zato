# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from select import poll
from socket import MSG_PEEK

# Zato
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx
from zato.server.control.config_route import ModuleCtx as ConfigRouteCtx
from zato.server.control.envelope import decode, encode, MessageType, ModuleCtx as EnvelopeCtx, new_message
from zato.server.control.hub import ControlHub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from socket import socket
    from zato.common.typing_ import any_, intlist
    from zato.server.control.envelope import Message

    any_ = any_
    intlist = intlist
    Message = Message
    Path = Path
    socket = socket

# ################################################################################################################################
# ################################################################################################################################

# How long a poll of the hub waits for its descriptors, in milliseconds
_poll_timeout_ms = 100

# How long the end of a process waits for a datagram, in seconds
_receive_timeout = 2.0

# The slots of the worker and of the config process
_worker_slot = WorkerSlotCtx.Worker_Slot
_config_slot = WorkerSlotCtx.Config_Slot

# ################################################################################################################################
# ################################################################################################################################

class HubUnderTest:
    """ A hub with the ends of the worker and of the config process.
    """

    def __init__(self, body_dir:'str') -> 'None':
        self.body_dir = body_dir
        self.ready_slots:'intlist' = []
        self.hub = ControlHub(body_dir, _receive_timeout, self.ready_slots.append, self.on_logs_reopened, self.on_replaced)
        self.ends:'dict[int, socket]' = {}

        self.open(_config_slot)
        self.open(_worker_slot)

    def on_logs_reopened(self, slot:'int', rotation_id:'int') -> 'None':
        pass

    def on_replaced(self, slot:'int') -> 'None':
        pass

    def open(self, slot:'int') -> 'None':
        end = self.hub.open_slot(slot)
        end.settimeout(_receive_timeout)
        self.ends[slot] = end

    def close(self, slot:'int') -> 'None':
        self.ends[slot].close()
        self.hub.close_slot(slot)

    def pump(self) -> 'None':
        """ Runs one poll of the hub, as the main loop of the arbiter does.
        """
        poller = poll()

        for fd, events in self.hub.get_poll_requests():
            poller.register(fd, events)

        poll_events = poller.poll(_poll_timeout_ms)
        self.hub.handle_poll_events(poll_events)

    def send(self, slot:'int', message_type:'str', body:'any_', cid:'str'='', target:'int'=EnvelopeCtx.No_Slot) -> 'None':
        message = new_message(message_type, body, cid, target)
        datagram = encode(message, self.body_dir)

        _ = self.ends[slot].send(datagram)
        self.pump()

    def report_ready(self, slot:'int') -> 'None':
        """ Reports a process ready, and reads the empty loading state that a config process receives first.
        """
        self.send(slot, MessageType.Ready, None)

        if slot == _config_slot:
            state = self.receive(_config_slot)

            assert state.type == MessageType.Loading_State
            assert state.body == []

    def receive(self, slot:'int') -> 'Message':
        datagram = self.ends[slot].recv(EnvelopeCtx.Max_Datagram)
        out = decode(datagram)
        return out

    def has_nothing(self, slot:'int') -> 'bool':
        """ Returns whether the end of a slot holds no datagram.
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

def _new_ready_hub(body_dir:'str') -> 'HubUnderTest':
    out = HubUnderTest(body_dir)

    out.report_ready(_config_slot)
    out.report_ready(_worker_slot)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_forwarded_invocation_reaches_the_config_process_with_its_origin(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Forward, {'name': 'zato.ping'}, 'cid-1')

    message = test.receive(_config_slot)

    assert message.type == MessageType.Forward
    assert message.slot == _worker_slot
    assert message.cid == 'cid-1'
    assert message.body == {'name': 'zato.ping'}

    assert test.has_nothing(_worker_slot)

# ################################################################################################################################

def test_the_result_of_a_forward_follows_the_events_of_its_change(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Forward, {'name': 'zato.security.basic-auth.create'}, 'cid-1')
    _ = test.receive(_config_slot)

    # The config process commits the change, publishes its event and then returns the result ..
    test.send(_config_slot, MessageType.Event, {'action': 'change'})
    test.send(_config_slot, MessageType.Forward_Result, {'payload': 'out'}, 'cid-1', _worker_slot)

    # .. so the worker receives the event before the result ..
    event = test.receive(_worker_slot)
    result = test.receive(_worker_slot)

    assert event.type == MessageType.Event
    assert event.slot == _config_slot
    assert event.body == {'action': 'change'}

    assert result.type == MessageType.Forward_Result
    assert result.cid == 'cid-1'
    assert result.body == {'payload': 'out'}

    # .. and the config process receives nothing of its own.
    assert test.has_nothing(_worker_slot)
    assert test.has_nothing(_config_slot)

# ################################################################################################################################

def test_a_forward_without_a_config_process_fails_at_once(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))
    test.close(_config_slot)

    test.send(_worker_slot, MessageType.Forward, {'name': 'zato.ping'}, 'cid-1')

    result = test.receive(_worker_slot)

    assert result.type == MessageType.Forward_Result
    assert result.cid == 'cid-1'
    assert result.body['error']['message'] == ConfigRouteCtx.Config_Unavailable

# ################################################################################################################################

def test_the_forwards_of_a_terminated_config_process_fail_to_the_worker(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Forward, {'name': 'a'}, 'cid-0')
    test.send(_worker_slot, MessageType.Forward, {'name': 'b'}, 'cid-1')

    _ = test.receive(_config_slot)
    _ = test.receive(_config_slot)

    test.close(_config_slot)

    result_0 = test.receive(_worker_slot)
    result_1 = test.receive(_worker_slot)

    assert result_0.cid == 'cid-0'
    assert result_1.cid == 'cid-1'

    assert result_0.body['error']['message'] == ConfigRouteCtx.Config_Unavailable
    assert result_1.body['error']['message'] == ConfigRouteCtx.Config_Unavailable

# ################################################################################################################################

def test_the_result_for_a_terminated_worker_is_discarded(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Forward, {'name': 'a'}, 'cid-0')
    _ = test.receive(_config_slot)

    test.close(_worker_slot)

    # The config process learns of the termination, and the result it sends afterwards reaches no one.
    gone = test.receive(_config_slot)

    assert gone.type == MessageType.Worker_Gone
    assert gone.body == _worker_slot

    test.send(_config_slot, MessageType.Forward_Result, {'payload': 'out'}, 'cid-0', _worker_slot)

    assert test.hub.config_route.forwards == {}
    assert test.has_nothing(_config_slot)

# ################################################################################################################################

def test_the_mark_discards_the_events_held_for_a_starting_worker(tmp_path:'Path') -> 'None':
    test = HubUnderTest(str(tmp_path))
    test.report_ready(_config_slot)

    # An event published before the mark is held for the starting worker ..
    test.send(_config_slot, MessageType.Event, 'before-mark')

    test.send(_worker_slot, MessageType.Load_Request, None, 'load-1')
    request = test.receive(_config_slot)

    assert request.type == MessageType.Load_Request
    assert request.slot == _worker_slot
    assert request.cid == 'load-1'

    # .. the mark reaches the starting worker at once ..
    test.send(_config_slot, MessageType.Mark, None, 'load-1', _worker_slot)

    mark = test.receive(_worker_slot)

    assert mark.type == MessageType.Mark
    assert mark.cid == 'load-1'

    # .. an event published after the mark is held as well ..
    test.send(_config_slot, MessageType.Event, 'after-mark')

    assert test.has_nothing(_worker_slot)

    # .. and once the worker is ready, it receives only what its load did not contain.
    test.report_ready(_worker_slot)

    event = test.receive(_worker_slot)

    assert event.body == 'after-mark'
    assert test.has_nothing(_worker_slot)

# ################################################################################################################################

def test_a_mark_of_another_request_is_not_delivered(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Load_Request, None, 'load-new')
    _ = test.receive(_config_slot)

    test.send(_config_slot, MessageType.Mark, None, 'load-old', _worker_slot)

    assert test.has_nothing(_worker_slot)

    test.send(_config_slot, MessageType.Mark, None, 'load-new', _worker_slot)

    mark = test.receive(_worker_slot)
    assert mark.cid == 'load-new'

# ################################################################################################################################

def test_the_load_report_reaches_the_config_process(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Load_Request, None, 'load-0')
    _ = test.receive(_config_slot)

    test.send(_config_slot, MessageType.Mark, None, 'load-0', _worker_slot)
    _ = test.receive(_worker_slot)

    test.send(_worker_slot, MessageType.Load_Done, None, 'load-0')

    done = test.receive(_config_slot)

    assert done.type == MessageType.Load_Done
    assert done.slot == _worker_slot
    assert done.cid == 'load-0'

    assert test.hub.config_route.loading == {}

# ################################################################################################################################

def test_a_replacement_config_process_receives_the_load_in_progress_first(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    # The worker received its mark and has not reported its load ..
    test.send(_worker_slot, MessageType.Load_Request, None, 'load-0')
    _ = test.receive(_config_slot)

    test.send(_config_slot, MessageType.Mark, None, 'load-0', _worker_slot)
    _ = test.receive(_worker_slot)

    # .. when the config process terminates ..
    test.close(_config_slot)

    # .. and its replacement receives the load before anything else, once it reports ready.
    test.open(_config_slot)
    test.send(_worker_slot, MessageType.Event, 'event-of-worker')

    assert test.has_nothing(_config_slot)

    test.send(_config_slot, MessageType.Ready, None)

    state = test.receive(_config_slot)
    event = test.receive(_config_slot)

    assert state.type == MessageType.Loading_State
    assert state.body == [[_worker_slot, 'load-0']]

    assert event.type == MessageType.Event
    assert event.body == 'event-of-worker'

# ################################################################################################################################

def test_a_replacement_config_process_receives_the_request_not_served_first(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    # The config process terminates before it serves the load request of the worker ..
    test.send(_worker_slot, MessageType.Load_Request, None, 'load-0')
    _ = test.receive(_config_slot)

    test.close(_config_slot)

    # .. and its replacement receives the request before anything else, once it reports ready.
    test.open(_config_slot)
    test.send(_worker_slot, MessageType.Event, 'event-of-worker')

    test.report_ready(_config_slot)

    request = test.receive(_config_slot)
    event = test.receive(_config_slot)

    assert request.type == MessageType.Load_Request
    assert request.slot == _worker_slot
    assert request.cid == 'load-0'

    assert event.type == MessageType.Event
    assert event.body == 'event-of-worker'

# ################################################################################################################################

def test_a_terminated_worker_releases_its_load(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_worker_slot, MessageType.Load_Request, None, 'load-0')
    _ = test.receive(_config_slot)

    test.close(_worker_slot)

    gone = test.receive(_config_slot)

    assert gone.type == MessageType.Worker_Gone
    assert gone.body == _worker_slot

    assert test.hub.config_route.requested == {}
    assert test.hub.config_route.loading == {}

# ################################################################################################################################

def test_the_config_process_receives_no_reload(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.hub.broadcast_reload()

    message = test.receive(_worker_slot)

    assert message.type == MessageType.Reload
    assert test.has_nothing(_config_slot)

# ################################################################################################################################

def test_a_reload_requested_by_the_config_process_reaches_the_worker(tmp_path:'Path') -> 'None':
    test = _new_ready_hub(str(tmp_path))

    test.send(_config_slot, MessageType.Reload, None)

    message = test.receive(_worker_slot)

    assert message.type == MessageType.Reload
    assert test.has_nothing(_config_slot)

# ################################################################################################################################
# ################################################################################################################################
