# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from logging import getLogger

# redis
from redis.exceptions import ResponseError

# Zato
from zato.common.api import PubSub
from zato.common.marshal_.api import Model
from zato.common.pubsub.disk_store import DiskMessageStore
from zato.common.typing_ import cast_
from zato.common.util.api import new_msg_id, utcnow
from zato.server.metrics import zato_pubsub_messages_delivered_total, zato_pubsub_messages_published_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from redis.typing import EncodableT, FieldT
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist, strnone, strset

    browse_result = tuple['anylist', str]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority       = PubSub.Message.Priority_Default
_default_expiration     = PubSub.Message.Default_Expiration
_default_max_messages   = PubSub.Message.Default_Max_Messages
_default_max_len        = PubSub.Message.Default_Max_Len
_default_data_preview_len = PubSub.Message.Data_Preview_Len
_default_stream_max_len = 100_000
_default_page_size      = 50

_browse_state_handlers = {
    'pending':   '_browse_pending',
    'all':       '_browse_all',
    'delivered': '_browse_delivered',
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PublishResult:
    msg_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Stream_Prefix      = 'zato:pubsub:stream:'
    Subs_Prefix        = 'zato:pubsub:subs:'
    Topic_Subs_Prefix  = 'zato:pubsub:topic_subs:'
    Pending_Prefix     = 'zato:pubsub:pending:'
    Pending_Expiry_Key = 'zato:pubsub:pending_expiry'
    Sub_Pending_Prefix = 'zato:pubsub:sub_pending:'

# ################################################################################################################################
# ################################################################################################################################

_lua_unsub_script = """
local sub_pending_key = KEYS[1]
local expiry_key = KEYS[2]
local sub_key = ARGV[1]
local pending_prefix = ARGV[2]

local data_refs = redis.call('SMEMBERS', sub_pending_key)
local deleted_refs = {}

for _, data_ref in ipairs(data_refs) do
    local pending_key = pending_prefix .. data_ref
    redis.call('SREM', pending_key, sub_key)
    local remaining = redis.call('SCARD', pending_key)
    if remaining == 0 then
        redis.call('DEL', pending_key)
        redis.call('ZREM', expiry_key, data_ref)
        table.insert(deleted_refs, data_ref)
    end
end

redis.call('DEL', sub_pending_key)
return deleted_refs
"""

# ################################################################################################################################
# ################################################################################################################################

_lua_pending_depths_script = """

-- Extract a named field from a flat key-value array returned by XINFO ..
local function get_field(info, field_name)
    for field_index = 1, #info, 2 do
        if info[field_index] == field_name then
            return info[field_index + 1]
        end
    end

    -- .. the field was not found.
    return false
end

-- Find a consumer group by name in XINFO GROUPS output ..
local function get_group_lag(groups, group_name)

    -- .. walk each group entry ..
    for group_index = 1, #groups do
        local group = groups[group_index]
        local name = get_field(group, 'name')

        -- .. and return the lag for the matching group.
        if name == group_name then
            return get_field(group, 'lag')
        end
    end

    -- .. the group was not found.
    return false
end

-- Get the PEL (Pending Entries List) count for a consumer group ..
-- .. PEL is Redis's internal list of messages delivered via XREADGROUP but not yet acked.
-- .. XPENDING summary returns a 4-element array where index [1] is the count.
-- .. The call can fail if the stream or group does not exist.
local function get_pel_count(stream_key, group_name)
    local ok, pending = pcall(redis.call, 'XPENDING', stream_key, group_name)
    if not ok then
        return 0
    end
    return pending[1]
end

-- Get the unread backlog count for a consumer group ..
-- .. these are messages in the stream that the group has not consumed yet.
-- .. XINFO GROUPS returns a 'lag' field (Redis 7+) with this count.
-- .. The call can fail if the stream does not exist ..
-- .. and 'lag' can be nil (false in Lua) after XDEL or stream trimming.
local function get_lag_count(stream_key, group_name)
    local ok, groups = pcall(redis.call, 'XINFO', 'GROUPS', stream_key)
    if not ok then
        return 0
    end

    local lag = get_group_lag(groups, group_name)
    if lag == false then
        return 0
    end
    return lag
end

-- Compute pending depths for all (stream_key, group_name) pairs ..
-- .. ARGV contains repeated pairs: stream_key_1, group_name_1, stream_key_2, group_name_2, ...
local result = {}

for pair_index = 1, #ARGV, 2 do
    local stream_key = ARGV[pair_index]
    local group_name = ARGV[pair_index + 1]

    -- .. get delivered-but-unacked count ..
    local pel = get_pel_count(stream_key, group_name)

    -- .. get not-yet-delivered count ..
    local lag = get_lag_count(stream_key, group_name)

    -- .. and sum them into the total pending depth for this pair.
    table.insert(result, pel + lag)
end

return result
"""

# ################################################################################################################################
# ################################################################################################################################

class RedisPubSubBackend:
    """ Redis Streams-based pub/sub backend.
    """

    def __init__(self, redis_client:'Redis', disk_store:'DiskMessageStore', server:'any_'=None) -> 'None':
        self.redis = redis_client
        self.disk_store = disk_store
        self.server = server
        self._lua_unsub_sha:'str' = cast_('str', self.redis.script_load(_lua_unsub_script))
        self._lua_pending_depths_sha:'str' = cast_('str', self.redis.script_load(_lua_pending_depths_script))

# ################################################################################################################################

    def _get_stream_key(self, topic_name:'str') -> 'str':
        out = f'{ModuleCtx.Stream_Prefix}{topic_name}'
        return out

# ################################################################################################################################

    def get_stream_key(self, topic_name:'str') -> 'str':
        """ Returns the Redis stream key for a given topic name.
        """
        out = self._get_stream_key(topic_name)
        return out

# ################################################################################################################################

    def _get_subs_key(self, sub_key:'str') -> 'str':
        out = f'{ModuleCtx.Subs_Prefix}{sub_key}'
        return out

# ################################################################################################################################

    def _get_topic_subs_key(self, topic_name:'str') -> 'str':
        out = f'{ModuleCtx.Topic_Subs_Prefix}{topic_name}'
        return out

# ################################################################################################################################

    def _get_pending_key(self, data_ref:'str') -> 'str':
        out = f'{ModuleCtx.Pending_Prefix}{data_ref}'
        return out

# ################################################################################################################################

    def _get_sub_pending_key(self, sub_key:'str') -> 'str':
        out = f'{ModuleCtx.Sub_Pending_Prefix}{sub_key}'
        return out

# ################################################################################################################################

    def publish(
        self,
        topic_name:'str',
        data:'any_',
        *,
        priority:'int'=_default_priority,
        expiration:'int'=_default_expiration,
        correl_id:'strnone'=None,
        in_reply_to:'strnone'=None,
        ext_client_id:'strnone'=None,
        publisher:'strnone'=None,
        pub_time:'strnone'=None,
    ) -> 'PublishResult':
        """ Publish a message to a topic stream.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        # .. generate message ID ..
        message_id = new_msg_id()

        # .. build timestamps ..
        now = utcnow()

        if pub_time:
            pub_time_iso = pub_time
        else:
            now_iso = now.isoformat()
            pub_time_iso = now_iso

        expiration_delta = timedelta(seconds=expiration)
        expiration_time = now + expiration_delta
        expiration_time_iso = expiration_time.isoformat()

        # .. serialize data ..
        data_class = ''

        if isinstance(data, str):
            serialized_data = data

        elif isinstance(data, Model):
            data_module = data.__class__.__module__
            data_class_name = data.__class__.__qualname__
            data_class = f'{data_module}.{data_class_name}'
            serialized_data = data.to_json().decode()

        else:
            serialized_data = json.dumps(data)

        # .. store the payload on disk ..
        encrypt = self.server.encrypt_at_rest if self.server else False
        data_ref = self.disk_store.store(message_id, topic_name, serialized_data, data_class, encrypt=encrypt)

        # .. build the message with a reference to the disk file ..
        recv_time_iso = now.isoformat()
        data_size = len(serialized_data)
        data_preview = serialized_data[:_default_data_preview_len]

        message:'dict[FieldT, EncodableT]' = {
            'msg_id': message_id,
            'data_ref': data_ref,
            'data_size': data_size,
            'data_preview': data_preview,
            'topic_name': topic_name,
            'priority': str(priority),
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': recv_time_iso,
            'expiration': str(expiration),
            'expiration_time_iso': expiration_time_iso,
        }

        if correl_id:
            message['correl_id'] = correl_id

        if in_reply_to:
            message['in_reply_to'] = in_reply_to

        if ext_client_id:
            message['ext_client_id'] = ext_client_id

        if publisher:
            message['publisher'] = publisher

        # .. add to stream ..
        stream_key = self._get_stream_key(topic_name)
        redis_stream_id = self.redis.xadd(stream_key, message, maxlen=_default_stream_max_len)

        logger.info('Published to stream -> message_id:%s, data_ref:%s, stream_key:%s, redis_stream_id:%s',
            message_id, data_ref, stream_key, redis_stream_id)

        # .. populate the pending subscriber set and index by expiration time ..
        topic_subs_key = self._get_topic_subs_key(topic_name)
        subscriber_keys:'strset' = cast_('strset', self.redis.smembers(topic_subs_key))

        # .. if there are any subscribers, record which ones still need this message ..
        if subscriber_keys:
            pending_key = self._get_pending_key(data_ref)
            _ = self.redis.sadd(pending_key, *subscriber_keys)

            # .. populate the reverse index for each subscriber ..
            for sk in subscriber_keys:
                sub_pending_key = self._get_sub_pending_key(sk)
                _ = self.redis.sadd(sub_pending_key, data_ref)

            # .. and index the message by its expiration time for the cleanup job ..
            expiration_timestamp = expiration_time.timestamp()
            _ = self.redis.zadd(ModuleCtx.Pending_Expiry_Key, {data_ref: expiration_timestamp})

            subscriber_count = len(subscriber_keys)
            logger.info('Populated pending set -> data_ref:%s, subscriber_count:%d, expiration_timestamp:%.1f',
                data_ref, subscriber_count, expiration_timestamp)
        # .. update the publish counter and return the result.
        counter = zato_pubsub_messages_published_total.labels(topic_name=topic_name)
        _ = counter.inc()

        out = PublishResult()
        out.msg_id = message_id

        return out

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Subscribe a user to a topic.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        # .. build key names ..
        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        # .. add topic to subscriber's set ..
        _ = self.redis.sadd(subs_key, topic_name)

        # .. add subscriber to topic's set ..
        _ = self.redis.sadd(topic_subs_key, sub_key)

        # .. create consumer group if not exists.
        try:
            _ = self.redis.xgroup_create(stream_key, sub_key, id='0', mkstream=True)
        except ResponseError as error:
            if 'BUSYGROUP' not in error.args[0]:
                raise

# ################################################################################################################################

    def unsubscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Unsubscribe a user from a topic.
        """

        # Normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        # .. build key names ..
        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        # .. remove topic from subscriber's set ..
        _ = self.redis.srem(subs_key, topic_name)

        # .. remove subscriber from topic's set ..
        _ = self.redis.srem(topic_subs_key, sub_key)

        # .. eagerly clean up all pending messages for this subscriber via Lua script ..
        sub_pending_key = self._get_sub_pending_key(sub_key)
        deleted_refs:'anylist' = cast_('anylist', self.redis.evalsha(
            self._lua_unsub_sha, 2,
            sub_pending_key, ModuleCtx.Pending_Expiry_Key,
            sub_key, ModuleCtx.Pending_Prefix
        ))

        # .. delete disk files for messages that no longer have any pending subscribers ..
        for data_ref in deleted_refs:
            self.disk_store.delete(data_ref)

        if deleted_refs:
            logger.info('unsubscribe deleted files -> sub_key:%s, count:%d',
                sub_key, len(deleted_refs))

        # .. check if subscriber has any remaining subscriptions ..
        remaining = self.redis.scard(subs_key)

        # .. if no remaining subscriptions, destroy the consumer group.
        if remaining == 0:
            try:
                _ = self.redis.xgroup_destroy(stream_key, sub_key)
            except ResponseError as e:
                logger.warning('xgroup_destroy failed -> stream_key:%s, sub_key:%s, error:%s', stream_key, sub_key, e)

# ################################################################################################################################

    def fetch_messages(
        self,
        sub_key:'str',
        max_messages:'int'=_default_max_messages,
        max_len:'int'=_default_max_len,
        block_ms:'int'=0,
        stream_id:'str'='>'
    ) -> 'anylist':
        """ Fetch messages for a subscriber from all subscribed topics.
        Does not acknowledge messages - the caller is responsible for calling
        ack_message after successful processing.
        """
        # Build the subscriber's key ..
        subs_key = self._get_subs_key(sub_key)

        # .. get all topics this subscriber is subscribed to ..
        topics:'strset' = cast_('strset', self.redis.smembers(subs_key))

        if not topics:
            return []

        # .. build streams dict for xreadgroup ..
        streams:'anydict' = {}

        for topic in topics:
            stream_key = self._get_stream_key(topic)
            streams[stream_key] = stream_id

        # .. read from all subscribed streams ..
        try:
            block_value = block_ms if block_ms else None

            result:'anylist' = cast_('anylist', self.redis.xreadgroup(
                groupname=sub_key,
                consumername=sub_key,
                streams=streams,
                count=max_messages,
                block=block_value
            ))

        except ResponseError as error:
            if 'NOGROUP' in error.args[0]:
                return []
            raise

        if not result:
            return []

        messages:'anylist' = []
        total_len = 0

        for stream_name, stream_messages in result:

            for redis_message_id, message_data in stream_messages:

                # .. message_data is already dict[str, str] because decode_responses=True ..
                decoded = message_data

                # .. check expiration - ack expired messages immediately and skip them ..
                expiration_time_iso = decoded['expiration_time_iso']

                normalized_expiration_iso = expiration_time_iso.replace('Z', '+00:00')
                expiration_time = datetime.fromisoformat(normalized_expiration_iso)

                now = utcnow()

                if now > expiration_time:
                    expired_data_ref = decoded['data_ref']
                    self.ack_message(stream_name, sub_key, redis_message_id, expired_data_ref)
                    continue

                # .. check max_len constraint using data_size from metadata ..
                data_len = int(decoded['data_size'])

                if total_len + data_len > max_len:
                    break

                total_len += data_len

                # .. load the actual payload from disk ..
                data_ref = decoded['data_ref']

                try:
                    load_result = self.disk_store.load(data_ref)
                except FileNotFoundError:
                    logger.warning('Orphaned message -> sub_key:%s, data_ref:%s, redis_id:%s - acking and skipping',
                        sub_key, data_ref, redis_message_id)
                    self.ack_message(stream_name, sub_key, redis_message_id, data_ref)
                    continue

                decoded['data'] = load_result.data
                decoded['data_class'] = load_result.data_class

                # .. convert priority and expiration from string to int once ..
                decoded['priority'] = int(decoded['priority'])
                decoded['expiration'] = int(decoded['expiration'])

                # .. store internal routing metadata for ack ..
                decoded['_redis_message_id'] = redis_message_id
                decoded['_stream_name'] = stream_name
                decoded['_data_ref'] = data_ref

                messages.append(decoded)

        # .. sort by priority desc, then by pub_time asc and return the page.
        def _sort_key(message:'anydict') -> 'tuple':
            negated_priority = -message['priority']
            pub_time = message['pub_time_iso']

            out = (negated_priority, pub_time)
            return out

        messages.sort(key=_sort_key)

        out = messages[:max_messages]
        return out

# ################################################################################################################################

    def ack_message(self, stream_name:'str', sub_key:'str', redis_message_id:'str', data_ref:'strnone'=None) -> 'None':
        """ Acknowledge a single message after successful processing.
        """
        # Acknowledge the message in the stream ..
        logger.info('ack_message -> sub_key:%s, stream_name:%s, redis_message_id:%s, data_ref:%s',
            sub_key, stream_name, redis_message_id, data_ref)

        _ = self.redis.xack(stream_name, sub_key, redis_message_id)

        # .. remove this subscriber from the message's pending set and the reverse index ..
        if data_ref:
            pending_key = self._get_pending_key(data_ref)

            _ = self.redis.srem(pending_key, sub_key)

            sub_pending_key = self._get_sub_pending_key(sub_key)
            _ = self.redis.srem(sub_pending_key, data_ref)

            # .. check if any subscribers still need this message ..
            remaining = self.redis.scard(pending_key)

            if remaining == 0:

                # .. no one needs this message anymore, delete everything.
                _ = self.redis.delete(pending_key)
                _ = self.redis.zrem(ModuleCtx.Pending_Expiry_Key, data_ref)
                self.disk_store.delete(data_ref)

                logger.info('ack_message deleted file -> data_ref:%s, sub_key:%s',
                    data_ref, sub_key)

            else:
                logger.info('ack_message pending remaining -> data_ref:%s, sub_key:%s, remaining:%s',
                    data_ref, sub_key, remaining)

# ################################################################################################################################

    def fetch_pending(self, sub_key:'str', max_messages:'int'=_default_max_messages) -> 'anylist':
        """ Fetch previously read but unacknowledged messages for a subscriber.
        Used on startup to retry messages that were not delivered before the process stopped.
        """
        return self.fetch_messages(sub_key, max_messages=max_messages, stream_id='0')

# ################################################################################################################################

    def format_messages_for_rest(self, messages:'anylist', sub_key:'str') -> 'anylist':
        """ Format raw messages into the {data, meta} structure expected by the REST API.
        Also acknowledges each message and increments delivery counters.
        """
        now = utcnow()

        out:'anylist' = []

        for message in messages:

            # Extract internal routing metadata ..
            redis_message_id = message.pop('_redis_message_id')
            stream_name = message.pop('_stream_name')
            data_ref = message.pop('_data_ref')

            data_raw = message.pop('data')

            # .. deserialize JSON data if possible ..
            try:
                data = json.loads(data_raw)
            except (json.JSONDecodeError, TypeError):
                data = data_raw

            data_size = len(data_raw)

            pub_time_iso = message['pub_time_iso']
            recv_time_iso = message['recv_time_iso']

            time_since_pub = self._compute_time_since(pub_time_iso, now)
            time_since_recv = self._compute_time_since(recv_time_iso, now)

            meta = {
                'topic_name': message['topic_name'],
                'size': data_size,
                'priority': message['priority'],
                'expiration': message['expiration'],
                'msg_id': message['msg_id'],
                'sub_key': sub_key,
                'pub_time_iso': pub_time_iso,
                'recv_time_iso': recv_time_iso,
                'expiration_time_iso': message['expiration_time_iso'],
                'time_since_pub': time_since_pub,
                'time_since_recv': time_since_recv,
            }

            if correl_id := message.get('correl_id'):
                meta['correl_id'] = correl_id

            if in_reply_to := message.get('in_reply_to'):
                meta['in_reply_to'] = in_reply_to

            if ext_client_id := message.get('ext_client_id'):
                meta['ext_client_id'] = ext_client_id

            out.append({
                'data': data,
                'meta': meta
            })

            # .. acknowledge and clean up the disk file ..
            self.ack_message(stream_name, sub_key, redis_message_id, data_ref)

            # .. update the delivery counter.
            counter = zato_pubsub_messages_delivered_total.labels(topic_name=message['topic_name'])
            _ = counter.inc()

        return out

# ################################################################################################################################

    @staticmethod
    def _compute_time_since(iso_timestamp:'str', now:'datetime') -> 'str':

        # Parse the ISO timestamp into a datetime ..
        normalized_iso = iso_timestamp.replace('Z', '+00:00')
        timestamp = datetime.fromisoformat(normalized_iso)

        # .. strip tzinfo from both sides so subtraction always works ..
        if timestamp.tzinfo:
            timestamp_naive = timestamp.replace(tzinfo=None)
        else:
            timestamp_naive = timestamp

        if now.tzinfo:
            now_naive = now.replace(tzinfo=None)
        else:
            now_naive = now

        # .. compute the delta, clamping negative values to zero.
        delta = now_naive - timestamp_naive

        if delta.total_seconds() < 0:
            delta = timedelta(0)

        out = str(delta)
        return out

# ################################################################################################################################

    def browse_messages(
        self,
        topic_name:'str',
        sub_key:'str',
        state:'str' = 'pending',
        cursor:'str' = '-',
        page_size:'int' = _default_page_size,
        needs_data:'bool' = False,
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Browse messages in a topic filtered by delivery state.
        Dispatches to a state-specific handler method.
        Returns (messages, next_cursor) for cursor-based pagination.
        When reverse=True, returns newest messages first.
        """
        handler_name = _browse_state_handlers[state]
        handler = getattr(self, handler_name)
        out = handler(topic_name, sub_key, cursor, page_size, needs_data, reverse)
        return out

# ################################################################################################################################

    def _browse_all(
        self,
        topic_name:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Returns all messages in the stream regardless of delivery state.
        """

        # Our response to produce
        out:'browse_result' = ([], '')

        # Normalize topic name ..
        topic_name = topic_name.lower()
        stream_key = self._get_stream_key(topic_name)

        # .. read a page from the stream ..
        if reverse:
            xrange_max = '+' if cursor == '-' else cursor
            xrange_result = self.redis.xrevrange(stream_key, max=xrange_max, count=page_size)
        else:
            xrange_result = self.redis.xrange(stream_key, min=cursor, count=page_size)

        raw_messages:'anylist' = cast_('anylist', xrange_result)

        # .. handle empty result ..
        if not raw_messages:
            return out

        messages = self._build_entries(raw_messages, needs_data)

        # .. stamp delivery status per message ..
        last_delivered_id = self._get_last_delivered_id(stream_key, sub_key)
        for msg in messages:
            msg['is_delivered'] = bool(last_delivered_id and msg['redis_stream_id'] <= last_delivered_id)

        # .. compute next_cursor ..
        next_cursor = self._compute_next_cursor(raw_messages, page_size)

        # .. and return the result.
        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def _get_last_delivered_id(self, stream_key:'str', group_name:'str') -> 'strnone':
        """ Returns the last-delivered-id for a consumer group, or None if the group does not exist.
        """
        try:
            groups:'anylist' = cast_('anylist', self.redis.xinfo_groups(stream_key))
        except ResponseError as e:
            logger.warning('xinfo_groups failed -> stream_key:%s, error:%s', stream_key, e)
            return None

        for group in groups:
            if group['name'] == group_name:
                return group['last-delivered-id']

        return None

# ################################################################################################################################

    @staticmethod
    def _increment_stream_id(stream_id:'str') -> 'str':
        """ Increments the sequence part of a Redis stream ID by 1.
        """
        parts = stream_id.split('-')
        timestamp_part = parts[0]
        sequence_part = parts[1]
        next_sequence = int(sequence_part) + 1
        out = f'{timestamp_part}-{next_sequence}'
        return out

# ################################################################################################################################

    def _browse_pending(
        self,
        topic_name:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Returns messages that are still pending for the subscriber.
        This covers two categories:
        - Messages read via XREADGROUP but not yet acked (from the consumer group PEL via XPENDING)
        - Messages not yet read by this consumer group (after the group's last-delivered-id)

        When reverse=True, returns the newest pending messages first by scanning
        the stream backwards and checking each entry against the PEL and last-delivered-id.
        XPENDING_RANGE has no reverse mode (the Redis rax iterator always walks forward),
        so the reverse path uses XREVRANGE on the stream and filters to pending entries.
        """

        # Our response to produce
        out:'browse_result' = ([], '')

        # Normalize topic name ..
        topic_name = topic_name.lower()
        stream_key = self._get_stream_key(topic_name)

        # .. find the group's last-delivered-id so we know where unread messages start ..
        last_delivered_id = self._get_last_delivered_id(stream_key, sub_key)

        if reverse:
            return self._browse_pending_reverse(
                stream_key, sub_key, cursor, page_size, needs_data, last_delivered_id)

        # .. forward scan: 1) read-but-unacked entries from the PEL ..
        pending_min = cursor if cursor != '-' else '-'

        try:
            pending_entries:'anylist' = cast_('anylist', self.redis.xpending_range(
                stream_key, sub_key, min=pending_min, max='+', count=page_size, consumername=sub_key))
        except ResponseError as e:
            logger.warning('xpending_range failed -> stream_key:%s, sub_key:%s, error:%s', stream_key, sub_key, e)
            pending_entries = []

        pending_ids:'anylist' = [entry['message_id'] for entry in pending_entries]

        # .. 2) unread entries beyond the last-delivered-id ..
        # .. entries at or before last_delivered_id have already been delivered,
        # .. so the unread boundary is always at least increment(last_delivered_id),
        # .. even when the pagination cursor is behind it.
        if last_delivered_id:
            after_delivered = self._increment_stream_id(last_delivered_id)
            if cursor != '-' and cursor > after_delivered:
                unread_min = cursor
            else:
                unread_min = after_delivered
            unread_entries:'anylist' = cast_('anylist', self.redis.xrange(
                stream_key, min=unread_min, count=page_size))
        else:
            unread_entries = []

        unread_ids:'anylist' = [entry[0] for entry in unread_entries]

        # .. merge and deduplicate the two sets of IDs ..
        seen:'set' = set()
        all_ids:'anylist' = []

        for stream_id in pending_ids:
            if stream_id not in seen:
                all_ids.append(stream_id)
                seen.add(stream_id)

        for stream_id in unread_ids:
            if stream_id not in seen:
                all_ids.append(stream_id)
                seen.add(stream_id)

        all_ids.sort()
        all_ids = all_ids[:page_size]

        if not all_ids:
            return out

        # .. fetch the actual message data using a pipeline ..
        raw_messages = self._fetch_ids_pipeline(stream_key, all_ids)

        if not raw_messages:
            return out

        messages = self._build_entries(raw_messages, needs_data)

        for msg in messages:
            msg['is_delivered'] = False

        # .. compute next_cursor ..
        next_cursor = self._compute_next_cursor(raw_messages, page_size)

        # .. and return the result.
        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def _browse_pending_reverse(
        self,
        stream_key:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        last_delivered_id:'strnone',
        ) -> 'browse_result':
        """ Returns the newest pending messages first.
        XPENDING_RANGE has no reverse mode (the Redis rax iterator only walks forward),
        so we scan backwards through the stream with XREVRANGE and filter to pending entries.
        Entries after last-delivered-id are unread (pending by definition).
        Entries at or before last-delivered-id may be in the PEL (read but not acked) -
        we check those with a single XPENDING_RANGE call over the candidate range.
        """

        out:'browse_result' = ([], '')

        # .. scan backwards through the stream ..
        xrev_max = '+' if cursor == '-' else cursor
        scan_batch = page_size * 3

        raw_entries:'anylist' = cast_('anylist', self.redis.xrevrange(
            stream_key, max=xrev_max, count=scan_batch))

        if not raw_entries:
            return out

        # .. split candidates into unread (definitely pending) and maybe-pending (need PEL check) ..
        maybe_pending_ids:'anylist' = []

        for stream_id, _ in raw_entries:
            if not last_delivered_id:
                continue
            if stream_id <= last_delivered_id:
                maybe_pending_ids.append(stream_id)

        # .. check PEL membership for the maybe-pending entries in a single call.
        # .. maybe_pending_ids is in descending order (from XREVRANGE),
        # .. so [-1] is the smallest and [0] is the largest.
        pel_ids:'set' = set()

        if maybe_pending_ids:
            pel_range_min = maybe_pending_ids[-1]
            pel_range_max = maybe_pending_ids[0]

            pel_entries:'anylist' = cast_('anylist', self.redis.xpending_range(
                stream_key, sub_key, min=pel_range_min, max=pel_range_max,
                count=len(maybe_pending_ids), consumername=sub_key))
            for entry in pel_entries:
                pel_ids.add(entry['message_id'])

        # .. walk through the scan results again, collecting pending IDs newest first ..
        pending_ids:'anylist' = []

        for stream_id, _ in raw_entries:
            is_unread = last_delivered_id and stream_id > last_delivered_id
            is_in_pel = stream_id in pel_ids

            if is_unread or is_in_pel:
                pending_ids.append(stream_id)
                if len(pending_ids) >= page_size:
                    break

        if not pending_ids:
            return out

        # .. fetch the actual message data ..
        raw_messages = self._fetch_ids_pipeline(stream_key, pending_ids)

        if not raw_messages:
            return out

        messages = self._build_entries(raw_messages, needs_data)

        for msg in messages:
            msg['is_delivered'] = False

        next_cursor = self._compute_next_cursor(raw_messages, page_size)

        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def _fetch_ids_pipeline(self, stream_key:'str', ids:'anylist') -> 'anylist':
        """ Fetches stream entries by ID using a pipeline.
        """
        pipe = self.redis.pipeline()

        for message_id in ids:
            _ = pipe.xrange(stream_key, min=message_id, max=message_id)

        pipeline_results:'anylist' = pipe.execute()

        raw_messages:'anylist' = []

        for result_list in pipeline_results:
            if result_list:
                raw_messages.append(result_list[0])

        return raw_messages

# ################################################################################################################################

    def _browse_delivered(
        self,
        topic_name:'str',
        sub_key:'str',
        cursor:'str',
        page_size:'int',
        needs_data:'bool',
        reverse:'bool' = False,
        ) -> 'browse_result':
        """ Returns only messages that have been delivered (acked) for the subscriber.
        "Delivered" means the subscriber read the message and acked it - it is no longer
        in the pending entries list and it is at or before the last-delivered-id.
        """

        # Our response to produce
        out:'browse_result' = ([], '')

        # Normalize topic name ..
        topic_name = topic_name.lower()
        stream_key = self._get_stream_key(topic_name)

        # .. find the group's last-delivered-id - messages beyond it are unread, not delivered ..
        last_delivered_id = self._get_last_delivered_id(stream_key, sub_key)

        if not last_delivered_id:
            return out

        # .. read a page from the stream, capped at last-delivered-id ..
        if reverse:
            xrange_max = last_delivered_id if cursor == '-' else cursor
            xrange_result = self.redis.xrevrange(stream_key, max=xrange_max, min='-', count=page_size)
        else:
            xrange_max = last_delivered_id
            xrange_result = self.redis.xrange(stream_key, min=cursor, max=xrange_max, count=page_size)

        raw_messages:'anylist' = cast_('anylist', xrange_result)

        if not raw_messages:
            return out

        # .. get the pending IDs in the same range to filter them out ..
        first_id = raw_messages[0][0]
        last_id = raw_messages[-1][0]

        try:
            pending_entries:'anylist' = cast_('anylist', self.redis.xpending_range(
                stream_key, sub_key, min=first_id, max=last_id, count=page_size, consumername=sub_key))
        except ResponseError as e:
            logger.warning('xpending_range failed -> stream_key:%s, sub_key:%s, error:%s', stream_key, sub_key, e)
            pending_entries = []

        pending_ids:'set' = {entry['message_id'] for entry in pending_entries}

        # .. keep only messages that are not pending (i.e. already acked) ..
        delivered_messages:'anylist' = [
            entry for entry in raw_messages if entry[0] not in pending_ids
        ]

        if not delivered_messages:
            next_cursor = self._compute_next_cursor(raw_messages, page_size)
            out = ([], next_cursor)
            return out

        messages = self._build_entries(delivered_messages, needs_data)

        for msg in messages:
            msg['is_delivered'] = True

        # .. compute next_cursor from the full XRANGE page (not the filtered result) ..
        next_cursor = self._compute_next_cursor(raw_messages, page_size)

        # .. and return the result.
        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def _build_entries(self, raw_messages:'anylist', needs_data:'bool') -> 'anylist':
        """ Builds entry dicts from raw (redis_stream_id, message_data) tuples.
        """

        messages:'anylist' = []

        for redis_stream_id, message_data in raw_messages:

            entry:'anydict' = {
                'redis_stream_id': redis_stream_id,
                'msg_id': message_data['msg_id'],
                'topic_name': message_data['topic_name'],
                'priority': int(message_data['priority']),
                'expiration': int(message_data['expiration']),
                'pub_time_iso': message_data['pub_time_iso'],
                'recv_time_iso': message_data['recv_time_iso'],
                'expiration_time_iso': message_data['expiration_time_iso'],
                'data_size': int(message_data['data_size']),
                'data_preview': message_data['data_preview'],
            }

            # .. include optional metadata fields ..
            if correl_id := message_data.get('correl_id'):
                entry['correl_id'] = correl_id

            if in_reply_to := message_data.get('in_reply_to'):
                entry['in_reply_to'] = in_reply_to

            if ext_client_id := message_data.get('ext_client_id'):
                entry['ext_client_id'] = ext_client_id

            if publisher := message_data.get('publisher'):
                entry['publisher'] = publisher

            # .. optionally load the full payload from disk ..
            if needs_data:
                data_reference = message_data['data_ref']
                load_result = self.disk_store.load(data_reference)
                entry['data'] = load_result.data
                entry['data_class'] = load_result.data_class

            messages.append(entry)

        return messages

# ################################################################################################################################

    def _compute_next_cursor(self, raw_messages:'anylist', page_size:'int') -> 'str':
        """ Computes the next pagination cursor from the last message in the result set.
        """

        raw_messages_len = len(raw_messages)

        if raw_messages_len < page_size:
            return ''

        # .. the next cursor is the last stream ID + 1 sequence number ..
        last_message = raw_messages[-1]
        last_stream_id = last_message[0]

        # .. Redis stream IDs are '<ms>-<seq>', increment the seq.
        parts = last_stream_id.split('-')
        timestamp_part = parts[0]
        sequence_part = parts[1]
        sequence_number = int(sequence_part)
        next_sequence = sequence_number + 1
        next_cursor = f'{timestamp_part}-{next_sequence}'

        return next_cursor

# ################################################################################################################################

    def get_subscribed_topics(self, sub_key:'str') -> 'strlist':
        """ Get list of topics a subscriber is subscribed to.
        """
        subs_key = self._get_subs_key(sub_key)
        topics:'strset' = cast_('strset', self.redis.smembers(subs_key))

        out = list(topics)
        return out

# ################################################################################################################################

    def get_pending_depths(self, sub_topic_pairs:'anylist') -> 'anydict':
        """ Get the total pending depth for each subscriber across its topics.
        Accepts a list of (sub_key, topic_name) pairs.
        Returns a dict mapping sub_key to total pending message count.
        Uses a Lua script to compute PEL + lag per pair in a single EVALSHA call.
        """

        # Build the ARGV list of (stream_key, group_name) pairs ..
        argv:'anylist' = []

        for sub_key, topic_name in sub_topic_pairs:
            stream_key = self._get_stream_key(topic_name)
            argv.append(stream_key)
            argv.append(sub_key)

        # .. call the Lua script ..
        counts:'anylist' = cast_('anylist', self.redis.evalsha(self._lua_pending_depths_sha, 0, *argv))

        # .. and sum the per-pair results into per-subscriber totals.
        out:'anydict' = {}

        for pair_index in range(len(sub_topic_pairs)):
            sub_key = sub_topic_pairs[pair_index][0]
            count = counts[pair_index]

            if sub_key in out:
                out[sub_key] = out[sub_key] + count
            else:
                out[sub_key] = count

        return out

# ################################################################################################################################

    def get_total_count(self, sub_key:'str', topic_name:'str', state:'str') -> 'int':
        """ Returns the total message count for a (sub_key, topic) pair by delivery state.
        """

        if state == 'pending':

            # Reuse the existing Lua script (PEL + lag) for pending depth ..
            depths = self.get_pending_depths([(sub_key, topic_name)])
            out = depths[sub_key]
            return out

        elif state == 'all':

            # XLEN gives the total number of entries in the stream ..
            stream_key = self._get_stream_key(topic_name)

            try:
                out = self.redis.xlen(stream_key)
            except ResponseError:
                out = 0

            return out

        elif state == 'delivered':

            # Delivered = total - pending ..
            stream_key = self._get_stream_key(topic_name)

            try:
                total = self.redis.xlen(stream_key)
            except ResponseError:
                total = 0

            depths = self.get_pending_depths([(sub_key, topic_name)])
            pending = depths[sub_key]

            out = total - pending
            if out < 0:
                out = 0

            return out

        else:
            return 0

# ################################################################################################################################

    def get_topic_subscribers(self, topic_name:'str') -> 'strlist':
        """ Get list of subscribers for a topic.
        """
        topic_subs_key = self._get_topic_subs_key(topic_name)
        subscriptions:'strset' = cast_('strset', self.redis.smembers(topic_subs_key))

        out = list(subscriptions)
        return out

# ################################################################################################################################

    def delete_topic(self, topic_name:'str') -> 'None':
        """ Delete a topic and all its data.
        """
        # Build the key names ..
        stream_key = self._get_stream_key(topic_name)
        topic_subs_key = self._get_topic_subs_key(topic_name)

        # .. delete all payload files from disk before removing the stream ..
        self.disk_store.delete_topic_dir(topic_name)

        # .. get all subscribers to this topic ..
        subscriptions = self.get_topic_subscribers(topic_name)

        # .. remove topic from each subscriber's set ..
        for sub_key in subscriptions:
            subs_key = self._get_subs_key(sub_key)
            _ = self.redis.srem(subs_key, topic_name)

            # .. destroy consumer group ..
            try:
                _ = self.redis.xgroup_destroy(stream_key, sub_key)
            except ResponseError:
                logger.debug('Consumer group %s not found for stream %s during delete', sub_key, stream_key)

        # .. delete the stream ..
        _ = self.redis.delete(stream_key)

        # .. delete the topic subscribers set.
        _ = self.redis.delete(topic_subs_key)

# ################################################################################################################################

    def get_publish_timeline(self, topic_names:'strlist', since_minutes:'int'=60) -> 'dictlist':
        """ Return a per-minute publish count timeline aggregated across the given topics.
        Each entry is {'ts': <epoch_ms>, 'count': <int>}.
        """

        # Compute the cutoff timestamp for the XRANGE query ..
        now = utcnow()
        cutoff_delta = timedelta(minutes=since_minutes)
        cutoff = now - cutoff_delta

        # .. Redis stream IDs are <ms_epoch>-<seq>, so build the min ID from the cutoff ..
        cutoff_epoch_ms = int(cutoff.timestamp() * 1000)
        min_stream_id = f'{cutoff_epoch_ms}-0'

        # .. bucket all messages by minute ..
        buckets:'anydict' = {}

        for topic_name in topic_names:
            stream_key = self._get_stream_key(topic_name)

            try:
                messages:'anylist' = cast_('anylist', self.redis.xrange(stream_key, min=min_stream_id))
            except ResponseError as e:
                logger.warning('xrange failed -> stream_key:%s, error:%s', stream_key, e)
                continue

            for _, message_data in messages:

                pub_time_iso = message_data['pub_time_iso']

                # .. parse the timestamp and truncate to the start of the minute ..
                normalized_iso = pub_time_iso.replace('Z', '+00:00')
                pub_time = datetime.fromisoformat(normalized_iso)
                minute_start = pub_time.replace(second=0, microsecond=0)
                bucket_key_ms = int(minute_start.timestamp() * 1000)

                if bucket_key_ms in buckets:
                    buckets[bucket_key_ms] += 1
                else:
                    buckets[bucket_key_ms] = 1

        # .. sort by timestamp and build the output list.
        sorted_keys = sorted(buckets.keys())

        out:'dictlist' = []

        for key_ms in sorted_keys:
            entry = {'ts': key_ms, 'count': buckets[key_ms]}
            out.append(entry)

        return out

# ################################################################################################################################

    def count_distinct_publishers(self, topic_names:'strlist', since_minutes:'int'=60) -> 'int':
        """ Count distinct publisher identifiers across all given topics within the time window.
        """

        # Compute the cutoff ..
        now = utcnow()
        cutoff_delta = timedelta(minutes=since_minutes)
        cutoff = now - cutoff_delta
        cutoff_epoch_ms = int(cutoff.timestamp() * 1000)
        min_stream_id = f'{cutoff_epoch_ms}-0'

        # .. collect distinct publishers from all topics.
        publishers:'set' = set()

        for topic_name in topic_names:
            stream_key = self._get_stream_key(topic_name)

            try:
                messages:'anylist' = cast_('anylist', self.redis.xrange(stream_key, min=min_stream_id))
            except ResponseError as e:
                logger.warning('xrange failed -> stream_key:%s, error:%s', stream_key, e)
                continue

            for _, message_data in messages:
                if publisher := message_data.get('publisher'):
                    publishers.add(publisher)

        out = len(publishers)
        return out

# ################################################################################################################################

    def rename_topic(self, old_topic_name:'str', new_topic_name:'str') -> 'None':
        """ Rename a topic.
        """
        # Build old and new key names ..
        old_stream_key = self._get_stream_key(old_topic_name)
        new_stream_key = self._get_stream_key(new_topic_name)
        old_topic_subs_key = self._get_topic_subs_key(old_topic_name)
        new_topic_subs_key = self._get_topic_subs_key(new_topic_name)

        # .. get all subscribers ..
        subscriptions = self.get_topic_subscribers(old_topic_name)

        # .. rename stream ..
        try:
            _ = self.redis.rename(old_stream_key, new_stream_key)
        except ResponseError:
            logger.debug('Stream %s not found during rename', old_stream_key)

        # .. rename topic subscribers set ..
        try:
            _ = self.redis.rename(old_topic_subs_key, new_topic_subs_key)
        except ResponseError:
            logger.debug('Topic subscribers set %s not found during rename', old_topic_subs_key)

        # .. update each subscriber's topic set.
        for sub_key in subscriptions:
            subs_key = self._get_subs_key(sub_key)
            _ = self.redis.srem(subs_key, old_topic_name)
            _ = self.redis.sadd(subs_key, new_topic_name)

        # Note: we do not rename the on-disk directory because Redis Streams
        # do not support in-place field updates, so existing data_ref values
        # in the stream must keep pointing to valid paths. New messages published
        # after the rename will use the new topic name for their directory.

# ################################################################################################################################
# ################################################################################################################################
