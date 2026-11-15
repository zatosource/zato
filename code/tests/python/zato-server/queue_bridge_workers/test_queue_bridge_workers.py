# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
from base64 import b64encode
from multiprocessing import get_context
from types import SimpleNamespace

# gevent
import gevent
from gevent import monkey, sleep

# Redis
from redis import Redis

# Zato
from zato.common.api import GENERIC, KAFKA
from zato.common.typing_ import cast_
from zato.server.queue_bridge.client import get_recv_stream, get_reply_group, ModuleCtx as ClientCtx, QueueBridgeClient
from zato.server.queue_bridge.recv import ChannelListener, Consumer_Name, Group_Name, Read_New, Read_Pending

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from multiprocessing.queues import SimpleQueue
    from multiprocessing.synchronize import Event, Semaphore
    from zato.common.typing_ import any_, anydict, anylist, intlist, strlist
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    anydict = anydict
    anylist = anylist
    Event = Event
    ForkProcess = ForkProcess
    intlist = intlist
    ParallelServer = ParallelServer
    Semaphore = Semaphore
    SimpleQueue = SimpleQueue
    strlist = strlist

    processlist = list[ForkProcess]

# ################################################################################################################################
# ################################################################################################################################

_context = get_context('fork')

class ModuleCtx:

    # How long the test waits for a process, in seconds
    Join_Timeout = 60.0

    # How long a listener may take to handle every entry, in seconds
    Handle_Timeout = 30.0

    # How long a listener keeps running after it handled every entry, so that an entry dispatched twice is handled again
    Settle_Seconds = 0.5

    # How long the service of the tests takes to handle one entry, in seconds
    Handle_Seconds = 0.1

    # How often the child checks whether every entry is acknowledged, in seconds
    Check_Interval = 0.05

    Channel_ID = 1
    Channel_Name = 'test.kafka'
    Topic = 'test.topic'
    Service = 'test.service'

    # The entries a terminated worker read and did not acknowledge, and the entries added after them
    Pending_Count = 4
    New_Count = 2

    # The value of the tombstone header of a message that is not a tombstone
    Is_Tombstone_False = 'false'

    Connection_Name = 'test.conn'
    Ping_Count = 5
    Ping_Timeout = 2.0

    # How long one read of the command stream blocks in the process that stands for the queue bridge, in milliseconds
    Command_Block_Ms = 100

# ################################################################################################################################
# ################################################################################################################################

def _new_redis(redis_conn:'Redis') -> 'Redis':
    """ A new connection to the Redis server of a test, for a forked process.
    """
    connection_kwargs = redis_conn.connection_pool.connection_kwargs
    out = Redis(host=connection_kwargs['host'], port=connection_kwargs['port'], decode_responses=True)

    return out

# ################################################################################################################################

def _patch_child() -> 'None':
    """ Prepares a forked process to run greenlets that use Redis connections.
    """
    gevent.reinit()
    _ = monkey.patch_all()

# ################################################################################################################################

def _new_channel_config() -> 'anydict':
    """ The configuration of the Kafka channel of the tests.
    """
    consumer = KAFKA.Consumer

    out = {
        'id': ModuleCtx.Channel_ID,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
        'name': ModuleCtx.Channel_Name,
        'service': ModuleCtx.Service,
        consumer.Field_Routing: '',
        consumer.Field_Should_Deliver_Tombstones: False,
        consumer.Field_Dedup_Header: '',
        consumer.Field_Dedup_TTL: consumer.Default_Dedup_TTL,
    }

    return out

# ################################################################################################################################

def _add_entries(redis:'Redis', first_offset:'int', count:'int') -> 'None':
    """ Adds the messages of one partition to the recv stream of the channel, as the queue bridge does.
    """
    header = KAFKA.Header
    stream = get_recv_stream(ModuleCtx.Channel_ID)

    for offset in range(first_offset, first_offset + count):
        headers = {header.Partition: '0', header.Offset: str(offset), header.Is_Tombstone: ModuleCtx.Is_Tombstone_False}
        payload = b64encode(json.dumps({'offset': offset}).encode()).decode()

        _ = redis.xadd(stream, {
            'channel_name': ModuleCtx.Channel_Name,
            'topic': ModuleCtx.Topic,
            'service': '',
            'payload': payload,
            'headers': json.dumps(headers),
        })

# ################################################################################################################################

def _get_pending_count(redis:'Redis') -> 'int':
    """ How many entries of the recv stream were read and not acknowledged.
    """
    stream = get_recv_stream(ModuleCtx.Channel_ID)
    summary = cast_('anydict', redis.xpending(stream, Group_Name))

    out = summary['pending']
    return out

# ################################################################################################################################

def _run_listener(results:'SimpleQueue', redis_conn:'Redis', total:'int') -> 'None':
    """ Runs the listener of the channel until it handled every entry, and reports the offset of each handling.
    """
    _patch_child()

    redis = _new_redis(redis_conn)
    handled:'intlist' = []

    def invoke(service:'str', payload:'bytes', **kwargs:'any_') -> 'None':
        offset = int(kwargs['request_ctx']['zato.request.headers'][KAFKA.Header.Offset])
        handled.append(offset)
        results.put(offset)
        sleep(ModuleCtx.Handle_Seconds)

    client = QueueBridgeClient(redis, slot=0)
    server = SimpleNamespace(_queue_bridge=client, service_audit_log=None, invoke=invoke)

    listener = ChannelListener(cast_('ParallelServer', server), _new_channel_config())
    listener.start()

    # The listener handles every entry and acknowledges it ..
    deadline = time.monotonic() + ModuleCtx.Handle_Timeout

    while time.monotonic() < deadline:
        if len(handled) >= total and _get_pending_count(redis) == 0:
            break
        sleep(ModuleCtx.Check_Interval)

    # .. and it keeps running for a while, during which an entry dispatched twice would be handled again.
    sleep(ModuleCtx.Settle_Seconds)
    listener.stop()

# ################################################################################################################################

def _run_pings(results:'SimpleQueue', redis_conn:'Redis', slot:'int', ready:'Semaphore', go:'Event') -> 'None':
    """ Runs the queue bridge client of one worker, which pings a connection and reports the status of each reply.
    """
    _patch_child()

    redis = _new_redis(redis_conn)
    client = QueueBridgeClient(redis, slot=slot)

    # The reply group of this worker exists before any worker sends its first command ..
    ready.release()
    _ = go.wait(ModuleCtx.Join_Timeout)

    # .. and every reply to a command of this worker reaches this worker.
    for _ in range(ModuleCtx.Ping_Count):
        reply = client.ping(ModuleCtx.Connection_Name, timeout=ModuleCtx.Ping_Timeout)
        results.put(reply['status'])

# ################################################################################################################################

def _answer_pings(redis:'Redis', processes:'processlist') -> 'None':
    """ Answers each ping command on the reply stream, as the queue bridge does, until every worker exits.
    """
    last_id = '0'

    while any(process.is_alive() for process in processes):
        result = cast_('anylist', redis.xread({ClientCtx.Command_Stream: last_id}, block=ModuleCtx.Command_Block_Ms))

        for _stream_name, messages in result:
            for msg_id, fields in messages:
                last_id = msg_id

                if fields['command'] == 'ping':
                    _ = redis.xadd(ClientCtx.Reply_Stream, {
                        'correlation_id': fields['correlation_id'],
                        'status': ClientCtx.Status_OK,
                        'data': '',
                    })

# ################################################################################################################################

def _run_workers(redis_conn:'Redis', slots:'intlist') -> 'strlist':
    """ Runs one pinging worker for each slot at once and returns the statuses of the replies of all of them.
    """
    results:'SimpleQueue' = _context.SimpleQueue()
    ready = _context.Semaphore(0)
    go = _context.Event()

    processes:'processlist' = []

    for slot in slots:
        process = _context.Process(target=_run_pings, args=(results, redis_conn, slot, ready, go))
        process.start()
        processes.append(process)

    # Every worker created its reply group, and all of them send their commands at once ..
    for _ in slots:
        assert ready.acquire(timeout=ModuleCtx.Join_Timeout)

    go.set()

    # .. while this process stands for the queue bridge.
    _answer_pings(redis_conn, processes)

    for process in processes:
        process.join(ModuleCtx.Join_Timeout)
        assert process.exitcode == 0

    out:'strlist' = []

    while not results.empty():
        out.append(results.get())

    return out

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################

def test_a_restarted_listener_handles_each_pending_entry_once_and_then_the_new_ones(redis_conn:'Redis') -> 'None':
    stream = get_recv_stream(ModuleCtx.Channel_ID)
    total = ModuleCtx.Pending_Count + ModuleCtx.New_Count

    # The entries that a terminated worker read and did not acknowledge ..
    _add_entries(redis_conn, 0, ModuleCtx.Pending_Count)
    _ = redis_conn.xgroup_create(stream, Group_Name, id=Read_Pending, mkstream=True)
    _ = redis_conn.xreadgroup(Group_Name, Consumer_Name, {stream: Read_New}, count=ModuleCtx.Pending_Count)

    # .. and the ones added after them, which no worker read yet.
    _add_entries(redis_conn, ModuleCtx.Pending_Count, ModuleCtx.New_Count)

    results:'SimpleQueue' = _context.SimpleQueue()

    process = _context.Process(target=_run_listener, args=(results, redis_conn, total))
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

    handled:'intlist' = []

    while not results.empty():
        handled.append(results.get())

    # Each entry was handled once, the pending ones first and all of them in the order of the partition ..
    assert handled == list(range(total))

    # .. and every one of them was acknowledged.
    assert _get_pending_count(redis_conn) == 0

# ################################################################################################################################

def test_every_reply_reaches_the_worker_that_sent_its_command(redis_conn:'Redis') -> 'None':
    slots = [0, 1]
    statuses = _run_workers(redis_conn, slots)

    # Each worker received the reply to each of its commands ..
    assert statuses == [ClientCtx.Status_OK] * (ModuleCtx.Ping_Count * len(slots))

    # .. through the reply group of its own slot.
    groups = cast_('anylist', redis_conn.xinfo_groups(ClientCtx.Reply_Stream))
    group_names = sorted(item['name'] for item in groups)

    assert group_names == [get_reply_group(slot) for slot in slots]

# ################################################################################################################################

def test_a_worker_that_replaces_another_of_its_slot_receives_its_replies(redis_conn:'Redis') -> 'None':

    # The first worker of the slot receives its replies ..
    statuses = _run_workers(redis_conn, [0])
    assert statuses == [ClientCtx.Status_OK] * ModuleCtx.Ping_Count

    # .. and so does the worker that replaces it in the reply group that already exists.
    statuses = _run_workers(redis_conn, [0])
    assert statuses == [ClientCtx.Status_OK] * ModuleCtx.Ping_Count

# ################################################################################################################################
# ################################################################################################################################
