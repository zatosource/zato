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
from zato.common import worker_slot as worker_slot_module
from zato.common.pubsub.outgoing import get_outgoing_sub_key
from zato.common.typing_ import cast_
from zato.server.base.config_manager.outgoing_queues import OutgoingNameMark, OutgoingQueues
from zato.server.control.hub import EntryStatus, new_entry
from zato.server.outgoing_region import _state, bind_outgoing, bind_outgoing_control, get_outgoing_binding, LockWaker, \
    ModuleCtx as RegionCtx, OutgoingBinding, OutgoingHoldError, pause_outgoing_delivery, resume_outgoing_delivery, \
    handle_outgoing_query, SharedNameMark, SharedPublishLock
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import anydict, anylist, generator_, list_, stranydict, strlist
    from zato.server.base.parallel.delivery import PushDelivery
    from zato.server.control.client import ControlClient

    anydict = anydict
    anylist = anylist
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

    Region_Config = {
        'queue_count': 1,
        'lock_capacity': 8,
    }

    # The places of the worker and of the config process
    Worker_Place = 0
    Config_Place = 1

    Conn_Type = 'outconn-rest'
    Conn_ID = 1

    Old_Name = 'crm.orders'
    New_Name = 'crm.orders.v2'

    # How long a holder of a lock keeps it while another greenlet waits, in seconds
    Hold_Seconds = 0.05

    # How long a test waits for a greenlet or a process, in seconds
    Wait_Seconds = 10.0

    # How many times each process of the concurrency test takes the lock
    Round_Count = 200

_sub_key = get_outgoing_sub_key(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID)

_fork_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

class FakeDelivery:
    """ The delivery of the worker, which records the pauses and resumptions it receives.
    """
    def __init__(self) -> 'None':
        self.calls:'anylist' = []

    def pause_sub_key(self, sub_key:'str', join_timeout:'float'=0.0) -> 'None':
        self.calls.append(('pause', sub_key, join_timeout))

    def resume_sub_key(self, sub_key:'str') -> 'None':
        self.calls.append(('resume', sub_key))

# ################################################################################################################################

class FakeClient:
    """ The control client of the config process, which sends each query to the delivery of the worker, as the arbiter relays it.
    """
    def __init__(self, delivery:'FakeDelivery', status:'str') -> 'None':
        self.delivery = delivery
        self.status = status
        self.bodies:'anylist' = []

    def query(self, body:'stranydict') -> 'anydict':
        self.bodies.append(body)
        handle_outgoing_query(cast_('PushDelivery', self.delivery), body)

        out = new_entry(self.status, None)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_binding(region:'SharedRegion', place:'int') -> 'OutgoingBinding':
    """ The binding of the config process, which the tests create in this process.
    """
    out = OutgoingBinding()
    out.region = region
    out.place = place
    out.waker = LockWaker(region, place)
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
    """ Binds this process to the place of the worker, and returns that binding and the binding of the config process.
    """
    bind_outgoing(region, ModuleCtx.Worker_Place)

    worker = cast_('OutgoingBinding', get_outgoing_binding())
    config = _new_binding(region, ModuleCtx.Config_Place)

    yield [worker, config]

    worker.waker_greenlet.kill()
    config.waker_greenlet.kill()
    _state.binding = None

# ################################################################################################################################

def _bind_as_config_process(binding:'OutgoingBinding', client:'FakeClient', monkeypatch:'pytest.MonkeyPatch') -> 'None':
    _state.binding = binding
    bind_outgoing_control(cast_('ControlClient', client))
    monkeypatch.setattr(worker_slot_module, '_slot', worker_slot_module.ModuleCtx.Config_Slot)

# ################################################################################################################################
# ################################################################################################################################

def test_an_unbound_process_keeps_its_own_name_mark_and_lock() -> 'None':
    config_manager = _new_config_manager(FakeDelivery())
    lock = config_manager.get_outgoing_publish_lock(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID)

    assert type(config_manager.outgoing_name_mark) is OutgoingNameMark
    assert type(lock) is type(RLock())

# ################################################################################################################################

def test_the_name_mark_is_shared_by_both_processes(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    _, config = bindings

    config_manager = _new_config_manager(FakeDelivery())
    worker_mark = config_manager.outgoing_name_mark

    assert type(worker_mark) is SharedNameMark

    # Every name is current before the first rename ..
    assert worker_mark.is_current(_sub_key, ModuleCtx.Old_Name)

    # .. the config process renames the connection, after which only the new name is current in the worker ..
    config_mark = SharedNameMark(config)
    config_mark.set_name(_sub_key, ModuleCtx.New_Name)

    assert worker_mark.is_current(_sub_key, ModuleCtx.New_Name)
    assert not worker_mark.is_current(_sub_key, ModuleCtx.Old_Name)
    assert region.lock_counter(region.lock_entry(_sub_key)) != RegionCtx.Name_Mark_Unset

    # .. and the deletion of the connection clears the mark.
    config_mark.clear(_sub_key)

    assert worker_mark.is_current(_sub_key, ModuleCtx.Old_Name)
    assert region.lock_counter(region.lock_entry(_sub_key)) == RegionCtx.Name_Mark_Unset

# ################################################################################################################################

def test_the_lock_is_reentrant_and_orders_the_greenlets_of_a_process(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    worker, _ = bindings

    config_manager = _new_config_manager(FakeDelivery())
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
    assert not region.lock_has_place(entry, worker.place)

# ################################################################################################################################

def test_the_worker_waits_for_the_lock_of_the_config_process(bindings:'bindinglist') -> 'None':
    worker, config = bindings

    worker_lock = SharedPublishLock(worker, _sub_key)
    config_lock = SharedPublishLock(config, _sub_key)

    events:'strlist' = []

    def hold() -> 'None':
        with config_lock:
            events.append('config-in')
            gevent.sleep(ModuleCtx.Hold_Seconds)
            events.append('config-out')

    def wait() -> 'None':
        with worker_lock:
            events.append('worker')

    holder = gevent.spawn(hold)
    gevent.sleep(0)
    waiter = gevent.spawn(wait)

    # The worker enters only after the config process released the lock and its descriptor was written to
    _ = gevent.joinall([holder, waiter], timeout=ModuleCtx.Wait_Seconds, raise_error=True)

    assert events == ['config-in', 'config-out', 'worker']

# ################################################################################################################################

def test_a_stopped_waiter_withdraws_its_ticket(region:'SharedRegion', bindings:'bindinglist') -> 'None':
    worker, config = bindings
    entry = region.lock_entry(_sub_key)

    worker_lock = SharedPublishLock(worker, _sub_key)
    config_lock = SharedPublishLock(config, _sub_key)

    def wait() -> 'None':
        with worker_lock:
            pass

    # The waiter of the worker is stopped while the config process holds the lock ..
    with config_lock:
        waiter = gevent.spawn(wait)
        gevent.sleep(0)

        assert region.lock_has_place(entry, worker.place)

        waiter.kill()

        assert not region.lock_has_place(entry, worker.place)

    # .. so the next waiter of the worker takes a ticket anew and enters at once.
    entered = gevent.spawn(wait)
    _ = entered.join(timeout=ModuleCtx.Wait_Seconds)

    assert entered.successful()

# ################################################################################################################################

def test_the_worker_pauses_its_own_delivery(bindings:'bindinglist') -> 'None':
    delivery = FakeDelivery()

    pause_outgoing_delivery(cast_('PushDelivery', delivery), _sub_key)
    resume_outgoing_delivery(cast_('PushDelivery', delivery), _sub_key)

    assert delivery.calls == [('pause', _sub_key, 0.0), ('resume', _sub_key)]
    assert bindings[0].place == ModuleCtx.Worker_Place

# ################################################################################################################################

def test_the_config_process_has_the_worker_pause_its_delivery(
    bindings:'bindinglist',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    _, config = bindings

    delivery = FakeDelivery()
    client = FakeClient(delivery, EntryStatus.OK)

    _bind_as_config_process(config, client, monkeypatch)

    pause_outgoing_delivery(cast_('PushDelivery', FakeDelivery()), _sub_key)

    # The worker paused with the timeout that keeps its answer within the deadline of the query ..
    assert delivery.calls == [('pause', _sub_key, RegionCtx.Relay_Join_Timeout)]

    resume_outgoing_delivery(cast_('PushDelivery', FakeDelivery()), _sub_key)

    # .. and resumed once the hold ended.
    assert delivery.calls[-1] == ('resume', _sub_key)
    assert [body[RegionCtx.Key_Action] for body in client.bodies] == [RegionCtx.Action_Pause, RegionCtx.Action_Resume]

# ################################################################################################################################

def test_an_unconfirmed_pause_fails_the_hold(bindings:'bindinglist', monkeypatch:'pytest.MonkeyPatch') -> 'None':
    _, config = bindings

    delivery = FakeDelivery()
    client = FakeClient(delivery, EntryStatus.Timeout)

    _bind_as_config_process(config, client, monkeypatch)

    with pytest.raises(OutgoingHoldError):
        pause_outgoing_delivery(cast_('PushDelivery', FakeDelivery()), _sub_key)

    # The worker, which may pause after the deadline, is asked to resume
    assert [body[RegionCtx.Key_Action] for body in client.bodies] == [RegionCtx.Action_Pause, RegionCtx.Action_Resume]

# ################################################################################################################################

def test_a_hold_in_the_config_process_pauses_the_worker_under_the_lock(
    region:'SharedRegion',
    bindings:'bindinglist',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    _, config = bindings
    entry = region.lock_entry(_sub_key)

    delivery = FakeDelivery()
    client = FakeClient(delivery, EntryStatus.OK)

    _bind_as_config_process(config, client, monkeypatch)

    config_manager = _new_config_manager(FakeDelivery())
    config_manager._outgoing_sub_key_cache.add(_sub_key)

    with config_manager.hold_outgoing_queue(ModuleCtx.Conn_Type, ModuleCtx.Conn_ID):

        # The config process holds the lock of the region, which no publication in the worker can take meanwhile,
        # and the worker paused its delivery ..
        assert region.lock_has_place(entry, config.place)
        assert delivery.calls == [('pause', _sub_key, RegionCtx.Relay_Join_Timeout)]

    # .. which it resumed once the hold ended, after which the lock is free.
    assert delivery.calls[-1] == ('resume', _sub_key)
    assert not region.lock_has_place(entry, config.place)

# ################################################################################################################################
# ################################################################################################################################

def _publish_in_process(region:'SharedRegion', place:'int', count_path:'str') -> 'None':
    """ Takes the publish lock of the queue the given number of times, and under it reads, raises and writes back
    a count that both processes share in a file.
    """
    gevent.reinit()
    bind_outgoing(region, place)

    binding = cast_('OutgoingBinding', get_outgoing_binding())
    lock = SharedPublishLock(binding, _sub_key)

    for _ in range(ModuleCtx.Round_Count):
        with lock:
            with open(count_path) as count_file:
                count = int(count_file.read())

            # The other process runs meanwhile, and only the lock keeps it from reading the same count
            gevent.sleep(0)
            os.sched_yield()

            with open(count_path, 'w') as count_file:
                _ = count_file.write(str(count + 1))

    os._exit(0)

# ################################################################################################################################

def test_the_worker_and_the_config_process_take_turns(region:'SharedRegion', tmp_path:'Path') -> 'None':
    count_path = tmp_path / 'count'
    _ = count_path.write_text('0')

    places = [ModuleCtx.Worker_Place, ModuleCtx.Config_Place]
    processes = []

    for place in places:
        process = _fork_context.Process(target=_publish_in_process, args=(region, place, str(count_path)))
        process.start()
        processes.append(process)

    for process in processes:
        process.join(ModuleCtx.Wait_Seconds)
        assert process.exitcode == 0

    # Every read, raise and write of each process happened under the lock, so none of them was lost
    expected = len(places) * ModuleCtx.Round_Count

    assert int(count_path.read_text()) == expected

# ################################################################################################################################
# ################################################################################################################################
