# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# gevent
from gevent.event import Event

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.fence import DeliveryFence
from zato.common.pubsub.ownership import get_owner_slot
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import any_, anydict, anylist, intlist, strlist
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    anydict = anydict
    anylist = anylist
    intlist = intlist
    strlist = strlist
    ParallelServer = ParallelServer
    SQLPubSubBackend = SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Region_Config = {
        'slot_count': 2,
        'wake_capacity': 8,
        'cell_capacity': 8,
        'queue_count': 1,
        'metric_count': 1,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': 1,
    }

    Slot_Count = 2
    Delivering_Slot = 0

    Topic_Name = '/test/fencing'
    Service_Name = 'test.fencing.subscriber'

    # How many subscription keys the ownership test starts
    Key_Count = 40

    # The expiration of the messages of the tests, which no test reaches
    Expiration_Time_ISO = '2099-01-01T00:00:00+00:00'

# ################################################################################################################################
# ################################################################################################################################

class Clock:
    """ The clock of the database, read by the delivery to compare with the expiration of a message.
    """
    def now(self) -> 'datetime':
        out = datetime.now(timezone.utc)
        return out

# ################################################################################################################################
# ################################################################################################################################

class AuditLog:
    """ Records the outcome events of the deliveries.
    """
    def __init__(self, region:'SharedRegion') -> 'None':
        self.region = region
        self.msg_ids:'strlist' = []

        # Whether a replacement worker starts in the delivering slot while an outcome event is written
        self.is_replaced_during_insert = False

    def insert(self, *args:'any_', **kwargs:'any_') -> 'None':
        self.msg_ids.append(kwargs['msg_id'])

        if self.is_replaced_during_insert:
            _ = self.region.next_slot_generation(ModuleCtx.Delivering_Slot)

# ################################################################################################################################
# ################################################################################################################################

class Backend:
    """ The part of the SQL pub/sub backend that a delivery loop uses, holding one batch of pending messages.
    """
    def __init__(self, server:'Server', messages:'anylist') -> 'None':
        self.server = server
        self.messages = messages
        self.clock = Clock()
        self.audit_log = AuditLog(server.region)
        self.audit_disabled_topics:'strlist' = []

        self.attempts:'strlist' = []
        self.acked:'strlist' = []

    def fetch_pending(self, sub_key:'str', max_messages:'int') -> 'anylist':
        out = self.messages
        self.messages = []
        return out

    def record_attempt(self, message:'anydict') -> 'bool':
        self.attempts.append(message['msg_id'])
        return True

    def ack_messages(self, sub_key:'str', msg_ids:'strlist', sequence_ids:'intlist') -> 'int':
        self.acked.extend(msg_ids)

        # The subscription ends after its batch, so the loop returns rather than waiting for new messages
        del self.server.config_manager._push_subs[sub_key]

        out = len(msg_ids)
        return out

    def is_topic_payload_exported(self, topic_name:'str') -> 'bool':
        return False

    def get_sub_event(self, sub_key:'str') -> 'Event':
        out = Event()
        return out

    def notify_sub_keys(self, sub_keys:'strlist') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class QueueDepth:
    def lower(self, sub_key:'str', count:'int') -> 'None':
        pass

# ################################################################################################################################

class ConfigManager:
    def __init__(self) -> 'None':
        self._push_subs:'anydict' = {}
        self.outgoing_queue_depth = QueueDepth()

# ################################################################################################################################

class Server:
    """ The part of the server that a delivery loop uses, invoking the service of a subscription.
    """
    def __init__(self, region:'SharedRegion') -> 'None':
        self.region = region
        self.config_manager = ConfigManager()
        self.invoked:'anylist' = []

        # Whether a replacement worker starts in the delivering slot while the service runs
        self.is_replaced_during_invoke = False

    def invoke(self, service_name:'str', data:'any_', data_format:'str') -> 'None':
        self.invoked.append(data)

        if self.is_replaced_during_invoke:
            _ = self.region.next_slot_generation(ModuleCtx.Delivering_Slot)

# ################################################################################################################################
# ################################################################################################################################

class Terminations:
    """ Records each call through which a fenced worker would terminate.
    """
    def __init__(self) -> 'None':
        self.count = 0

    def on_fenced(self) -> 'None':
        self.count += 1

# ################################################################################################################################
# ################################################################################################################################

def _new_message(msg_id:'str', sequence_id:'int') -> 'anydict':
    out = {
        'msg_id': msg_id,
        'sequence_id': sequence_id,
        'topic_name': ModuleCtx.Topic_Name,
        'expiration_time_iso': ModuleCtx.Expiration_Time_ISO,
        'data': '{}',
        'data_class': '',
        'cid': msg_id,
        'pub_time_iso': '2026-01-01T00:00:00+00:00',
        'data_size': 2,
        'priority': 5,
    }
    return out

# ################################################################################################################################

def _new_sub_config() -> 'anydict':
    out = {
        'topic_name': ModuleCtx.Topic_Name,
        'push_type': PubSub.Push_Type.Service,
        'push_service_name': ModuleCtx.Service_Name,
    }
    return out

# ################################################################################################################################

def _new_delivery(
    region:'SharedRegion',
    slot:'int',
    terminations:'Terminations',
    messages:'anylist',
    ) -> 'tuple[PushDelivery, Server, Backend]':

    generation = region.next_slot_generation(slot)
    fence = DeliveryFence(region, slot, generation, terminations.on_fenced)

    server = Server(region)
    backend = Backend(server, messages)

    # The server and the backend provide the part of their interfaces that a delivery loop uses
    parallel_server = cast_('ParallelServer', server)
    pubsub_backend = cast_('SQLPubSubBackend', backend)

    delivery = PushDelivery(parallel_server, pubsub_backend, fence)
    return delivery, server, backend

# ################################################################################################################################
# ################################################################################################################################

def test_a_loop_starts_only_in_the_worker_that_owns_its_key() -> 'None':
    region = SharedRegion(ModuleCtx.Region_Config)
    terminations = Terminations()

    deliveries:'list[PushDelivery]' = []

    for slot in range(ModuleCtx.Slot_Count):
        delivery, _, _ = _new_delivery(region, slot, terminations, [])
        deliveries.append(delivery)

    # Every worker is asked to start every key ..
    for index in range(ModuleCtx.Key_Count):
        sub_key = f'zpsk.test.{index}'

        for delivery in deliveries:
            delivery.start_sub_key(sub_key)

        # .. and only the owner of the key runs its loop.
        owner = get_owner_slot(sub_key, ModuleCtx.Slot_Count)

        for slot, delivery in enumerate(deliveries):
            assert (sub_key in delivery._greenlets) == (slot == owner)

    for delivery in deliveries:
        delivery.stop()

# ################################################################################################################################

def test_a_current_worker_acknowledges_its_batch() -> 'None':
    region = SharedRegion(ModuleCtx.Region_Config)
    terminations = Terminations()

    messages = [_new_message('msg-1', 1), _new_message('msg-2', 2)]
    delivery, server, backend = _new_delivery(region, ModuleCtx.Delivering_Slot, terminations, messages)

    sub_key = 'zpsk.test.current'
    server.config_manager._push_subs[sub_key] = [_new_sub_config()]

    delivery._delivery_loop(sub_key)

    assert backend.attempts == ['msg-1', 'msg-2']
    assert backend.audit_log.msg_ids == ['msg-1', 'msg-2']
    assert backend.acked == ['msg-1', 'msg-2']
    assert terminations.count == 0

# ################################################################################################################################

def test_a_superseded_worker_sends_no_attempt() -> 'None':
    region = SharedRegion(ModuleCtx.Region_Config)
    terminations = Terminations()

    messages = [_new_message('msg-1', 1)]
    delivery, server, backend = _new_delivery(region, ModuleCtx.Delivering_Slot, terminations, messages)

    sub_key = 'zpsk.test.superseded'
    server.config_manager._push_subs[sub_key] = [_new_sub_config()]

    # A replacement worker starts in the slot before the first attempt ..
    _ = region.next_slot_generation(ModuleCtx.Delivering_Slot)

    delivery._delivery_loop(sub_key)

    # .. so the worker records no attempt, sends nothing, acknowledges nothing and terminates.
    assert backend.attempts == []
    assert server.invoked == []
    assert backend.acked == []
    assert terminations.count == 1

# ################################################################################################################################

def test_a_worker_superseded_during_an_attempt_records_no_outcome() -> 'None':
    region = SharedRegion(ModuleCtx.Region_Config)
    terminations = Terminations()

    messages = [_new_message('msg-1', 1), _new_message('msg-2', 2)]
    delivery, server, backend = _new_delivery(region, ModuleCtx.Delivering_Slot, terminations, messages)

    sub_key = 'zpsk.test.during'
    server.config_manager._push_subs[sub_key] = [_new_sub_config()]

    # A replacement worker starts in the slot while the first message is sent ..
    server.is_replaced_during_invoke = True

    delivery._delivery_loop(sub_key)

    # .. so the worker records no outcome of it, sends no further message and terminates.
    assert backend.attempts == ['msg-1']
    assert len(server.invoked) == 1
    assert backend.audit_log.msg_ids == []
    assert backend.acked == []
    assert terminations.count == 1

# ################################################################################################################################

def _run_superseded_after_outcome_event(sub_key:'str') -> 'Backend':
    region = SharedRegion(ModuleCtx.Region_Config)
    terminations = Terminations()

    messages = [_new_message('msg-1', 1)]
    delivery, server, backend = _new_delivery(region, ModuleCtx.Delivering_Slot, terminations, messages)

    server.config_manager._push_subs[sub_key] = [_new_sub_config()]

    # A replacement worker starts in the slot after the outcome event of the message is written ..
    backend.audit_log.is_replaced_during_insert = True

    delivery._delivery_loop(sub_key)

    # .. so the worker acknowledges nothing and terminates.
    assert terminations.count == 1

    out = backend
    return out

# ################################################################################################################################

def test_a_worker_superseded_after_an_outcome_event_acknowledges_no_batch() -> 'None':
    backend = _run_superseded_after_outcome_event('zpsk.test.batch')

    assert backend.audit_log.msg_ids == ['msg-1']
    assert backend.acked == []

# ################################################################################################################################

def test_a_worker_superseded_after_an_outcome_event_acknowledges_no_queued_message() -> 'None':
    sub_key = f'{PubSub.Outgoing.Sub_Key_Prefix}test.queue'
    backend = _run_superseded_after_outcome_event(sub_key)

    assert backend.audit_log.msg_ids == ['msg-1']
    assert backend.acked == []

# ################################################################################################################################
# ################################################################################################################################
