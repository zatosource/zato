# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import unittest
from base64 import b64encode
from time import monotonic, sleep

# Zato
from zato.common.api import KAFKA
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig
from zato.common.test.config_multi_cpu_singletons import SingletonsConfig
from zato.common.test.queue_bridge_stand_in import ModuleCtx as StandInCtx
from zato.server.queue_bridge.client import get_reply_group, ModuleCtx as ClientCtx
from zato.server.queue_bridge.recv import Consumer_Name, Group_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import anydict, anylist, intlist, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Channel_Name = 'test.multi-cpu.singletons.kafka'
    Topic = 'test.multi-cpu.singletons'
    Group_ID = 'test.multi-cpu.singletons'

    # The broker of the channel, to which the stand-in for the queue bridge never connects
    Broker_Address = 'localhost:9092'

    # The connection that each worker pings through the stand-in
    Ping_Connection = 'test.multi-cpu.singletons.kafka-out'

    # How many pings the test sends through each slot, and how long each waits for its reply, in seconds
    Pings_Per_Slot = 3
    Ping_Timeout = 10.0

    # How many messages the stand-in adds to the stream of the channel
    Message_Count = 40

    # How long the channel has to start and to handle every message, in seconds
    Deadline = 60.0

    # How long the records are observed after every message was handled, so that a message handled twice is recorded
    Settle_Period = 5.0

    Is_Tombstone_False = 'false'
    Partition = '0'

# ################################################################################################################################
# ################################################################################################################################

def _get_recv_streams(redis:'Redis') -> 'strlist':
    """ Returns the recv stream of each Kafka channel that a listener of the server reads.
    """
    out:'strlist' = []

    for stream in redis.scan_iter(f'{ClientCtx.Recv_Stream_Prefix}*'):
        for group in redis.xinfo_groups(stream):
            if group['name'] == Group_Name:
                out.append(stream)

    return out

# ################################################################################################################################

def _add_messages(redis:'Redis', stream:'str', count:'int') -> 'None':
    """ Adds the messages of one partition to the recv stream of the channel, as the queue bridge does.
    """
    header = KAFKA.Header

    for offset in range(count):
        headers = {header.Partition: ModuleCtx.Partition, header.Offset: str(offset), header.Is_Tombstone: ModuleCtx.Is_Tombstone_False}
        payload = b64encode(json.dumps({'offset': offset}).encode()).decode()

        _ = redis.xadd(stream, {
            'channel_name': ModuleCtx.Channel_Name,
            'topic': ModuleCtx.Topic,
            'service': '',
            'payload': payload,
            'headers': json.dumps(headers),
        })

# ################################################################################################################################

def _read_records() -> 'anylist':
    """ Returns the offset and the slot of each message that the service of the channel handled, in the order of handling.
    """
    path = os.environ[SingletonsConfig.Bridge_Record_Env]

    if not os.path.exists(path):
        return []

    out:'anylist' = []

    with open(path) as record_file:
        for line in record_file:
            out.append(json.loads(line))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestQueueBridgeAcrossWorkers(unittest.TestCase):
    """ The reply to a command of a worker reaches that worker through the reply group of its slot,
    and the messages of a Kafka channel are read and handled by the listener of slot 0 alone, each once and in order.
    """

    def test_reply_of_each_worker_reaches_it(self) -> 'None':

        redis = SingletonsConfig.bridge_stand_in.new_redis()

        # Each worker reads the reply stream through a group of its own slot ..
        group_names:'strset' = set()

        for group in redis.xinfo_groups(ClientCtx.Reply_Stream):
            group_names.add(group['name'])

        for slot in range(MultiCPUTestConfig.worker_count):
            self.assertIn(get_reply_group(slot), group_names)

        # .. and receives the reply to each of its commands.
        payload:'anydict' = {
            'conn_name': ModuleCtx.Ping_Connection,
            'timeout': ModuleCtx.Ping_Timeout,
        }

        for slot in range(MultiCPUTestConfig.worker_count):
            for _ in range(ModuleCtx.Pings_Per_Slot):

                status, body = invoke_on_slot(slot, SingletonsConfig.Bridge_Ping_Service, payload)
                self.assertEqual(status, MultiCPUCtx.Status_OK, body)

                response = json.loads(body)
                self.assertEqual(response['slot'], slot)
                self.assertEqual(response['reply']['status'], StandInCtx.Status_OK)

# ################################################################################################################################

    def test_channel_messages_handled_once_by_one_worker(self) -> 'None':

        redis = SingletonsConfig.bridge_stand_in.new_redis()

        enmasse_import({
            'channel_kafka': [{
                'name': ModuleCtx.Channel_Name,
                'address': ModuleCtx.Broker_Address,
                'topics': [ModuleCtx.Topic],
                'group_id': ModuleCtx.Group_ID,
                'service': SingletonsConfig.Bridge_Record_Service,
            }],
        })

        # The listener of the channel starts reading its stream ..
        deadline = monotonic() + ModuleCtx.Deadline

        while not (streams := _get_recv_streams(redis)):

            if monotonic() > deadline:
                raise Exception(f'No listener of {ModuleCtx.Channel_Name} within {ModuleCtx.Deadline} s')

            sleep(MultiCPUCtx.Poll_Interval)

        self.assertEqual(len(streams), 1)
        stream = streams[0]

        # .. the messages of one partition arrive ..
        _add_messages(redis, stream, ModuleCtx.Message_Count)

        while len(_read_records()) < ModuleCtx.Message_Count:

            if monotonic() > deadline:
                raise Exception(f'Handled {len(_read_records())} of {ModuleCtx.Message_Count} messages')

            sleep(MultiCPUCtx.Poll_Interval)

        sleep(ModuleCtx.Settle_Period)

        # .. each of which the worker of slot 0 handled once and in the order of the partition ..
        offsets:'intlist' = []
        slots:'set[int]' = set()

        for record in _read_records():
            offsets.append(record['offset'])
            slots.add(record['slot'])

        self.assertEqual(offsets, list(range(ModuleCtx.Message_Count)))
        self.assertEqual(slots, {0})

        # .. through the one consumer of the group of the stream, which acknowledged every message.
        consumer_names:'strset' = set()

        for consumer in redis.xinfo_consumers(stream, Group_Name):
            consumer_names.add(consumer['name'])

        self.assertEqual(consumer_names, {Consumer_Name})

        pending = redis.xpending(stream, Group_Name)
        self.assertEqual(pending['pending'], 0)

# ################################################################################################################################
# ################################################################################################################################
