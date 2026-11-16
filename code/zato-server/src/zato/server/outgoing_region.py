# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The depth and the publish lock of the queue of each outgoing connection, shared by the worker processes of one server.
# The arbiter binds each worker to the region of the server after the fork. The depth of a queue is the counter
# of the keyed lock of its sub key, and the publish lock is that keyed lock, which one greenlet of one worker holds
# at a time, the workers taking turns in the order in which they asked for it. A worker that holds a queue still
# while the worker of another slot owns its delivery has the owner pause that delivery through a query of the control
# channel, and resume it once the hold ends. The counter of a second keyed entry of each sub key holds the mark
# of the current name of the connection, which the config process sets under the publish lock when it renames or deletes
# the connection, and against which a worker checks the name in its own configuration before it publishes.

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
from zato.common.pubsub.ownership import get_owner_slot
from zato.common.typing_ import cast_
from zato.server.control.hub import EntryStatus, ModuleCtx as HubCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.server.base.parallel.delivery import PushDelivery
    from zato.server.control.client import ControlClient
    from zato_ipc_core.zato_ipc_core import SharedRegion

    any_ = any_
    anydict = anydict
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
    Key_Is_Owner = 'is_owner'

    Action_Pause = 'outgoing.pause'
    Action_Resume = 'outgoing.resume'

    # How long the owner of a queue waits for the round in flight before it confirms a pause that another worker
    # asked for, which stays below the deadline of the query that carries the request
    Relay_Join_Share = 0.6
    Relay_Join_Timeout = HubCtx.Query_Timeout * Relay_Join_Share

    # The keyed entry of the name mark of a sub key is the sub key followed by this suffix
    Name_Mark_Suffix = '.name-mark'

    # The mark of a name is its digest of this many bytes, which stays below the range of the counter, plus this offset,
    # so that no mark equals the value of a counter that no process has set
    Name_Mark_Digest_Size = 7
    Name_Mark_Offset = 1

    # The value of the counter of a queue whose connection was never renamed, or was deleted, which every name matches
    Name_Mark_Unset = 0

# ################################################################################################################################
# ################################################################################################################################

class OutgoingHoldError(Exception):
    """ The worker that owns the delivery of a queue did not confirm that it paused that delivery.
    """

# ################################################################################################################################
# ################################################################################################################################

class LockWaker:
    """ Wakes the greenlets of one worker that wait for a keyed lock, each time a worker passes the turn of a keyed lock
    to the slot of this one. A waiter takes the event of the next wake-up before it polls its lock, so a wake-up that
    arrives between the poll and the wait sets the event that the waiter waits on.
    """

    def __init__(self, region:'SharedRegion', slot:'int') -> 'None':
        self.region = region
        self.slot = slot
        self.wake_fd = region.lock_wake_fd(slot)
        self.event = Event()

# ################################################################################################################################

    def start(self) -> 'Greenlet':
        """ Starts the greenlet that reads the wake-up descriptor of the slot and returns it.
        """
        out = spawn(self._run)
        return out

# ################################################################################################################################

    def _run(self) -> 'None':

        while True:
            wait_read(self.wake_fd)
            _ = self.region.lock_drain(self.slot)

            # Each wake-up sets the event that every current waiter holds, and later waiters take a new one
            event = self.event
            self.event = Event()
            event.set()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutgoingBinding:
    """ The region of the server of a worker, the slot of the worker, the waker of its lock waiters,
    and the control client through which it asks the owner of a queue to pause its delivery.
    """
    region: 'SharedRegion'
    slot: 'int'
    waker: 'LockWaker'
    waker_greenlet: 'Greenlet'
    client: 'ControlClient'

# ################################################################################################################################

class OutgoingState:
    binding: 'OutgoingBinding | None' = None

_state = OutgoingState()

# ################################################################################################################################
# ################################################################################################################################

def bind_outgoing(region:'SharedRegion', slot:'int') -> 'None':
    """ Gives this process the region of its server for the depths, the publish locks and the name marks
    of the outgoing queues, under the slot of a worker or the place of the config process.
    """
    binding = OutgoingBinding()
    binding.region = region
    binding.slot = slot
    binding.waker = LockWaker(region, slot)
    binding.waker_greenlet = binding.waker.start()

    _state.binding = binding

# ################################################################################################################################

def bind_outgoing_control(client:'ControlClient') -> 'None':
    """ Gives the binding of this process the control client of the worker, once the worker created it.
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

class SharedQueueDepth:
    """ How many messages wait in the queue of each outgoing connection, by sub key, across every worker of the server.
    """

    def __init__(self, binding:'OutgoingBinding') -> 'None':
        self.region = binding.region

# ################################################################################################################################

    def get(self, sub_key:'str') -> 'int':
        """ How many messages wait in one queue.
        """
        entry = self.region.lock_entry(sub_key)
        out = self.region.lock_counter(entry)
        return out

# ################################################################################################################################

    def raise_(self, sub_key:'str') -> 'None':
        """ One more message waits in this queue.
        """
        entry = self.region.lock_entry(sub_key)
        _ = self.region.lock_counter_add(entry, 1)

# ################################################################################################################################

    def lower(self, sub_key:'str', count:'int') -> 'None':
        """ That many messages left this queue.
        """
        entry = self.region.lock_entry(sub_key)
        _ = self.region.lock_counter_add(entry, -count)

# ################################################################################################################################

    def set_counts(self, counts:'anydict') -> 'None':
        """ Sets the counts read from the database at startup, each of which the first worker to start sets
        and no worker sets over a depth that a worker changed already.
        """
        for sub_key, count in counts.items():
            entry = self.region.lock_entry(sub_key)
            _ = self.region.lock_counter_init(entry, count)

# ################################################################################################################################
# ################################################################################################################################

def _get_name_mark(conn_name:'str') -> 'int':
    digest = blake2b(conn_name.encode('utf8'), digest_size=ModuleCtx.Name_Mark_Digest_Size).digest()
    out = int.from_bytes(digest) + ModuleCtx.Name_Mark_Offset
    return out

# ################################################################################################################################
# ################################################################################################################################

class SharedNameMark:
    """ The mark of the current name of the connection of each outgoing queue, by sub key, across every process of the server.
    A queue whose connection was never renamed has no mark, which every name matches, and the deletion of a connection
    clears its mark, because a new connection may receive the id and with it the sub key of the deleted one.
    """

    def __init__(self, binding:'OutgoingBinding') -> 'None':
        self.region = binding.region

# ################################################################################################################################

    def _set(self, sub_key:'str', mark:'int') -> 'None':
        """ Sets the mark of one queue, which only the holder of the publish lock of the queue changes.
        """
        entry = self.region.lock_entry(sub_key + ModuleCtx.Name_Mark_Suffix)
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
        entry = self.region.lock_entry(sub_key + ModuleCtx.Name_Mark_Suffix)
        mark = self.region.lock_counter(entry)

        out = mark == ModuleCtx.Name_Mark_Unset or mark == _get_name_mark(conn_name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class SharedPublishLock:
    """ The publish lock of the queue of one outgoing connection, which one greenlet of one worker holds at a time.
    The lock of this process orders the greenlets of the worker and lets the holder enter again, and the greenlet
    that enters first also takes the keyed lock of the region, which orders the workers.
    """

    def __init__(self, binding:'OutgoingBinding', sub_key:'str') -> 'None':
        self.region = binding.region
        self.slot = binding.slot
        self.waker = binding.waker
        self.entry = binding.region.lock_entry(sub_key)

        self.local_lock = RLock()
        self.hold_count = 0

# ################################################################################################################################

    def _take(self) -> 'None':
        """ Takes the keyed lock of the region, waiting for the turn of this slot.
        """
        _ = self.region.lock_enter(self.entry, self.slot)

        try:
            while True:

                # The event is taken before the poll, so a turn that passes to this slot after the poll sets it
                event = self.waker.event

                if self.region.lock_poll(self.entry, self.slot):
                    break

                _ = event.wait()

        # A waiter that is stopped withdraws its ticket, so the lock passes on to the next one
        except BaseException:
            self.region.lock_abandon(self.entry, self.slot)
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
            self.region.lock_release(self.entry, self.slot)

        self.local_lock.release()

# ################################################################################################################################
# ################################################################################################################################

def _is_local_owner(binding:'OutgoingBinding', sub_key:'str') -> 'bool':
    owner_slot = get_owner_slot(sub_key, binding.region.slot_count)
    out = owner_slot == binding.slot
    return out

# ################################################################################################################################

def _relay(binding:'OutgoingBinding', action:'str', sub_key:'str') -> 'stranydict':
    """ Sends an action on the delivery of a queue to every worker and returns the entry of the owner of the queue.
    """
    owner_slot = get_owner_slot(sub_key, binding.region.slot_count)

    body = {
        ModuleCtx.Key_Action: action,
        ModuleCtx.Key_Sub_Key: sub_key,
    }

    # The result holds one entry for each slot, in the order of the slots
    entries = binding.client.query(body)
    out = entries[owner_slot]

    return out

# ################################################################################################################################

def pause_outgoing_delivery(delivery:'PushDelivery', sub_key:'str') -> 'None':
    """ Stops the delivery of a queue between two of its rounds, in this worker if it owns the queue,
    or in its owner, which confirms once the round in flight completed.
    """
    binding = _state.binding

    if binding is None or _is_local_owner(binding, sub_key):
        delivery.pause_sub_key(sub_key)
        return

    entry = _relay(binding, ModuleCtx.Action_Pause, sub_key)
    status = entry['status']

    # An owner that did not confirm may pause later, so it is asked to resume before the hold fails
    if status != EntryStatus.OK:
        _ = _relay(binding, ModuleCtx.Action_Resume, sub_key)
        raise OutgoingHoldError(f'Worker of slot {entry["slot"]} did not confirm the pause of `{sub_key}`, status `{status}`')

# ################################################################################################################################

def resume_outgoing_delivery(delivery:'PushDelivery', sub_key:'str') -> 'None':
    """ Starts the delivery of a queue again, in this worker if it owns the queue, or in its owner.
    """
    binding = _state.binding

    if binding is None or _is_local_owner(binding, sub_key):
        delivery.resume_sub_key(sub_key)
        return

    entry = _relay(binding, ModuleCtx.Action_Resume, sub_key)
    status = entry['status']

    if status != EntryStatus.OK:
        logger.warning('Worker of slot %s did not confirm the resumption of `%s`, status `%s`', entry['slot'], sub_key, status)

# ################################################################################################################################

def handle_outgoing_query(delivery:'PushDelivery', body:'stranydict') -> 'stranydict':
    """ Applies an action on the delivery of a queue that a worker sent to every worker, which changes the delivery
    of the owner of the queue only, and returns whether this worker owns the queue.
    """
    sub_key = body[ModuleCtx.Key_Sub_Key]

    if body[ModuleCtx.Key_Action] == ModuleCtx.Action_Pause:
        delivery.pause_sub_key(sub_key, join_timeout=ModuleCtx.Relay_Join_Timeout)
    else:
        delivery.resume_sub_key(sub_key)

    out = {
        ModuleCtx.Key_Is_Owner: delivery.fence.owns(sub_key),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
