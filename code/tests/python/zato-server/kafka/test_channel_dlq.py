# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQ of a Kafka channel - how a message gets there, what each DLQ action does with it, what the delivery page
# shows of it and what a restart, a rename and a delete of the channel do to it.

# stdlib
import os
from json import dumps
from time import monotonic, sleep
from typing import NamedTuple

# pytest
import pytest

# Zato
from live_kafka.client import committed_offset, group_assignments, produce, wait_until_committed
from zato.common.api import HTTP_SOAP, KAFKA, PubSub
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.pubsub.dlq import Header_Attempts, Header_CID, Header_Error, Header_Error_Class, Header_Reason, Header_Rounds, \
    Header_Source, Header_Source_Topic, Key_DLQ
from zato.common.pubsub.outgoing import InboundType, Key_CID, Key_Conn_Name, Key_Conn_Type, Key_Data, Key_DLQ_Rounds, \
    Key_Headers, Key_Is_Base64, Key_Request, Key_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import KafkaSuite
    from redis.typing import EncodableT, FieldT
    from zato.common.typing_ import any_, anydict, callable_, strdict

    # The fields of one Redis stream entry
    stream_fields = dict[FieldT, EncodableT]

# ################################################################################################################################
# ################################################################################################################################

_header = KAFKA.Header
_dlq = HTTP_SOAP.DLQ

Receiver = 'test.kafka.receiver'
Receiver_Two = 'test.kafka.receiver.two'
Receiver_Three = 'test.kafka.receiver.three'

Route_Header = 'route-to'
Route_Value = 'three'

# The channel of the exhausted-retries case - three attempts, a second apart
Max_Retries = 2
Sleep_Time = 1

# How many times the rule puts a message back under the retry action
DLQ_Retries = 2

# How long the DLQ-off channel is left blocked before the consumer is checked to still be in its group,
# ten minutes is what the plan asks for and what a run on purpose sets
Block_Wait = float(os.environ.get('Zato_Test_Kafka_Block_Wait', '20'))

# How long nothing should arrive for a message that must not be invoked
Quiet_Time = 3.0

# A round of the DLQ-off channel plus room for the receiver
Round_Timeout = PubSub.Delivery.Retry_Round_Wait + 20.0

# ################################################################################################################################
# ################################################################################################################################

_yaml = """
channel_kafka:
  - name: {channel_dlq}
    address: {address}
    topics:
      - {topic_dlq}
      - {topic_dlq_two}
    group_id: {group_dlq}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: {max_retries}
    retry_sleep_time: {sleep_time}
    routing:
      - topic: {topic_dlq_two}
        service: {receiver_two}
      - header_name: {route_header}
        header_value: {route_value}
        service: {receiver_three}

  - name: {channel_off}
    address: {address}
    topics:
      - {topic_off}
    group_id: {group_off}
    service: {receiver_two}
    auto_offset_reset: earliest
    use_dlq: false
    max_retries: 0

  - name: {channel_poison}
    address: {address}
    topics:
      - {topic_poison}
    group_id: {group_poison}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0

  - name: {channel_retry}
    address: {address}
    topics:
      - {topic_retry}
    group_id: {group_retry}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: retry
    dlq_retries: {dlq_retries}
    dlq_retry_interval: 0
    routing:
      - header_name: {route_header}
        header_value: {route_value}
        service: {receiver_three}

  - name: {channel_forward}
    address: {address}
    topics:
      - {topic_forward}
    group_id: {group_forward}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: forward
    dlq_forward_to: {forward_topic}
    dlq_keep_header: true
    dlq_retry_interval: 0

  - name: {channel_discard}
    address: {address}
    topics:
      - {topic_discard}
    group_id: {group_discard}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: discard
    dlq_retry_interval: 0

  - name: {channel_keep}
    address: {address}
    topics:
      - {topic_keep}
    group_id: {group_keep}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: keep
    dlq_retry_interval: 0

  - name: {channel_lifecycle}
    address: {address}
    topics:
      - {topic_lifecycle}
    group_id: {group_lifecycle}
    service: {receiver}
    auto_offset_reset: earliest
    max_retries: 0
    dlq_action: retry
    dlq_retry_interval: 0
"""

# ################################################################################################################################
# ################################################################################################################################

class Names(NamedTuple):
    channel_dlq: str
    channel_off: str
    channel_poison: str
    channel_retry: str
    channel_forward: str
    channel_discard: str
    channel_keep: str
    channel_lifecycle: str
    topic_dlq: str
    topic_dlq_two: str
    topic_off: str
    topic_poison: str
    topic_retry: str
    topic_forward: str
    topic_discard: str
    topic_keep: str
    topic_lifecycle: str
    group_dlq: str
    group_off: str
    group_poison: str
    group_retry: str
    group_forward: str
    group_discard: str
    group_keep: str
    group_lifecycle: str
    forward_topic: str
    forward_sub_key: str

# ################################################################################################################################

@pytest.fixture(scope='module')
def names(kafka_suite:'KafkaSuite') -> 'Names':
    """ The connections of this module, imported once.
    """
    kinds = ('dlq', 'off', 'poison', 'retry', 'forward', 'discard', 'keep', 'lifecycle')

    fields:'strdict' = {}

    for kind in kinds:
        fields[f'channel_{kind}'] = kafka_suite.new_name(f'channel.{kind}')
        fields[f'topic_{kind}'] = kafka_suite.new_name(f'topic.{kind}')
        fields[f'group_{kind}'] = kafka_suite.new_name(f'group.{kind}')

    fields['topic_dlq_two'] = kafka_suite.new_name('topic.dlq.two')
    fields['forward_topic'] = kafka_suite.new_name('forward')
    fields['forward_sub_key'] = kafka_suite.new_name('forward.sub')

    out = Names(**fields)

    # The partition-blocking case needs a second partition to flow around the first
    kafka_suite.create_topic(out.topic_dlq, partitions=2)
    kafka_suite.create_topic(out.topic_off, partitions=2)

    for topic in (out.topic_dlq_two, out.topic_poison, out.topic_retry, out.topic_forward, out.topic_discard,
            out.topic_keep, out.topic_lifecycle):
        kafka_suite.create_topic(topic)

    yaml = _yaml.format(
        address=kafka_suite.address,
        receiver=Receiver,
        receiver_two=Receiver_Two,
        receiver_three=Receiver_Three,
        route_header=Route_Header,
        route_value=Route_Value,
        max_retries=Max_Retries,
        sleep_time=Sleep_Time,
        dlq_retries=DLQ_Retries,
        **out._asdict(),
    )
    kafka_suite.import_yaml(yaml)

    kafka_suite.subscribe_topic(out.forward_topic, out.forward_sub_key)

    return out

# ################################################################################################################################
# ################################################################################################################################

def dlq_ids(kafka_suite:'KafkaSuite', conn_name:'str') -> 'set[str]':
    out = {elem['msg_id'] for elem in kafka_suite.dlq(conn_name)['messages']}
    return out

# ################################################################################################################################

def wait_for_new_dlq_message(kafka_suite:'KafkaSuite', conn_name:'str', before:'set[str]') -> 'anydict':
    """ Waits until a DLQ holds one message more than before and returns the new one.
    """
    dlq = kafka_suite.wait_for_dlq_count(conn_name, len(before) + 1, timeout=Round_Timeout)
    new = [elem for elem in dlq['messages'] if elem['msg_id'] not in before]

    assert len(new) == 1, dlq
    return new[0]

# ################################################################################################################################

def send_to_dlq(
    kafka_suite:'KafkaSuite',
    conn_name:'str',
    topic:'str',
    receiver:'str',
    *,
    headers:'strdict | None'=None,
    key:'str | None'=None,
    partition:'int | None'=None,
    ) -> 'tuple[any_, anydict]':
    """ Produces a message the receiver refuses and returns where it landed and what the DLQ holds of it.
    """
    before = dlq_ids(kafka_suite, conn_name)
    kafka_suite.set_behaviour(receiver, fail_always=True)

    payload = kafka_suite.new_name('payload')
    landed = produce(kafka_suite.address, topic, payload, key=key, headers=headers, partition=partition)

    message = wait_for_new_dlq_message(kafka_suite, conn_name, before)
    assert message['document'][Key_Request][Key_Data] == payload

    out = (landed, message)
    return out

# ################################################################################################################################

def wait_for_rounds(kafka_suite:'KafkaSuite', conn_name:'str', rounds:'int') -> 'anydict':
    """ Blocks until a DLQ holds exactly one message that the rule has put back that many times.
    """
    deadline = monotonic() + Round_Timeout

    while monotonic() < deadline:
        messages = kafka_suite.dlq(conn_name)['messages']

        if len(messages) == 1 and messages[0]['document'][Key_DLQ][Header_Rounds] == rounds:
            out = messages[0]
            return out

        sleep(0.2)

    raise AssertionError(f'Timed out waiting for a DLQ message of `{conn_name}` with {rounds} rounds')

# ################################################################################################################################

def delivered_ok(payload:'str') -> 'callable_':
    """ What matches the invocation that delivered a payload successfully.
    """
    def matches(item:'anydict') -> 'bool':
        out = False

        if item['data'] == payload:
            if item['outcome'] == 'ok':
                out = True

        return out

    return matches

# ################################################################################################################################

def with_key(key:'str') -> 'callable_':
    """ What matches an invocation with a message of that key.
    """
    def matches(item:'anydict') -> 'bool':
        out = item['headers'].get(_header.Key) == key
        return out

    return matches

# ################################################################################################################################

def poison_entry(kafka_suite:'KafkaSuite', conn_name:'str', topic:'str', *, payload:'str', headers:'str') -> 'int':
    """ Writes one entry straight into a channel's recv stream, as the bridge would, with fields of the test's choosing.
    """
    connection = kafka_suite.connection(conn_name)
    channel_id = connection['id']

    fields:'stream_fields' = {
        'channel_id': str(channel_id),
        'channel_name': conn_name,
        'topic': topic,
        'service': Receiver,
        'payload': payload,
        'headers': headers,
        'reply_to_queue': '',
        'reply_to_queue_manager': '',
        'message_id': '',
    }
    _ = kafka_suite.redis.xadd(kafka_suite.recv_stream(channel_id), fields)

    return channel_id

# ################################################################################################################################

def wait_until_acked(kafka_suite:'KafkaSuite', channel_id:'int') -> 'None':
    deadline = monotonic() + Round_Timeout

    while monotonic() < deadline:
        if kafka_suite.pending_count(channel_id) == 0:
            return
        sleep(0.2)

    raise AssertionError(f'Channel {channel_id} still has pending entries: {kafka_suite.pending_count(channel_id)}')

# ################################################################################################################################
# ################################################################################################################################

def test_exhausted_retries_move_the_message_to_the_dlq_and_commit(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A service that always raises - the message is invoked once per attempt, lands in the channel's DLQ with everything
    it carried and a header saying why, its offset is committed and the next message on the partition follows.
    """
    headers = {'x-first': 'one', 'x-second': 'two'}
    landed, message = send_to_dlq(kafka_suite, names.channel_dlq, names.topic_dlq, Receiver,
        headers=headers, key='the-key', partition=0)

    document = message['document']
    request = document[Key_Request]
    dlq_header = document[Key_DLQ]

    assert document[Key_Conn_Type] == InboundType.KAFKA
    assert document[Key_Conn_Name] == names.channel_dlq
    assert document[Key_DLQ_Rounds] == 0

    # The payload and every header, the user's own and the Kafka ones
    assert request[Key_Service] == Receiver
    assert request[Key_Is_Base64] is False

    stored_headers = request[Key_Headers]
    assert stored_headers['x-first'] == 'one'
    assert stored_headers['x-second'] == 'two'
    assert stored_headers[_header.Topic] == names.topic_dlq
    assert stored_headers[_header.Partition] == '0'
    assert stored_headers[_header.Offset] == str(landed.offset)
    assert stored_headers[_header.Key] == 'the-key'
    assert stored_headers[_header.Channel] == names.channel_dlq

    # The DLQ header of the move
    assert dlq_header[Header_Reason] == PubSub.Outgoing.DLQ_Reason_Retries_Exhausted
    assert dlq_header[Header_Error_Class] == 'ValueError'
    assert 'failed on purpose' in dlq_header[Header_Error]
    assert dlq_header[Header_Attempts] == Max_Retries + 1
    assert dlq_header[Header_Rounds] == 0
    assert dlq_header[Header_CID] == document[Key_CID]
    assert dlq_header[Header_Source_Topic] == names.topic_dlq
    assert dlq_header[Header_Source] == {_header.Topic: names.topic_dlq, _header.Partition: 0, _header.Offset: landed.offset}

    # Each attempt ran under the one cid the DLQ holds
    invocations = kafka_suite.wait_for_payload(request[Key_Data], Max_Retries + 1)
    assert [elem['outcome'] for elem in invocations] == ['failed'] * (Max_Retries + 1)
    assert {elem['cid'] for elem in invocations} == {document[Key_CID]}

    # The offset is committed and the next message on the partition is delivered
    _ = wait_until_committed(kafka_suite.address, names.group_dlq, names.topic_dlq, 0, landed.offset + 1)

    kafka_suite.set_behaviour(Receiver)
    next_payload = kafka_suite.new_name('payload')
    next_landed = produce(kafka_suite.address, names.topic_dlq, next_payload, partition=0)

    assert next_landed.offset == landed.offset + 1
    _ = kafka_suite.wait_for_payload(next_payload)

# ################################################################################################################################

def test_with_the_dlq_off_a_failing_message_blocks_its_partition_only(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ With the DLQ off a message is tried again a round later, its offset is not committed, the message behind it
    on the same partition waits, one on another partition does not, and the consumer stays in its group all along.
    """
    committed_before = committed_offset(kafka_suite.address, names.group_off, names.topic_off, 0)
    kafka_suite.set_behaviour(Receiver_Two, fail_always=True)

    blocked = kafka_suite.new_name('payload.blocked')
    behind = kafka_suite.new_name('payload.behind')
    other = kafka_suite.new_name('payload.other')

    blocked_landed = produce(kafka_suite.address, names.topic_off, blocked, partition=0)
    behind_landed = produce(kafka_suite.address, names.topic_off, behind, partition=0)
    _ = produce(kafka_suite.address, names.topic_off, other, partition=1)

    try:
        # The other partition flows ..
        _ = kafka_suite.wait_for_payload(other)

        # .. the blocked message is tried once per round, a round wait apart ..
        rounds = kafka_suite.wait_for_payload(blocked, 2, timeout=Round_Timeout)
        assert rounds[1]['time'] - rounds[0]['time'] >= PubSub.Delivery.Retry_Round_Wait
        assert {elem['cid'] for elem in rounds} == {rounds[0]['cid']}

        # .. nothing was committed and the one behind it was not invoked ..
        assert committed_offset(kafka_suite.address, names.group_off, names.topic_off, 0) == committed_before
        assert not [elem for elem in kafka_suite.received() if elem['data'] == behind]

        # .. and the consumer is still in its group once the block has lasted.
        sleep(Block_Wait)

        assignments = group_assignments(kafka_suite.address, names.group_off)
        held = {partition for partitions in assignments.values() for partition in partitions}

        assert held == {(names.topic_off, 0), (names.topic_off, 1)}, assignments
        assert committed_offset(kafka_suite.address, names.group_off, names.topic_off, 0) == committed_before
        assert not [elem for elem in kafka_suite.received() if elem['data'] == behind]

    finally:
        kafka_suite.set_behaviour(Receiver_Two)

    # Once the service works the message goes through, is committed, and the one behind it follows
    _ = kafka_suite.wait_for_received(delivered_ok(blocked), timeout=Round_Timeout)
    _ = kafka_suite.wait_for_payload(behind)

    assert behind_landed.offset == blocked_landed.offset + 1
    _ = wait_until_committed(kafka_suite.address, names.group_off, names.topic_off, 0, behind_landed.offset + 1)

# ################################################################################################################################

def test_a_payload_that_is_not_base64_goes_to_the_dlq_and_is_committed(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ An entry whose payload the server cannot decode is moved to the DLQ as one failed attempt with the decoding error,
    its offset is committed and the next message follows.
    """
    first = kafka_suite.new_name('payload')
    first_landed = produce(kafka_suite.address, names.topic_poison, first)
    _ = kafka_suite.wait_for_payload(first)
    _ = wait_until_committed(kafka_suite.address, names.group_poison, names.topic_poison, 0, first_landed.offset + 1)

    before = dlq_ids(kafka_suite, names.channel_poison)

    headers = {
        _header.Topic: names.topic_poison,
        _header.Partition: '0',
        _header.Offset: str(first_landed.offset),
        _header.Is_Tombstone: 'false',
        'x-poison': 'yes',
    }
    channel_id = poison_entry(kafka_suite, names.channel_poison, names.topic_poison, payload='not*base64', headers=dumps(headers))

    message = wait_for_new_dlq_message(kafka_suite, names.channel_poison, before)
    document = message['document']
    dlq_header = document[Key_DLQ]

    assert document[Key_Request][Key_Data] == 'not*base64'
    assert document[Key_Request][Key_Headers][_header.Topic] == names.topic_poison
    assert document[Key_Request][Key_Headers][_header.Offset] == str(first_landed.offset)
    assert dlq_header[Header_Error].startswith('Cannot decode message')
    assert dlq_header[Header_Error_Class] == 'Error'
    assert dlq_header[Header_Attempts] == 1
    assert dlq_header[Header_Source] == {
        _header.Topic: names.topic_poison, _header.Partition: 0, _header.Offset: first_landed.offset}

    wait_until_acked(kafka_suite, channel_id)
    assert committed_offset(kafka_suite.address, names.group_poison, names.topic_poison, 0) == first_landed.offset + 1

    # The listener goes on with the next entry
    following = kafka_suite.new_name('payload')
    following_landed = produce(kafka_suite.address, names.topic_poison, following)
    _ = kafka_suite.wait_for_payload(following)
    _ = wait_until_committed(kafka_suite.address, names.group_poison, names.topic_poison, 0, following_landed.offset + 1)

# ################################################################################################################################

def test_a_headers_field_that_is_not_json_goes_to_the_dlq(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ An entry whose headers cannot be read goes to the DLQ with the error, without a position, and is acknowledged.
    """
    before = dlq_ids(kafka_suite, names.channel_poison)

    channel_id = poison_entry(kafka_suite, names.channel_poison, names.topic_poison, payload='YWJj', headers='not json')

    message = wait_for_new_dlq_message(kafka_suite, names.channel_poison, before)
    document = message['document']
    dlq_header = document[Key_DLQ]

    assert document[Key_Request][Key_Data] == 'YWJj'
    assert document[Key_Request][Key_Headers] == {_header.Channel: names.channel_poison, _header.Topic: names.topic_poison}
    assert dlq_header[Header_Error].startswith('Cannot decode message')
    assert dlq_header[Header_Error_Class] == 'JSONDecodeError'
    assert Header_Source not in dlq_header

    wait_until_acked(kafka_suite, channel_id)

    following = kafka_suite.new_name('payload')
    _ = produce(kafka_suite.address, names.topic_poison, following)
    _ = kafka_suite.wait_for_payload(following)

# ################################################################################################################################

def test_a_payload_the_service_cannot_parse_goes_to_the_dlq_and_is_committed(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A service that parses its input and raises on what it gets - the message goes to the DLQ with the parser's error.
    """
    before = dlq_ids(kafka_suite, names.channel_poison)
    kafka_suite.set_behaviour(Receiver, parse_json=True)

    payload = 'this is not json ' + kafka_suite.new_name('payload')
    landed = produce(kafka_suite.address, names.topic_poison, payload)

    message = wait_for_new_dlq_message(kafka_suite, names.channel_poison, before)
    dlq_header = message['document'][Key_DLQ]

    assert message['document'][Key_Request][Key_Data] == payload
    assert dlq_header[Header_Error_Class] == 'JSONDecodeError'
    assert dlq_header[Header_Attempts] == 1

    _ = wait_until_committed(kafka_suite.address, names.group_poison, names.topic_poison, 0, landed.offset + 1)

# ################################################################################################################################

def test_a_tombstone_with_delivery_off_is_committed_and_skipped(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A tombstone on a channel that does not deliver them never reaches a service or the DLQ, only its commit.
    """
    before = dlq_ids(kafka_suite, names.channel_poison)

    landed = produce(kafka_suite.address, names.topic_poison, None, key='gone')
    _ = wait_until_committed(kafka_suite.address, names.group_poison, names.topic_poison, 0, landed.offset + 1)

    assert dlq_ids(kafka_suite, names.channel_poison) == before
    kafka_suite.not_received(with_key('gone'), within=Quiet_Time)

# ################################################################################################################################

def test_the_retry_action_invokes_the_routed_service_again_under_the_original_cid(
    kafka_suite:'KafkaSuite',
    names:'Names',
    ) -> 'None':
    """ The rule's retry invokes the service the routing picked, with the original payload, headers, Kafka metadata and cid,
    the audit log shows every attempt under that cid, and the rule gives up after as many rounds as the channel allows.
    """
    headers = {Route_Header: Route_Value, 'x-original': 'yes'}
    landed, message = send_to_dlq(kafka_suite, names.channel_retry, names.topic_retry, Receiver_Three, headers=headers, key='rk')

    document = message['document']
    cid = document[Key_CID]
    payload = document[Key_Request][Key_Data]

    assert document[Key_Request][Key_Service] == Receiver_Three
    assert document[Key_DLQ][Header_Rounds] == 0

    def is_ours(elem:'anydict') -> 'bool':
        return elem['data'] == payload

    first = kafka_suite.wait_for_received(is_ours, 1, service=Receiver_Three)
    assert first[0]['cid'] == cid

    try:
        for rounds in range(1, DLQ_Retries + 1):
            counts = kafka_suite.run_dlq_rule()
            assert counts[names.channel_retry] == 1, counts

            message = wait_for_rounds(kafka_suite, names.channel_retry, rounds)
            assert message['document'][Key_DLQ_Rounds] == rounds
            assert message['document'][Key_CID] == cid

            invocations = kafka_suite.wait_for_received(is_ours, rounds + 1, service=Receiver_Three)
            replay = invocations[-1]

            assert replay['cid'] == cid
            assert replay['outcome'] == 'failed'
            assert replay['headers'][Route_Header] == Route_Value
            assert replay['headers']['x-original'] == 'yes'
            assert replay['headers'][_header.Topic] == names.topic_retry
            assert replay['headers'][_header.Partition] == '0'
            assert replay['headers'][_header.Offset] == str(landed.offset)
            assert replay['headers'][_header.Key] == 'rk'
            assert replay['headers'][_header.Channel] == names.channel_retry

        # The channel's default service never saw it
        assert not kafka_suite.wait_for_received(is_ours, 0, service=Receiver)

        # As many rounds as allowed, then the rule leaves it
        counts = kafka_suite.run_dlq_rule()
        assert names.channel_retry not in counts, counts

        dlq = kafka_suite.dlq(names.channel_retry)
        assert len(dlq['messages']) == 1
        assert dlq['messages'][0]['msg_id'] == message['msg_id']

        # The audit log ties the first attempt and each replay together
        events = kafka_suite.wait_for_audit_events(cid, DLQ_Retries + 1)
        attempts = [elem for elem in events if elem['event_type'] == AuditEvent.Message_Received]

        assert len(attempts) == DLQ_Retries + 1, events
        assert {elem['source'] for elem in attempts} == {AuditSource.Kafka_Channel}
        assert {elem['object_name'] for elem in attempts} == {names.channel_retry}
        assert {elem['endpoint'] for elem in attempts} == {names.topic_retry}
        assert {elem['outcome'] for elem in attempts} == {AuditOutcome.Error}

    finally:
        kafka_suite.set_behaviour(Receiver_Three)

    # A retry by hand once the service works delivers it
    _ = kafka_suite.dlq_action('retry-message', sub_key=dlq['sub_key'], msg_id=message['msg_id'])

    invocations = kafka_suite.wait_for_received(is_ours, DLQ_Retries + 2, service=Receiver_Three)
    assert invocations[-1]['outcome'] == 'ok'
    assert invocations[-1]['cid'] == cid

    assert kafka_suite.dlq(names.channel_retry)['messages'] == []

    events = kafka_suite.wait_for_audit_events(cid, DLQ_Retries + 2)
    attempts = [elem for elem in events if elem['event_type'] == AuditEvent.Message_Received]
    assert attempts[-1]['outcome'] == AuditOutcome.OK

# ################################################################################################################################

def test_forward_publishes_the_message_with_its_header_and_without_it_when_the_switch_is_off(
    kafka_suite:'KafkaSuite',
    names:'Names',
    ) -> 'None':
    """ Under the forward action the rule publishes a due message to the topic the channel names - with the DLQ header
    and the Kafka position in it, or without the header once the switch is off.
    """
    _ = kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key)

    landed, message = send_to_dlq(kafka_suite, names.channel_forward, names.topic_forward, Receiver)

    counts = kafka_suite.run_dlq_rule()
    assert counts[names.channel_forward] == 1, counts

    forwarded = kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key)
    assert len(forwarded) == 1

    assert forwarded[0]['document'] == message['document']
    assert forwarded[0]['document'][Key_DLQ][Header_Source] == {
        _header.Topic: names.topic_forward, _header.Partition: 0, _header.Offset: landed.offset}

    assert kafka_suite.dlq(names.channel_forward)['messages'] == []

    kafka_suite.edit_connection(names.channel_forward, **{_dlq.Field_Keep_Header: False})

    try:
        assert kafka_suite.connection(names.channel_forward)[_dlq.Field_Keep_Header] is False

        _, message = send_to_dlq(kafka_suite, names.channel_forward, names.topic_forward, Receiver)

        counts = kafka_suite.run_dlq_rule()
        assert counts[names.channel_forward] == 1, counts

        forwarded = kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key)
        assert len(forwarded) == 1

        expected = dict(message['document'])
        _ = expected.pop(Key_DLQ)

        assert forwarded[0]['document'] == expected
        assert kafka_suite.dlq(names.channel_forward)['messages'] == []

    finally:
        kafka_suite.edit_connection(names.channel_forward, **{_dlq.Field_Keep_Header: True})

# ################################################################################################################################

def test_discard_empties_the_dlq(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ Under the discard action a due message is taken out of the DLQ and goes nowhere else.
    """
    _ = kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key)
    _, message = send_to_dlq(kafka_suite, names.channel_discard, names.topic_discard, Receiver)
    payload = message['document'][Key_Request][Key_Data]

    counts = kafka_suite.run_dlq_rule()
    assert counts[names.channel_discard] == 1, counts

    assert kafka_suite.dlq(names.channel_discard)['messages'] == []
    assert kafka_suite.topic_messages(names.forward_topic, names.forward_sub_key) == []

    kafka_suite.set_behaviour(Receiver)
    kafka_suite.not_received(delivered_ok(payload), within=Quiet_Time)

# ################################################################################################################################

def test_keep_leaves_the_message_and_an_edit_of_the_action_applies_to_the_next_run(
    kafka_suite:'KafkaSuite',
    names:'Names',
    ) -> 'None':
    """ Under the keep action the rule does not touch the DLQ, and once the action is edited the very next run carries
    the new one out.
    """
    _, message = send_to_dlq(kafka_suite, names.channel_keep, names.topic_keep, Receiver)

    counts = kafka_suite.run_dlq_rule()
    assert names.channel_keep not in counts, counts

    dlq = kafka_suite.dlq(names.channel_keep)
    assert [elem['msg_id'] for elem in dlq['messages']] == [message['msg_id']]

    kafka_suite.edit_connection(names.channel_keep, **{_dlq.Field_Action: _dlq.Action.Discard})

    try:
        assert kafka_suite.connection(names.channel_keep)[_dlq.Field_Action] == _dlq.Action.Discard

        counts = kafka_suite.run_dlq_rule()
        assert counts[names.channel_keep] == 1, counts
        assert kafka_suite.dlq(names.channel_keep)['messages'] == []

    finally:
        kafka_suite.edit_connection(names.channel_keep, **{_dlq.Field_Action: _dlq.Action.Keep})

# ################################################################################################################################

def test_the_delivery_page_lists_searches_shows_and_acts_on_the_dlq(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ The channel's delivery page lists its DLQ, a search matches a payload, the details hold the exception class,
    the cid and the Kafka position, and retry and discard from the page do what the DLQ services do.
    """
    landed, message = send_to_dlq(kafka_suite, names.channel_dlq, names.topic_dlq, Receiver, partition=1)
    document = message['document']
    payload = document[Key_Request][Key_Data]

    page = kafka_suite.dlq_page(names.channel_dlq)

    assert page['conn_name'] == names.channel_dlq
    assert page['has_queue'] is False
    assert page['dlq_depth'] == len(kafka_suite.dlq(names.channel_dlq)['messages'])
    assert page['dlq_settings'][_dlq.Field_Action] == _dlq.Action.Keep

    rows = {elem['msg_id']: elem for elem in page['items']}
    row = rows[message['msg_id']]

    assert row['cid'] == document[Key_CID]
    assert row['attempts'] == Max_Retries + 1
    assert row['rounds'] == 0
    assert row['destination'] == Receiver
    assert row['reason'] == PubSub.Outgoing.DLQ_Reason_Retries_Exhausted
    assert 'failed on purpose' in row['error']

    # A search matches the payload
    found = kafka_suite.dlq_page(names.channel_dlq, query=payload)
    assert found['total'] == 1
    assert found['items'][0]['msg_id'] == message['msg_id']

    # The details window
    detail = kafka_suite.dlq_page_message(names.channel_dlq, message['msg_id'])

    assert detail['document'] == document
    assert detail['document'][Key_DLQ][Header_Error_Class] == 'ValueError'
    assert detail['document'][Key_CID] == document[Key_CID]
    assert detail['destination'] == Receiver

    facts = {elem['label']: elem['value'] for elem in detail['facts']}
    assert facts['Topic'] == names.topic_dlq
    assert facts['Partition'] == '1'
    assert facts['Offset'] == str(landed.offset)

    # Retry from the page delivers the message once the service works
    kafka_suite.set_behaviour(Receiver)
    _ = kafka_suite.dlq_page_action(names.channel_dlq, 'retry', [message['msg_id']])

    delivered = kafka_suite.wait_for_received(delivered_ok(payload))
    assert delivered[0]['cid'] == document[Key_CID]
    assert message['msg_id'] not in dlq_ids(kafka_suite, names.channel_dlq)

    # Discard from the page takes a message out for good
    _, message = send_to_dlq(kafka_suite, names.channel_dlq, names.topic_dlq, Receiver, partition=1)
    payload = message['document'][Key_Request][Key_Data]

    _ = kafka_suite.dlq_page_action(names.channel_dlq, 'discard', [message['msg_id']])
    assert message['msg_id'] not in dlq_ids(kafka_suite, names.channel_dlq)

    kafka_suite.set_behaviour(Receiver)
    kafka_suite.not_received(delivered_ok(payload), within=Quiet_Time)

# ################################################################################################################################

def test_the_dlq_survives_a_restart_a_rename_and_goes_away_with_the_channel(kafka_suite:'KafkaSuite', names:'Names') -> 'None':
    """ A message in a channel's DLQ is still there after a server restart and the rule still acts on it, a renamed channel
    takes its DLQ along, and a deleted channel leaves no DLQ topic, no sub key and no recv stream behind.
    """
    _, message = send_to_dlq(kafka_suite, names.channel_lifecycle, names.topic_lifecycle, Receiver)
    payload = message['document'][Key_Request][Key_Data]
    cid = message['document'][Key_CID]

    dlq_before = kafka_suite.dlq(names.channel_lifecycle)

    # The restart resets the receivers too, so the one here works again
    kafka_suite.restart_server()

    dlq_after = kafka_suite.dlq(names.channel_lifecycle)
    assert dlq_after['sub_key'] == dlq_before['sub_key']
    assert dlq_after['topic_name'] == dlq_before['topic_name']
    assert [elem['msg_id'] for elem in dlq_after['messages']] == [message['msg_id']]

    # The restored DLQ is one the rule acts on
    counts = kafka_suite.run_dlq_rule()
    assert counts[names.channel_lifecycle] == 1, counts

    delivered = kafka_suite.wait_for_received(delivered_ok(payload))
    assert delivered[0]['cid'] == cid
    assert kafka_suite.dlq(names.channel_lifecycle)['messages'] == []

    # A renamed channel takes its DLQ along
    _, message = send_to_dlq(kafka_suite, names.channel_lifecycle, names.topic_lifecycle, Receiver)
    new_name = kafka_suite.new_name('channel.renamed')

    kafka_suite.edit_connection(names.channel_lifecycle, name=new_name)

    connection = kafka_suite.connection(new_name)
    channel_id = connection['id']

    renamed = kafka_suite.dlq(new_name)
    assert renamed['sub_key'] == dlq_before['sub_key']
    assert renamed['topic_name'] != dlq_before['topic_name']
    assert new_name.lower() in renamed['topic_name']
    assert [elem['msg_id'] for elem in renamed['messages']] == [message['msg_id']]

    # A deleted channel leaves nothing behind
    kafka_suite.set_behaviour(Receiver)
    kafka_suite.delete_connection(new_name)

    assert kafka_suite.topic_subscribers(renamed['topic_name']) == []
    assert kafka_suite.redis.exists(kafka_suite.recv_stream(channel_id)) == 0

    queues = kafka_suite.client.invoke('zato.pubsub.outgoing.get-queue-list')['items']
    assert not [elem for elem in queues if elem['conn_type'] == InboundType.KAFKA and elem['conn_id'] == channel_id], queues

# ################################################################################################################################
# ################################################################################################################################
