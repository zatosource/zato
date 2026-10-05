# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The server's listeners for the channels the queue bridge consumes.

# stdlib
from base64 import b64decode, b64encode
from json import dumps, loads
from logging import getLogger
from time import monotonic
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.queue import Queue

# Zato
from zato.common.api import DATA_FORMAT, GENERIC, HTTP_SOAP, KAFKA, PubSub
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource
from zato.common.pubsub.delivery import deliver_with_policy, DeliveryExhausted, DeliveryInterrupted, wait_between_rounds
from zato.common.pubsub.dlq import move_to_dlq
from zato.common.pubsub.outgoing import Attempts_None, build_envelope, InboundType, Key_Data, Key_Headers, Key_Is_Base64, \
    Key_Service
from zato.common.util.api import new_cid_server
from zato.common.util.retry import RetryPolicy
from zato.server.queue_bridge.client import get_recv_stream

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import any_, anydict, anylist, anynone, anytuple, stranydict, strdict, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_consumer = KAFKA.Consumer
_header = KAFKA.Header
_routing = KAFKA.Routing
_retry = HTTP_SOAP.Retry

_channel_kafka = GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA

# The consumer group and consumer every channel listener reads its stream as
Group_Name = 'server-recv'
Consumer_Name = 'server-recv-0'

# The stream ids of pending entries and of new ones
Read_Pending = '0'
Read_New = '>'

# How many entries one read brings back and how long it blocks, in milliseconds
Read_Count = 10
Read_Block_Ms = 1000

# How long the listener waits after an error
_error_sleep = PubSub.Delivery.Fetch_Error_Sleep

# How often, at most, a failing listener logs a reminder, in seconds
_error_log_interval = 60.0

# Why a round of attempts was interrupted
Interrupt_Stopped = 'stopped'

# A message that cannot be decoded counts as one failed attempt
Attempts_Poison = 1

# ################################################################################################################################
# ################################################################################################################################

def decode_payload(payload:'bytes') -> 'anytuple':
    """ A message's payload as the text an envelope stores and whether that text is base64.
    """
    try:
        out = (payload.decode('utf8'), False)
    except UnicodeDecodeError:
        out = (b64encode(payload).decode('ascii'), True)

    return out

# ################################################################################################################################

def encode_payload(request:'stranydict') -> 'bytes':
    """ The bytes a service is invoked with, out of what an envelope stores.
    """
    data = request[Key_Data]

    if request[Key_Is_Base64]:
        out = b64decode(data)
    else:
        out = data.encode('utf8')

    return out

# ################################################################################################################################

def build_channel_request(service:'str', payload:'bytes', headers:'strdict') -> 'stranydict':
    """ The request part of a channel message's envelope.
    """
    data, is_base64 = decode_payload(payload)

    out = {
        Key_Service: service,
        Key_Data: data,
        Key_Is_Base64: is_base64,
        Key_Headers: headers,
    }

    return out

# ################################################################################################################################

def invoke_channel_service(server:'ParallelServer', cid:'str', service:'str', payload:'bytes', headers:'strdict') -> 'any_':
    """ Invokes the service a channel's message was routed to, the headers are what the service reads as self.request.headers.
    """
    request_ctx = {'zato.request.headers': headers}
    out = server.invoke(service, payload, data_format=DATA_FORMAT.JSON, request_ctx=request_ctx, cid=cid)

    return out

# ################################################################################################################################

def invoke_kafka_service(server:'ParallelServer', cid:'str', service:'str', payload:'bytes', headers:'strdict') -> 'any_':
    """ One attempt at the service a Kafka channel's message was routed to, recorded in the audit log under the message's cid,
    so that a replay from the DLQ lines up with the first attempts.
    """
    start = monotonic()

    try:
        out = invoke_channel_service(server, cid, service, payload, headers)
    except Exception as e:
        _audit_kafka_attempt(server, cid, service, payload, headers, start, AuditOutcome.Error, str(e))
        raise
    else:
        _audit_kafka_attempt(server, cid, service, payload, headers, start, AuditOutcome.OK, '')
        return out

# ################################################################################################################################

def _audit_kafka_attempt(
    server:'ParallelServer',
    cid:'str',
    service:'str',
    payload:'bytes',
    headers:'strdict',
    start:'float',
    outcome:'str',
    status:'str',
    ) -> 'None':
    """ Records one attempt at a Kafka channel's service - the channel is the object, the topic is the endpoint.
    """
    audit_log = server.service_audit_log

    if not audit_log:
        return

    data, _ = decode_payload(payload)
    duration_ms = int((monotonic() - start) * 1000)

    attrs = {
        _header.Topic: headers.get(_header.Topic, ''),
        _header.Partition: headers.get(_header.Partition, ''),
        _header.Offset: headers.get(_header.Offset, ''),
        Key_Service: service,
    }

    _ = audit_log.insert(
        AuditSource.Kafka_Channel,
        AuditEvent.Message_Received,
        headers.get(_header.Channel, ''),
        cid=cid,
        endpoint=headers.get(_header.Topic, ''),
        size=len(payload),
        outcome=outcome,
        status=status,
        duration_ms=duration_ms,
        attrs=attrs,
        bodies={AuditBody.Request: data},
    )

# ################################################################################################################################

def invoke_channel_request(server:'ParallelServer', cid:'str', request:'stranydict') -> 'any_':
    """ Invokes the service of a stored channel message.
    """
    out = invoke_kafka_service(server, cid, request[Key_Service], encode_payload(request), request[Key_Headers])
    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_routing(value:'str') -> 'anylist':
    """ The routing rules of a channel as a list, out of the stored JSON text.
    """
    if not value:
        return []

    out = loads(value)
    return out

# ################################################################################################################################

def route_message(rules:'anylist', default_service:'str', topic:'str', headers:'strdict') -> 'str':
    """ The service a message goes to - the first rule it matches picks it, otherwise the channel's own service.
    """
    for rule in rules:

        rule_topic = rule[_routing.Key_Topic]
        if rule_topic and rule_topic != topic:
            continue

        header_name = rule[_routing.Key_Header_Name]
        if header_name:

            if header_name not in headers:
                continue

            header_value = rule[_routing.Key_Header_Value]
            if header_value and headers[header_name] != header_value:
                continue

        out = rule[_routing.Key_Service]
        return out

    out = default_service
    return out

# ################################################################################################################################
# ################################################################################################################################

class ChannelListener:
    """ One greenlet reading the recv stream of one channel the queue bridge consumes.
    """

    def __init__(self, server:'ParallelServer', config:'anydict') -> 'None':
        self.server = server
        self.channel_id = config['id']
        self.stream = get_recv_stream(self.channel_id)
        self.is_kafka = config['type_'] == _channel_kafka

        self.config:'anydict' = {}
        self.routing:'anylist' = []
        self.policy:'RetryPolicy'
        self.update_config(config)

        self.redis:'Redis' = server._queue_bridge.new_redis_conn()
        self._greenlet:'anynone' = None
        self._is_stopped = False

        # One lane per partition, so that a message stuck in its rounds holds up its own partition only
        self._lanes:'dict[anytuple, Queue]' = {}
        self._lane_greenlets:'anylist' = []

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'ChannelListener({self.channel_id}/{self.config["name"]} at {hex(id(self))})'

# ################################################################################################################################

    def update_config(self, config:'anydict') -> 'None':
        """ Takes the channel's configuration, an edit applies from the next message on.
        """
        self.config = config
        self.policy = RetryPolicy.from_config(config, _retry)

        if self.is_kafka:
            self.routing = parse_routing(config[_consumer.Field_Routing])

# ################################################################################################################################

    def ensure_group(self) -> 'None':
        """ Creates the stream and its consumer group, from the stream's start.
        """
        self.server._queue_bridge.ensure_stream_group(self.redis, self.stream, Group_Name, Read_Pending)

# ################################################################################################################################

    def start(self) -> 'None':
        self.ensure_group()
        self._greenlet = spawn(self._loop)
        logger.info('Channel listener started for `%s` (%s), stream `%s`', self.config['name'], self.channel_id, self.stream)

# ################################################################################################################################

    def stop(self) -> 'None':
        self._is_stopped = True

        if self._greenlet:
            self._greenlet.kill()
            self._greenlet = None

        for greenlet in self._lane_greenlets:
            greenlet.kill()

        self._lane_greenlets.clear()
        self._lanes.clear()

        logger.info('Channel listener stopped for `%s` (%s)', self.config['name'], self.channel_id)

# ################################################################################################################################

    def delete_stream(self) -> 'None':
        """ Removes the channel's stream.
        """
        try:
            _ = self.redis.delete(self.stream)
        except Exception:
            logger.warning('Could not delete stream `%s`: %s', self.stream, format_exc())

# ################################################################################################################################

    def _loop(self) -> 'None':
        """ Reads the stream until stopped - first the pending entries, then new ones.
        """
        read_id = Read_Pending

        error_since = 0.0
        last_logged = 0.0

        while not self._is_stopped:
            try:
                result = self.redis.xreadgroup(
                    groupname=Group_Name,
                    consumername=Consumer_Name,
                    streams={self.stream: read_id},
                    count=Read_Count,
                    block=Read_Block_Ms,
                )

                if error_since:
                    logger.info('Channel listener recovered for `%s` (%s)', self.config['name'], self.channel_id)
                    error_since = 0.0

                # No pending entries are left, read new ones from now on.
                if read_id == Read_Pending:
                    if not self._has_entries(result):
                        read_id = Read_New
                        continue

                if not result:
                    continue

                for _stream_name, messages in result:
                    for msg_id, fields in messages:

                        if self._is_stopped:
                            return

                        self._dispatch(msg_id, fields)

            except Exception as exc:
                error_since, last_logged = self._on_read_error(exc, error_since, last_logged)
                sleep(_error_sleep)

# ################################################################################################################################

    def _dispatch(self, msg_id:'str', fields:'strdict') -> 'None':
        """ Hands one entry to the lane of its partition - a Kafka message waits behind the ones of its own partition only,
        while anything else is handled in the order it was read in.
        """
        if self.is_kafka:
            lane_key = self._get_lane_key(fields)
        else:
            lane_key = ()

        if not (lane := self._lanes.get(lane_key)):
            lane = Queue()
            self._lanes[lane_key] = lane
            self._lane_greenlets.append(spawn(self._run_lane, lane))

        lane.put((msg_id, fields))

# ################################################################################################################################

    def _get_lane_key(self, fields:'strdict') -> 'anytuple':
        """ The topic and partition an entry came from, or an empty key for one whose headers cannot be read.
        """
        try:
            headers = loads(fields['headers'])
            out = (fields['topic'], int(headers[_header.Partition]))
        except Exception:
            out = ()

        return out

# ################################################################################################################################

    def _run_lane(self, lane:'Queue') -> 'None':
        """ Handles the entries of one lane, one after another, until stopped.
        """
        while not self._is_stopped:
            msg_id, fields = lane.get()
            self._handle_entry(msg_id, fields)

# ################################################################################################################################

    def _has_entries(self, result:'any_') -> 'bool':
        """ Whether a read brought any entries back.
        """
        if not result:
            return False

        for _stream_name, messages in result:
            if messages:
                return True

        return False

# ################################################################################################################################

    def _on_read_error(self, exc:'Exception', error_since:'float', last_logged:'float') -> 'anytuple':
        """ A missing stream or group is recreated. Any other error logs the full traceback when the condition starts,
        then a one-line reminder at most once a minute.
        """
        now = monotonic()
        error_text = str(exc)
        is_missing_group = 'NOGROUP' in error_text
        name = self.config['name']

        if not error_since:
            error_since = now
            last_logged = now
            if is_missing_group:
                logger.warning('Recreating stream and group for channel `%s` (%s): %s', name, self.channel_id, error_text)
            else:
                logger.warning('Error in channel listener `%s` (%s): %s', name, self.channel_id, format_exc())

        elif now - last_logged >= _error_log_interval:
            last_logged = now
            elapsed = int(now - error_since)
            logger.warning('Channel listener `%s` (%s) still failing after %ss: %s', name, self.channel_id, elapsed, exc)

        if is_missing_group:
            try:
                self.ensure_group()
            except Exception:
                pass

        out = (error_since, last_logged)
        return out

# ################################################################################################################################

    def _handle_entry(self, msg_id:'str', fields:'strdict') -> 'None':
        """ Handles one entry until it is resolved, an error of the handling itself makes the entry wait and go again.
        """
        while not self._is_stopped:
            try:
                if self.is_kafka:
                    self._handle_kafka(msg_id, fields)
                else:
                    self._handle_ibm_mq(msg_id, fields)

                return

            except DeliveryInterrupted:
                return

            except Exception:
                logger.warning('Could not handle entry `%s` of `%s`, e:`%s`', msg_id, self.stream, format_exc())
                sleep(_error_sleep)

# ################################################################################################################################

    def _ack(self, msg_id:'str') -> 'None':
        _ = self.redis.xack(self.stream, Group_Name, msg_id)

# ################################################################################################################################

    def _should_continue(self) -> 'str':
        """ A round of attempts stops between two of them once the listener is stopped.
        """
        if self._is_stopped:
            out = Interrupt_Stopped
        else:
            out = ''

        return out

# ################################################################################################################################

    def _handle_kafka(self, msg_id:'str', fields:'strdict') -> 'None':
        """ One message of a Kafka channel, from the stream entry to its commit.
        """
        config = self.config
        channel_name = fields['channel_name']
        topic = fields['topic']

        # A message the entry cannot be decoded into is poison - it goes to the DLQ as it is and the next one follows.
        try:
            payload = b64decode(fields['payload'], validate=True)
            headers:'strdict' = loads(fields['headers'])
            partition = int(headers[_header.Partition])
            offset = int(headers[_header.Offset])
        except Exception as e:
            self._handle_poison(msg_id, fields, e)
            return

        headers[_header.Channel] = channel_name

        def resolve() -> 'None':
            self.server._queue_bridge.commit_offset(self.channel_id, topic, partition, offset)
            self._ack(msg_id)

        # A tombstone goes to the service only if the channel says so ..
        if headers[_header.Is_Tombstone] == _header.Is_Tombstone_True:
            if not config[_consumer.Field_Should_Deliver_Tombstones]:
                logger.info('Skipping tombstone from `%s` at %s/%s, channel `%s`', topic, partition, offset, channel_name)
                resolve()
                return

        # .. a message no rule and no service takes goes nowhere ..
        service = route_message(self.routing, config['service'], topic, headers)

        if not service:
            logger.info('Skipping message from `%s` at %s/%s, channel `%s` has no service for it',
                topic, partition, offset, channel_name)
            resolve()
            return

        # .. and a repeat of a message that was already delivered is not delivered again.
        dedup_key = self._get_dedup_key(headers)

        if dedup_key:
            if self.redis.exists(dedup_key):
                logger.info('Skipping duplicate from `%s` at %s/%s, channel `%s`, key `%s`',
                    topic, partition, offset, channel_name, dedup_key)
                resolve()
                return

        # Each message has a correlation id of its own.
        cid = new_cid_server()

        request = build_channel_request(service, payload, headers)

        def attempt() -> 'None':
            _ = invoke_kafka_service(self.server, cid, service, payload, headers)

        # The rounds go on until the message is delivered or moved to the DLQ.
        while not self._is_stopped:

            try:
                deliver_with_policy(self.policy, Attempts_None, cid, channel_name, attempt, self._should_continue)

            except DeliveryExhausted as e:

                envelope = build_envelope(InboundType.KAFKA, self.channel_id, channel_name, cid, e.attempts, request)

                source = {
                    _header.Topic: topic,
                    _header.Partition: partition,
                    _header.Offset: offset,
                }

                if move_to_dlq(self.server, cid, envelope, e, source_topic=topic, source=source):
                    resolve()
                    return

                logger.warning('Message from `%s` at %s/%s of channel `%s` failed, cid `%s`, next round in %ss: %s',
                    topic, partition, offset, channel_name, cid, PubSub.Delivery.Retry_Round_Wait, e.error)

                wait_between_rounds()

            else:
                if dedup_key:
                    _ = self.redis.set(dedup_key, '1', ex=self._get_dedup_ttl())

                resolve()
                return

# ################################################################################################################################

    def _handle_poison(self, msg_id:'str', fields:'strdict', error:'Exception') -> 'None':
        """ An entry that cannot be decoded goes to the DLQ as one failed attempt, with what little is known of it,
        its offset is committed if the headers said where it was, and the listener goes on with the next entry.
        """
        channel_name = fields['channel_name']
        topic = fields['topic']
        cid = new_cid_server()

        headers:'strdict' = {
            _header.Channel: channel_name,
            _header.Topic: topic,
        }

        # The position is known only if the headers themselves could be read.
        try:
            raw_headers = loads(fields['headers'])
            partition = int(raw_headers[_header.Partition])
            offset = int(raw_headers[_header.Offset])
        except Exception:
            source = None
        else:
            headers[_header.Partition] = str(partition)
            headers[_header.Offset] = str(offset)
            source = {
                _header.Topic: topic,
                _header.Partition: partition,
                _header.Offset: offset,
            }

        # The payload is stored as the bridge sent it, the one thing that is certain about it.
        request = {
            Key_Service: fields['service'] or self.config['service'],
            Key_Data: fields['payload'],
            Key_Is_Base64: False,
            Key_Headers: headers,
        }

        exhausted = DeliveryExhausted(f'Cannot decode message: {error}', Attempts_Poison, error.__class__.__name__)
        envelope = build_envelope(InboundType.KAFKA, self.channel_id, channel_name, cid, Attempts_Poison, request)

        if not move_to_dlq(self.server, cid, envelope, exhausted, source_topic=topic, source=source):
            logger.warning('Dropping message `%s` of channel `%s` from `%s` that cannot be decoded and has no DLQ, cid `%s`: %s',
                msg_id, channel_name, topic, cid, error)

        if source:
            self.server._queue_bridge.commit_offset(self.channel_id, topic, source[_header.Partition], source[_header.Offset])

        self._ack(msg_id)

# ################################################################################################################################

    def _get_dedup_key(self, headers:'strdict') -> 'strnone':
        """ The Redis key of this message once delivered, or None for a channel without deduplication
        or a message without the header.
        """
        dedup_header = self.config[_consumer.Field_Dedup_Header]

        if not dedup_header:
            return None

        if dedup_header not in headers:
            return None

        out = f'{_consumer.Dedup_Key_Prefix}{self.channel_id}:{headers[dedup_header]}'
        return out

# ################################################################################################################################

    def _get_dedup_ttl(self) -> 'int':
        """ How long a delivered message's dedup value is kept, in seconds.
        """
        out = self.config[_consumer.Field_Dedup_TTL]
        return out

# ################################################################################################################################

    def _handle_ibm_mq(self, msg_id:'str', fields:'strdict') -> 'None':
        """ One message of an IBM MQ channel - invoked once.
        """
        service_name = fields['service']
        payload = b64decode(fields['payload'])
        headers = loads(fields['headers'])

        try:
            response = invoke_channel_service(self.server, new_cid_server(), service_name, payload, headers)

            # The response goes back to the reply-to queue, if there is one.
            reply_to_queue = fields['reply_to_queue']
            if reply_to_queue and response:
                if isinstance(response, bytes):
                    reply_data = response
                elif isinstance(response, str):
                    reply_data = response.encode('utf8')
                else:
                    reply_data = dumps(response).encode('utf8')

                _ = self.server._queue_bridge.send_reply(
                    fields['channel_name'],
                    reply_to_queue,
                    fields['reply_to_queue_manager'],
                    fields['message_id'],
                    reply_data,
                )

        except Exception:
            logger.warning('Could not invoke `%s` for IBM MQ channel `%s`, e:`%s`',
                service_name, fields['channel_name'], format_exc())

        self._ack(msg_id)

# ################################################################################################################################
# ################################################################################################################################

class ChannelListeners:
    """ The listeners of every channel the queue bridge consumes, by channel id.
    """

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self._listeners:'anydict' = {}

# ################################################################################################################################

    def start(self, config:'anydict') -> 'None':
        """ Starts the listener of one channel, replacing the one it may already have.
        """
        channel_id = config['id']

        if listener := self._listeners.pop(channel_id, None):
            listener.stop()

        listener = ChannelListener(self.server, config)
        self._listeners[channel_id] = listener
        listener.start()

# ################################################################################################################################

    def update(self, config:'anydict') -> 'None':
        """ Gives one channel's listener the edited configuration, starting the listener if the channel did not have one.
        """
        channel_id = config['id']

        if listener := self._listeners.get(channel_id):
            listener.update_config(config)
        else:
            self.start(config)

# ################################################################################################################################

    def stop(self, channel_id:'int', *, needs_stream_delete:'bool'=False) -> 'None':
        """ Stops the listener of one channel.
        """
        if listener := self._listeners.pop(channel_id, None):
            listener.stop()

            if needs_stream_delete:
                listener.delete_stream()

# ################################################################################################################################

    def stop_all(self) -> 'None':
        for channel_id in list(self._listeners):
            self.stop(channel_id)

# ################################################################################################################################

    def sync(self, configs:'anylist') -> 'None':
        """ Makes the listeners match a full list of channels - after a config reload, a channel that is new
        gets a listener, one that is known gets the configuration it has now and one that is gone is stopped.
        """
        current_ids = set()

        for config in configs:
            current_ids.add(config['id'])
            self.update(config)

        for channel_id in list(self._listeners):
            if channel_id not in current_ids:
                self.stop(channel_id)

# ################################################################################################################################
# ################################################################################################################################
