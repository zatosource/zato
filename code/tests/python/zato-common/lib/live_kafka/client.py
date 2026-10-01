# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Host-side access to a test broker - what a test produces into a topic behind Zato's back
# and what it reads back out of one to see what Zato wrote there.

# stdlib
from time import monotonic, sleep
from typing import NamedTuple
from uuid import uuid4

# confluent-kafka
from confluent_kafka import Consumer, KafkaException, Producer, TopicPartition
from confluent_kafka.admin import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_kafka.tls import KafkaTLS
    from zato.common.typing_ import any_, anydict, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long one produce may take before it counts as failed
    Produce_Timeout = 15.0

    # How long a read of a topic waits for its messages
    Read_Timeout = 30.0

    # How long a single poll blocks
    Poll_Timeout = 0.5

    # How long a metadata or an offsets request may take
    Admin_Timeout = 10.0

    # How long to wait for a consumer group to be assigned its partitions
    Assignment_Timeout = 60.0

    # The group a one-off reader joins - it never commits, so the name does not matter beyond being unique
    Reader_Group_Prefix = 'zato-test-reader-'

# ################################################################################################################################
# ################################################################################################################################

class TopicMessage(NamedTuple):
    topic: str
    partition: int
    offset: int
    key: 'bytes | None'
    value: 'bytes | None'
    headers: 'dict[str, bytes | None]'
    timestamp: int

# ################################################################################################################################
# ################################################################################################################################

def base_config(address:'str', tls:'KafkaTLS | None'=None) -> 'anydict':
    """ The client configuration of a plaintext or a TLS connection to the broker.
    """
    out:'anydict' = {'bootstrap.servers': address}

    if tls:
        out.update({
            'security.protocol': 'ssl',
            'ssl.ca.location': tls.ca_cert,
            'ssl.certificate.location': tls.client_cert,
            'ssl.key.location': tls.encrypted_client_key,
            'ssl.key.password': tls.key_password,
        })

    return out

# ################################################################################################################################

def _to_header_list(headers:'dict[str, bytes | str] | None') -> 'anylist':
    """ Headers as the list of pairs the producer takes - text values become UTF-8.
    """
    out:'anylist' = []

    for name, value in (headers or {}).items():
        if isinstance(value, str):
            value = value.encode('utf8')
        out.append((name, value))

    return out

# ################################################################################################################################

def produce(
    address:'str',
    topic:'str',
    value:'bytes | str | None',
    *,
    key:'bytes | str | None'=None,
    headers:'dict[str, bytes | str] | None'=None,
    partition:'int | None'=None,
    tls:'KafkaTLS | None'=None,
    extra_config:'anydict | None'=None,
    ) -> 'TopicMessage':
    """ Writes one message to a topic and returns where it landed. A None value is a tombstone.
    """
    config = base_config(address, tls)
    config['message.timeout.ms'] = int(ModuleCtx.Produce_Timeout * 1000)
    config.update(extra_config or {})

    if isinstance(value, str):
        value = value.encode('utf8')

    if isinstance(key, str):
        key = key.encode('utf8')

    outcome:'anylist' = []

    def on_delivery(error:'any_', message:'any_') -> 'None':
        outcome.append((error, message))

    producer = Producer(config)

    kwargs:'anydict' = {'key': key, 'headers': _to_header_list(headers), 'on_delivery': on_delivery}

    if partition is not None:
        kwargs['partition'] = partition

    producer.produce(topic, value, **kwargs)
    _ = producer.flush(ModuleCtx.Produce_Timeout)

    if not outcome:
        raise Exception(f'No delivery report for a message to `{topic}` within {ModuleCtx.Produce_Timeout}s')

    error, message = outcome[0]

    if error:
        raise Exception(f'Could not produce to `{topic}`: {error}')

    out = TopicMessage(
        topic=message.topic(),
        partition=message.partition(),
        offset=message.offset(),
        key=key,
        value=value,
        headers=dict(headers or {}), # type: ignore[arg-type]
        timestamp=message.timestamp()[1],
    )

    return out

# ################################################################################################################################

def _to_topic_message(message:'any_') -> 'TopicMessage':
    """ A consumed message as the tuple the tests look at.
    """
    headers:'dict[str, bytes | None]' = {}

    for name, value in (message.headers() or []):
        headers[name] = value

    out = TopicMessage(
        topic=message.topic(),
        partition=message.partition(),
        offset=message.offset(),
        key=message.key(),
        value=message.value(),
        headers=headers,
        timestamp=message.timestamp()[1],
    )

    return out

# ################################################################################################################################

def read_topic(
    address:'str',
    topic:'str',
    count:'int',
    *,
    timeout:'float'=ModuleCtx.Read_Timeout,
    tls:'KafkaTLS | None'=None,
    from_offset:'int | None'=None,
    partition:'int | None'=None,
    ) -> 'list[TopicMessage]':
    """ Reads a topic from its start, or from an offset of one partition, until it has the count of messages asked for
    or the timeout passes. What it returns is everything it saw, so a caller asserting on the count sees the extras.
    """
    config = base_config(address, tls)
    config.update({
        'group.id': ModuleCtx.Reader_Group_Prefix + uuid4().hex,
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest',
        'enable.partition.eof': False,
    })

    consumer = Consumer(config)

    try:
        if partition is not None:
            start = from_offset if from_offset is not None else 0
            consumer.assign([TopicPartition(topic, partition, start)])
        else:
            metadata = consumer.list_topics(topic, timeout=ModuleCtx.Admin_Timeout)
            partitions = metadata.topics[topic].partitions
            start = from_offset if from_offset is not None else 0
            consumer.assign([TopicPartition(topic, idx, start) for idx in partitions])

        out:'list[TopicMessage]' = []
        deadline = monotonic() + timeout

        while len(out) < count and monotonic() < deadline:
            message = consumer.poll(ModuleCtx.Poll_Timeout)

            if message is None:
                continue

            if message.error():
                raise KafkaException(message.error())

            out.append(_to_topic_message(message))

        return out

    finally:
        consumer.close()

# ################################################################################################################################

def committed_offset(address:'str', group_id:'str', topic:'str', partition:'int'=0, tls:'KafkaTLS | None'=None) -> 'int':
    """ The offset a consumer group has committed for a partition, -1 when it has committed none.
    """
    config = base_config(address, tls)
    config['group.id'] = group_id

    consumer = Consumer(config)

    try:
        result = consumer.committed([TopicPartition(topic, partition)], timeout=ModuleCtx.Admin_Timeout)
        offset = result[0].offset

        # librdkafka reports an unset offset with a negative sentinel
        out = offset if offset >= 0 else -1
        return out

    finally:
        consumer.close()

# ################################################################################################################################

def wait_until_committed(
    address:'str',
    group_id:'str',
    topic:'str',
    partition:'int',
    expected:'int',
    *,
    timeout:'float'=ModuleCtx.Read_Timeout,
    tls:'KafkaTLS | None'=None,
    ) -> 'int':
    """ Waits until the group's committed offset reaches the expected one and returns what it saw last.
    """
    deadline = monotonic() + timeout
    offset = -1

    while monotonic() < deadline:
        offset = committed_offset(address, group_id, topic, partition, tls)

        if offset >= expected:
            return offset

        sleep(ModuleCtx.Poll_Timeout)

    raise Exception(f'Group `{group_id}` did not commit offset {expected} of {topic}/{partition} within {timeout}s, last: {offset}')

# ################################################################################################################################

def group_assignments(address:'str', group_id:'str', tls:'KafkaTLS | None'=None) -> 'dict[str, list[tuple[str, int]]]':
    """ The partitions each member of a consumer group holds, by member id - empty when the group has no members.
    """
    admin = AdminClient(base_config(address, tls))
    futures = admin.describe_consumer_groups([group_id], request_timeout=ModuleCtx.Admin_Timeout)
    description = futures[group_id].result()

    out:'dict[str, list[tuple[str, int]]]' = {}

    for member in description.members:
        partitions = [(elem.topic, elem.partition) for elem in member.assignment.topic_partitions]
        out[member.member_id] = partitions

    return out

# ################################################################################################################################

def wait_for_assignment(
    address:'str',
    group_id:'str',
    topic:'str',
    *,
    partition_count:'int'=1,
    timeout:'float'=ModuleCtx.Assignment_Timeout,
    tls:'KafkaTLS | None'=None,
    ) -> 'None':
    """ Waits until a consumer group holds every partition of a topic - a channel that has not joined yet
    would miss what a test produces when the channel starts from the latest offset.
    """
    deadline = monotonic() + timeout
    last:'any_' = None

    while monotonic() < deadline:
        try:
            assignments = group_assignments(address, group_id, tls)
        except Exception as e:
            last = e
        else:
            held = set()
            for partitions in assignments.values():
                for name, idx in partitions:
                    if name == topic:
                        held.add(idx)

            if len(held) >= partition_count:
                return

            last = assignments

        sleep(ModuleCtx.Poll_Timeout)

    raise Exception(f'Group `{group_id}` was not assigned {partition_count} partitions of `{topic}` within {timeout}s, last: {last}')

# ################################################################################################################################

def headers_as_text(message:'TopicMessage') -> 'strdict':
    """ A message's headers as text, for assertions on what Zato wrote.
    """
    out:'strdict' = {}

    for name, value in message.headers.items():
        out[name] = value.decode('utf8') if value is not None else ''

    return out

# ################################################################################################################################
# ################################################################################################################################
