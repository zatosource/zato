# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The publish lock and the name mark of the queue of each outgoing connection, shared by the worker and the config process
# of one server. The arbiter binds each of them to the region of the server after the fork. The publish lock is the keyed
# lock of the sub key of a queue, which one greenlet of one process holds at a time, the two processes taking turns
# in the order in which they asked for it. The config process, which holds a queue still while the worker delivers it,
# has the worker pause that delivery through a query of the control channel, and resume it once the hold ends.
# The counter of the keyed lock of each sub key holds the mark of the current name of the connection, which the config
# process sets under the publish lock when it renames or deletes the connection, and against which the worker checks
# the name in its own configuration before it publishes.

# stdlib
from dataclasses import dataclass
from hashlib import blake2b
from logging import getLogger

# gevent
from gevent import spawn
from gevent.event import Event
from gevent.lock import RLock
from gevent.socket import wait_read

# Zato
from zato.common.typing_ import cast_
from zato.common.worker_slot import is_config_process
from zato.server.control.hub import EntryStatus, ModuleCtx as HubCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import any_, stranydict
    from zato.server.base.parallel.delivery import PushDelivery
    from zato.server.control.client import ControlClient
    from zato_ipc_core.zato_ipc_core import SharedRegion

    any_ = any_
    ControlClient = ControlClient
    Greenlet = Greenlet
    PushDelivery = PushDelivery
    SharedRegion = SharedRegion
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Key_Action = 'action'
    Key_Sub_Key = 'sub_key'

    Action_Pause = 'outgoing.pause'
    Action_Resume = 'outgoing.resume'

    # How long the worker waits for the round in flight before it confirms a pause that the config process
    # asked for, which stays below the deadline of the query that carries the request
    Relay_Join_Share = 0.6
    Relay_Join_Timeout = HubCtx.Query_Timeout * Relay_Join_Share

    # The mark of a name is its digest of this many bytes, which stays below the range of the counter, plus this offset,
    # so that no mark equals the value of a counter that no process has set
    Name_Mark_Digest_Size = 7
    Name_Mark_Offset = 1

    # The value of the counter of a queue whose connection was never renamed, or was deleted, which every name matches
    Name_Mark_Unset = 0

# ################################################################################################################################
# ################################################################################################################################

class OutgoingHoldError(Exception):
    """ The worker did not confirm that it paused the delivery of a queue.
    """

# ################################################################################################################################
# ################################################################################################################################

class LockWaker:
    """ Wakes the greenlets of one process that wait for a keyed lock, each time the other process passes the turn
    of a keyed lock to the place of this one. A waiter takes the event of the next wake-up before it polls its lock,
    so a wake-up that arrives between the poll and the wait sets the event that the waiter waits on.
    """

    def __init__(self, region:'SharedRegion', place:'int') -> 'None':
        self.region = region
        self.place = place
        self.wake_fd = region.lock_wake_fd(place)
        self.event = Event()

# ################################################################################################################################

    def start(self) -> 'Greenlet':
        """ Starts the greenlet that reads the wake-up descriptor of the place and returns it.
        """
        out = spawn(self._run)
        return out

# ################################################################################################################################

    def _run(self) -> 'None':

        while True:
            wait_read(self.wake_fd)
            _ = self.region.lock_drain(self.place)

            # Each wake-up sets the event that every current waiter holds, and later waiters take a new one
            event = self.event
            self.event = Event()
            event.set()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutgoingBinding:
    """ The region of the server of a process, the place of the process, the waker of its lock waiters,
    and the control client through which the config process asks the worker to pause the delivery of a queue.
    """
    region: 'SharedRegion'
    place: 'int'
    waker: 'LockWaker'
    waker_greenlet: 'Greenlet'
    client: 'ControlClient'

# ################################################################################################################################

class OutgoingState:
    binding: 'OutgoingBinding | None' = None

_state = OutgoingState()

# ################################################################################################################################
# ################################################################################################################################

def bind_outgoing(region:'SharedRegion', place:'int') -> 'None':
    """ Gives this process the region of its server for the publish locks and the name marks of the outgoing queues,
    under the place of the worker or that of the config process.
    """
    binding = OutgoingBinding()
    binding.region = region
    binding.place = place
    binding.waker = LockWaker(region, place)
    binding.waker_greenlet = binding.waker.start()

    _state.binding = binding

# ################################################################################################################################

def bind_outgoing_control(client:'ControlClient') -> 'None':
    """ Gives the binding of this process its control client, once the process created it.
    """
    binding = cast_('OutgoingBinding', _state.binding)
    binding.client = client

# ################################################################################################################################

def get_outgoing_binding() -> 'OutgoingBinding | None':
    """ Returns the binding of this process, which a process that no arbiter started does not have.
    """
    out = _state.binding
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_name_mark(conn_name:'str') -> 'int':
    digest = blake2b(conn_name.encode('utf8'), digest_size=ModuleCtx.Name_Mark_Digest_Size).digest()
    out = int.from_bytes(digest) + ModuleCtx.Name_Mark_Offset
    return out

# ################################################################################################################################
# ################################################################################################################################

class SharedNameMark:
    """ The mark of the current name of the connection of each outgoing queue, by sub key, across both processes of the server.
    A queue whose connection was never renamed has no mark, which every name matches, and the deletion of a connection
    clears its mark, because a new connection may receive the id and with it the sub key of the deleted one.
    """

    def __init__(self, binding:'OutgoingBinding') -> 'None':
        self.region = binding.region

# ################################################################################################################################

    def _set(self, sub_key:'str', mark:'int') -> 'None':
        """ Sets the mark of one queue, which only the holder of the publish lock of the queue changes.
        """
        entry = self.region.lock_entry(sub_key)
        current = self.region.lock_counter(entry)
        _ = self.region.lock_counter_replace(entry, current, mark)

# ################################################################################################################################

    def set_name(self, sub_key:'str', conn_name:'str') -> 'None':
        """ The connection of this queue is now called by this name.
        """
        self._set(sub_key, _get_name_mark(conn_name))

# ################################################################################################################################

    def clear(self, sub_key:'str') -> 'None':
        """ The connection of this queue no longer exists.
        """
        self._set(sub_key, ModuleCtx.Name_Mark_Unset)

# ################################################################################################################################

    def is_current(self, sub_key:'str', conn_name:'str') -> 'bool':
        """ Whether the connection of this queue is still called by this name.
        """
        entry = self.region.lock_entry(sub_key)
        mark = self.region.lock_counter(entry)

        out = mark == ModuleCtx.Name_Mark_Unset or mark == _get_name_mark(conn_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class SharedPublishLock:
    """ The publish lock of the queue of one outgoing connection, which one greenlet of one process holds at a time.
    The lock of this process orders its greenlets and lets the holder enter again, and the greenlet that enters first
    also takes the keyed lock of the region, which orders the worker and the config process.
    """

    def __init__(self, binding:'OutgoingBinding', sub_key:'str') -> 'None':
        self.region = binding.region
        self.place = binding.place
        self.waker = binding.waker
        self.entry = binding.region.lock_entry(sub_key)

        self.local_lock = RLock()
        self.hold_count = 0

# ################################################################################################################################

    def _take(self) -> 'None':
        """ Takes the keyed lock of the region, waiting for the turn of this place.
        """
        _ = self.region.lock_enter(self.entry, self.place)

        try:
            while True:

                # The event is taken before the poll, so a turn that passes to this place after the poll sets it
                event = self.waker.event

                if self.region.lock_poll(self.entry, self.place):
                    break

                _ = event.wait()

        # A waiter that is stopped withdraws its ticket, so the lock passes on to the next one
        except BaseException:
            self.region.lock_abandon(self.entry, self.place)
            raise

# ################################################################################################################################

    def __enter__(self) -> 'None':
        _ = self.local_lock.acquire()
        self.hold_count += 1

        # Only the outermost entry of the holder takes the lock of the region ..
        if self.hold_count == 1:
            try:
                self._take()
            except BaseException:
                self.hold_count -= 1
                self.local_lock.release()
                raise

# ################################################################################################################################

    def __exit__(self, *_:'any_') -> 'None':
        self.hold_count -= 1

        # .. and only its exit releases it.
        if self.hold_count == 0:
            self.region.lock_release(self.entry, self.place)

        self.local_lock.release()

# ################################################################################################################################
# ################################################################################################################################

def _relay(binding:'OutgoingBinding', action:'str', sub_key:'str') -> 'stranydict':
    """ Sends an action on the delivery of a queue to the worker and returns its result.
    """
    body = {
        ModuleCtx.Key_Action: action,
        ModuleCtx.Key_Sub_Key: sub_key,
    }

    out = binding.client.query(body)
    return out

# ################################################################################################################################

def pause_outgoing_delivery(delivery:'PushDelivery', sub_key:'str') -> 'None':
    """ Stops the delivery of a queue between two of its rounds, in this process if it is the worker,
    or in the worker, which confirms once the round in flight completed.
    """
    binding = _state.binding

    if binding is None or not is_config_process():
        delivery.pause_sub_key(sub_key)
        return

    result = _relay(binding, ModuleCtx.Action_Pause, sub_key)
    status = result['status']

    # A worker that did not confirm may pause later, so it is asked to resume before the hold fails
    if status != EntryStatus.OK:
        _ = _relay(binding, ModuleCtx.Action_Resume, sub_key)
        raise OutgoingHoldError(f'The worker did not confirm the pause of `{sub_key}`, status `{status}`')

# ################################################################################################################################

def resume_outgoing_delivery(delivery:'PushDelivery', sub_key:'str') -> 'None':
    """ Starts the delivery of a queue again, in this process if it is the worker, or in the worker.
    """
    binding = _state.binding

    if binding is None or not is_config_process():
        delivery.resume_sub_key(sub_key)
        return

    result = _relay(binding, ModuleCtx.Action_Resume, sub_key)
    status = result['status']

    if status != EntryStatus.OK:
        logger.warning('The worker did not confirm the resumption of `%s`, status `%s`', sub_key, status)

# ################################################################################################################################

def handle_outgoing_query(delivery:'PushDelivery', body:'stranydict') -> 'None':
    """ Applies an action on the delivery of a queue that the config process sent to the worker.
    """
    sub_key = body[ModuleCtx.Key_Sub_Key]

    if body[ModuleCtx.Key_Action] == ModuleCtx.Action_Pause:
        delivery.pause_sub_key(sub_key, join_timeout=ModuleCtx.Relay_Join_Timeout)
    else:
        delivery.resume_sub_key(sub_key)

# ################################################################################################################################
# ################################################################################################################################
