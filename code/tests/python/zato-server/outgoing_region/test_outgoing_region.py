# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from multiprocessing import get_context
from threading import RLock
from types import SimpleNamespace

# gevent
import gevent
import pytest

# Zato
from zato.common.pubsub import outgoing as pubsub_outgoing
from zato.common.pubsub.outgoing import get_outgoing_sub_key
from zato.common.pubsub.ownership import get_owner_slot
from zato.common.typing_ import cast_
from zato.server.base.config_manager.outgoing_dlq import OutgoingDLQs
from zato.server.base.config_manager.outgoing_queues import OutgoingQueueDepth, OutgoingQueues
from zato.server.control.hub import EntryStatus
from zato.server.outgoing_region import _state, bind_outgoing, bind_outgoing_control, get_outgoing_binding, LockWaker, \
    ModuleCtx as RegionCtx, OutgoingBinding, OutgoingHoldError, pause_outgoing_delivery, resume_outgoing_delivery, \
    handle_outgoing_query, SharedPublishLock, SharedQueueDepth
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anylist, anytuple, callable_, generator_, list_, stranydict, strlist
    from zato.server.base.parallel.delivery import PushDelivery
    from zato.server.control.client import ControlClient

    any_ = any_
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    ControlClient = ControlClient
    Path = Path
    PushDelivery = PushDelivery
    stranydict = stranydict
    strlist = strlist

    bindinglist = list_[OutgoingBinding]
    bindinggen = generator_[bindinglist, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Count = 2

    Region_Config = {
        'slot_count': Slot_Count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 1,
        'metric_count': 0,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 8,
        'start_id': 1,
    }

    Conn_Type = 'outconn-rest'
    Conn_ID = 1
    Conn_Name = 'crm.orders'

    # The counts of the startup of the tests
    Startup_Depth = 5
    Later_Startup_Depth = 9

    # How long a holder of a lock keeps it while another greenlet waits, in seconds
    Hold_Seconds = 0.05

    # How long a test waits for a greenlet or a process, in seconds
    Wait_Seconds = 10.0

    # How many times each process of the concurrency test takes the lock
    Round_Count = 200

_sub_key = get_outgoing_sub_key(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID)
_owner_slot = get_owner_slot(_sub_key, ModuleCtx.Slot_Count)
_other_slot = 1 - _owner_slot

_fork_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

class FakeFence:
    def __init__(self, slot:'int') -> 'None':
        self.slot = slot

    def owns(self, sub_key:'str') -> 'bool':
        out = get_owner_slot(sub_key, ModuleCtx.Slot_Count) == self.slot
        return out

# ################################################################################################################################

class FakeDelivery:
    """ The delivery of one worker, which records the pauses and resumptions it receives.
    """
    def __init__(self, slot:'int') -> 'None':
        self.fence = FakeFence(slot)
        self.calls:'anylist' = []

    def pause_sub_key(self, sub_key:'str', join_timeout:'float'=0.0) -> 'None':
        self.calls.append(('pause', sub_key, join_timeout))

    def resume_sub_key(self, sub_key:'str') -> 'None':
        self.calls.append(('resume', sub_key))

# ################################################################################################################################

class FakeClient:
    """ The control client of a worker, which sends each query to the delivery of every slot, as the arbiter relays it.
    """
    def __init__(self, deliveries:'list_[FakeDelivery]', owner_status:'str') -> 'None':
        self.deliveries = deliveries
        self.owner_status = owner_status
        self.bodies:'anylist' = []

    def query(self, body:'stranydict') -> 'anylist':
        self.bodies.append(body)
        out:'anylist' = []

        for slot, delivery in enumerate(self.deliveries):
            response = handle_outgoing_query(cast_('PushDelivery', delivery), body)
            status = self.owner_status if slot == _owner_slot else EntryStatus.OK

            out.append({'slot': slot, 'status': status, 'body': response})

        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_binding(region:'SharedRegion', slot:'int') -> 'OutgoingBinding':
    """ The binding of a worker of another slot, which the tests create in this process.
    """
    out = OutgoingBinding()
    out.region = region
    out.slot = slot
    out.waker = LockWaker(region, slot)
    out.waker_greenlet = out.waker.start()

    return out

# ################################################################################################################################

def _new_config_manager(delivery:'FakeDelivery') -> 'OutgoingQueues':
    server = SimpleNamespace(pubsub_push_delivery=delivery)

    out = OutgoingQueues.__new__(OutgoingQueues)
    out.server = server # type: ignore[assignment]
    out.init_outgoing_dlqs = lambda: None
    out.init_outgoing_queues()

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def region() -> 'SharedRegion':
    out = SharedRegion(ModuleCtx.Region_Config)
    return out

# ################################################################################################################################

@pytest.fixture
def bindings(region:'SharedRegion') -> 'bindinggen':
    """ Binds this process to the slot of the owner of the queue, and returns that binding and the binding
    of the worker of the other slot.
    """
    bind_outgoing(region, _owner_slot)

    owner = cast_('OutgoingBinding', get_outgoing_binding())
    other = _new_binding(region, _other_slot)

    yield [owner, other]

    owner.waker_greenlet.kill()
    other.waker_greenlet.kill()
    _state.binding = None

# ################################################################################################################################

def _bind_as(binding:'OutgoingBinding') -> 'None':
    _state.binding = binding

# ################################################################################################################################
# ################################################################################################################################

def test_an_unbound_process_keeps_its_own_depth_and_lock() -> 'None':
    config_manager = _new_config_manager(FakeDelivery(_owner_slot))
    lock = config_manager.get_outgoing_publish_lock(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID)

    assert type(config_manager.outgoing_queue_depth) is OutgoingQueueDepth
    assert type(lock) is type(RLock())

# ################################################################################################################################

def test_the_depth_is_shared_by_the_workers(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    owner, other = bindings

    config_manager = _new_config_manager(FakeDelivery(_owner_slot))
    depth = config_manager.outgoing_queue_depth

    assert type(depth) is SharedQueueDepth

    # One worker raises the depth twice, and the other lowers it once ..
    depth.raise_(_sub_key)
    depth.raise_(_sub_key)

    other_depth = SharedQueueDepth(other)
    other_depth.lower(_sub_key, 1)

    # .. and both read the same value, which the region holds.
    assert depth.get(_sub_key) == 1
    assert other_depth.get(_sub_key) == 1
    assert region.lock_counter(region.lock_entry(_sub_key)) == 1

    assert owner.slot == _owner_slot

# ################################################################################################################################

class _QueueListManager(OutgoingQueues, OutgoingDLQs):
    """ The outgoing queues and the DLQs of a config manager, which the list of the queues reads together.
    """

# ################################################################################################################################

class FakeBackend:

    def get_pending_counts_by_prefix(self, _prefix:'str') -> 'stranydict':
        return {}

# ################################################################################################################################

def _locate_conn(_server:'any_', _conn_id:'int') -> 'anytuple':
    out = (ModuleCtx.Conn_Name, None)
    return out

# ################################################################################################################################

def test_the_queue_list_reports_the_depth_raised_by_another_worker(
    bindings:'bindinglist',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    _, other = bindings

    monkeypatch.setitem(pubsub_outgoing.conn_locators, ModuleCtx.Conn_Type, _locate_conn)
    monkeypatch.setitem(pubsub_outgoing.conn_directions, ModuleCtx.Conn_Type, pubsub_outgoing.Direction_Out)

    config_manager = _QueueListManager.__new__(_QueueListManager)
    config_manager.server = SimpleNamespace(pubsub_push_delivery=FakeDelivery(_owner_slot), pubsub_backend=FakeBackend()) # type: ignore[assignment]
    config_manager.init_outgoing_dlqs()
    config_manager.init_outgoing_queues()
    config_manager._outgoing_sub_key_cache.add(_sub_key)

    # The worker of the other slot queues three requests ..
    other_depth = SharedQueueDepth(other)

    for _ in range(3):
        other_depth.raise_(_sub_key)

    # .. and the list of the queues in this worker reports them.
    queue_list = config_manager.get_outgoing_queue_list()

    assert len(queue_list) == 1
    assert queue_list[0]['name'] == ModuleCtx.Conn_Name
    assert queue_list[0]['queue_depth'] == 3

# ################################################################################################################################

def test_the_startup_depth_is_set_once(bindings:'bindinglist') -> 'None':
    owner, other = bindings
    used_sub_key = get_outgoing_sub_key(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID + 1)

    first = SharedQueueDepth(owner)
    later = SharedQueueDepth(other)

    # A queue in use since the start keeps its depth when a worker starts later ..
    first.raise_(used_sub_key)

    first.set_counts({_sub_key: ModuleCtx.Startup_Depth, used_sub_key: ModuleCtx.Startup_Depth})
    later.set_counts({_sub_key: ModuleCtx.Later_Startup_Depth})

    # .. and the first worker to start sets the depth of a queue no worker used.
    assert later.get(_sub_key) == ModuleCtx.Startup_Depth
    assert later.get(used_sub_key) == 1

# ################################################################################################################################

def test_the_lock_is_reentrant_and_orders_the_greenlets_of_a_worker(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    owner, _ = bindings

    config_manager = _new_config_manager(FakeDelivery(_owner_slot))
    lock = config_manager.get_outgoing_publish_lock(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID)

    assert type(lock) is SharedPublishLock

    events:'strlist' = []

    def first() -> 'None':
        with lock:
            with lock:
                events.append('first-in')
                gevent.sleep(ModuleCtx.Hold_Seconds)
                events.append('first-out')

    def second() -> 'None':
        with lock:
            events.append('second')

    first_greenlet = gevent.spawn(first)
    gevent.sleep(0)
    second_greenlet = gevent.spawn(second)

    _ = gevent.joinall([first_greenlet, second_greenlet], timeout=ModuleCtx.Wait_Seconds, raise_error=True)

    assert events == ['first-in', 'first-out', 'second']

    # The lock of the region is free again
    entry = region.lock_entry(_sub_key)
    assert not region.lock_has_place(entry, owner.slot)

# ################################################################################################################################

def test_a_worker_waits_for_the_lock_of_another_worker(bindings:'bindinglist') -> 'None':
    owner, other = bindings

    owner_lock = SharedPublishLock(owner, _sub_key)
    other_lock = SharedPublishLock(other, _sub_key)

    events:'strlist' = []

    def hold() -> 'None':
        with owner_lock:
            events.append('owner-in')
            gevent.sleep(ModuleCtx.Hold_Seconds)
            events.append('owner-out')

    def wait() -> 'None':
        with other_lock:
            events.append('other')

    holder = gevent.spawn(hold)
    gevent.sleep(0)
    waiter = gevent.spawn(wait)

    # The waiter of the other slot enters only after the holder released the lock and its descriptor was written to
    _ = gevent.joinall([holder, waiter], timeout=ModuleCtx.Wait_Seconds, raise_error=True)

    assert events == ['owner-in', 'owner-out', 'other']

# ################################################################################################################################

def test_a_stopped_waiter_withdraws_its_ticket(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    owner, other = bindings
    entry = region.lock_entry(_sub_key)

    owner_lock = SharedPublishLock(owner, _sub_key)
    other_lock = SharedPublishLock(other, _sub_key)

    def wait() -> 'None':
        with other_lock:
            pass

    # The waiter of the other slot is stopped while the owner holds the lock ..
    with owner_lock:
        waiter = gevent.spawn(wait)
        gevent.sleep(0)

        assert region.lock_has_place(entry, other.slot)

        waiter.kill()

        assert not region.lock_has_place(entry, other.slot)

    # .. so the next waiter of that slot takes a ticket anew and enters at once.
    entered = gevent.spawn(wait)
    _ = entered.join(timeout=ModuleCtx.Wait_Seconds)

    assert entered.successful()

# ################################################################################################################################

def test_the_owner_pauses_its_own_delivery(bindings:'bindinglist') -> 'None':
    owner_delivery = FakeDelivery(_owner_slot)

    pause_outgoing_delivery(cast_('PushDelivery', owner_delivery), _sub_key)
    resume_outgoing_delivery(cast_('PushDelivery', owner_delivery), _sub_key)

    assert owner_delivery.calls[0][:2] == ('pause', _sub_key)
    assert owner_delivery.calls[1] == ('resume', _sub_key)
    assert bindings[0].slot == _owner_slot

# ################################################################################################################################

def test_another_worker_has_the_owner_pause_its_delivery(bindings:'bindinglist') -> 'None':
    _, other = bindings

    deliveries = [FakeDelivery(slot) for slot in range(ModuleCtx.Slot_Count)]
    client = FakeClient(deliveries, EntryStatus.OK)

    _bind_as(other)
    bind_outgoing_control(cast_('ControlClient', client))

    pause_outgoing_delivery(cast_('PushDelivery', deliveries[other.slot]), _sub_key)

    # The owner paused with the timeout that keeps its answer within the deadline of the query ..
    owner_delivery = deliveries[_owner_slot]
    assert owner_delivery.calls == [('pause', _sub_key, RegionCtx.Relay_Join_Timeout)]

    resume_outgoing_delivery(cast_('PushDelivery', deliveries[other.slot]), _sub_key)

    # .. and resumed once the hold ended.
    assert owner_delivery.calls[-1] == ('resume', _sub_key)
    assert [body[RegionCtx.Key_Action] for body in client.bodies] == [RegionCtx.Action_Pause, RegionCtx.Action_Resume]

# ################################################################################################################################

def test_an_unconfirmed_pause_fails_the_hold(bindings:'bindinglist') -> 'None':
    _, other = bindings

    deliveries = [FakeDelivery(slot) for slot in range(ModuleCtx.Slot_Count)]
    client = FakeClient(deliveries, EntryStatus.Timeout)

    _bind_as(other)
    bind_outgoing_control(cast_('ControlClient', client))

    with pytest.raises(OutgoingHoldError):
        pause_outgoing_delivery(cast_('PushDelivery', deliveries[other.slot]), _sub_key)

    # The owner, which may pause after the deadline, is asked to resume
    assert [body[RegionCtx.Key_Action] for body in client.bodies] == [RegionCtx.Action_Pause, RegionCtx.Action_Resume]

# ################################################################################################################################

def test_a_hold_in_another_worker_pauses_the_owner_under_the_lock(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    owner, other = bindings
    entry = region.lock_entry(_sub_key)

    deliveries = [FakeDelivery(slot) for slot in range(ModuleCtx.Slot_Count)]
    client = FakeClient(deliveries, EntryStatus.OK)

    _bind_as(other)
    bind_outgoing_control(cast_('ControlClient', client))

    config_manager = _new_config_manager(deliveries[other.slot])
    config_manager._outgoing_sub_key_cache.add(_sub_key)

    owner_delivery = deliveries[_owner_slot]

    with config_manager.hold_outgoing_queue(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID):

        # The worker holds the lock of the region, which no publication in the owner can take meanwhile,
        # and the owner paused its delivery ..
        assert region.lock_has_place(entry, other.slot)
        assert owner_delivery.calls == [('pause', _sub_key, RegionCtx.Relay_Join_Timeout)]

    # .. which it resumed once the hold ended, after which the lock is free.
    assert owner_delivery.calls[-1] == ('resume', _sub_key)
    assert not region.lock_has_place(entry, other.slot)
    assert owner.slot == _owner_slot

# ################################################################################################################################
# ################################################################################################################################

def _publish_in_worker(region:'SharedRegion', slot:'int', count_path:'str') -> 'None':
    """ Takes the publish lock of the queue the given number of times, and under it reads, raises and writes back
    a count that the workers share in a file, as well as the depth of the queue.
    """
    gevent.reinit()
    bind_outgoing(region, slot)

    binding = cast_('OutgoingBinding', get_outgoing_binding())
    lock = SharedPublishLock(binding, _sub_key)
    depth = SharedQueueDepth(binding)

    for _ in range(ModuleCtx.Round_Count):
        with lock:
            with open(count_path) as count_file:
                count = int(count_file.read())

            # The other worker runs meanwhile, and only the lock keeps it from reading the same count
            gevent.sleep(0)
            os.sched_yield()

            with open(count_path, 'w') as count_file:
                _ = count_file.write(str(count + 1))

            depth.raise_(_sub_key)

    os._exit(0)

# ################################################################################################################################

def test_the_workers_of_two_processes_take_turns(region:'SharedRegion', tmp_path:'Path') -> 'None':
    count_path = tmp_path / 'count'
    _ = count_path.write_text('0')

    processes = []

    for slot in range(ModuleCtx.Slot_Count):
        process = _fork_context.Process(target=_publish_in_worker, args=(region, slot, str(count_path)))
        process.start()
        processes.append(process)

    for process in processes:
        process.join(ModuleCtx.Wait_Seconds)
        assert process.exitcode == 0

    # Every read, raise and write of each worker happened under the lock, so none of them was lost
    expected = ModuleCtx.Slot_Count * ModuleCtx.Round_Count

    assert int(count_path.read_text()) == expected
    assert region.lock_counter(region.lock_entry(_sub_key)) == expected

# ################################################################################################################################
# ################################################################################################################################
