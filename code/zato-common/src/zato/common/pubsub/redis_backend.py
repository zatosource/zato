# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import threading
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

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PublishResult:
    msg_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Stream_Prefix     = 'zato:pubsub:stream:'
    Subs_Prefix       = 'zato:pubsub:subs:'
    Topic_Subs_Prefix = 'zato:pubsub:topic_subs:'
    Pending_Prefix    = 'zato:pubsub:pending:'
    Pending_Expiry_Key = 'zato:pubsub:pending_expiry'

# ################################################################################################################################
# ################################################################################################################################

class RedisPubSubBackend:
    """ Redis Streams-based pub/sub backend.
    """

    def __init__(self, redis_client:'Redis', disk_store:'DiskMessageStore', server:'any_'=None) -> 'None':
        self.redis = redis_client
        self.disk_store = disk_store
        self.server = server

# ################################################################################################################################

    def _get_stream_key(self, topic_name:'str') -> 'str':
        out = f'{ModuleCtx.Stream_Prefix}{topic_name}'
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

        logger.info('Published to stream -> message_id:%s, data_ref:%s, stream_key:%s, redis_stream_id:%s, thread:%s',
            message_id, data_ref, stream_key, redis_stream_id, threading.current_thread().name)

        # .. populate the pending subscriber set and index by expiration time ..
        topic_subs_key = self._get_topic_subs_key(topic_name)
        subscriber_keys:'strset' = cast_('strset', self.redis.smembers(topic_subs_key))

        # .. if there are any subscribers, record which ones still need this message ..
        if subscriber_keys:
            pending_key = self._get_pending_key(data_ref)
            _ = self.redis.sadd(pending_key, *subscriber_keys)

            # .. and index the message by its expiration time for the cleanup job ..
            expiration_timestamp = expiration_time.timestamp()
            _ = self.redis.zadd(ModuleCtx.Pending_Expiry_Key, {data_ref: expiration_timestamp})

            subscriber_count = len(subscriber_keys)
            logger.info('Populated pending set -> data_ref:%s, subscriber_count:%d, expiration_timestamp:%.1f, thread:%s',
                data_ref, subscriber_count, expiration_timestamp, threading.current_thread().name)

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

        # .. check if subscriber has any remaining subscriptions ..
        remaining = self.redis.scard(subs_key)

        # .. if no remaining subscriptions, destroy the consumer group.
        if remaining == 0:
            try:
                _ = self.redis.xgroup_destroy(stream_key, sub_key)
            except ResponseError:
                pass

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

                logger.info('fetch_messages -> sub_key:%s, stream_name:%s, redis_message_id:%s, msg_id:%s, data_ref:%s, thread:%s',
                    sub_key, stream_name, redis_message_id, message_data.get('msg_id'),
                    message_data.get('data_ref'), threading.current_thread().name)

                # .. message_data is already dict[str, str] because decode_responses=True ..
                decoded = message_data

                # .. check expiration - ack expired messages immediately and skip them ..
                expiration_time_iso = decoded['expiration_time_iso']

                normalized_expiration_iso = expiration_time_iso.replace('Z', '+00:00')
                expiration_time = datetime.fromisoformat(normalized_expiration_iso)

                now = utcnow()

                if now > expiration_time:
                    expired_data_ref = decoded['data_ref']
                    logger.info('Expiring message -> sub_key:%s, data_ref:%s, expiration_time_iso:%s, thread:%s',
                        sub_key, expired_data_ref, expiration_time_iso, threading.current_thread().name)
                    _ = self.redis.xack(stream_name, sub_key, redis_message_id)
                    self.disk_store.delete(expired_data_ref)
                    continue

                # .. check max_len constraint using data_size from metadata ..
                data_len = int(decoded['data_size'])

                if total_len + data_len > max_len:
                    break

                total_len += data_len

                # .. load the actual payload from disk ..
                data_ref = decoded['data_ref']
                logger.info('fetch_messages loading payload -> sub_key:%s, data_ref:%s, redis_message_id:%s, stream_name:%s, thread:%s',
                    sub_key, data_ref, redis_message_id, stream_name, threading.current_thread().name)
                load_result = self.disk_store.load(data_ref)
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

        return messages[:max_messages]

# ################################################################################################################################

    def ack_message(self, stream_name:'str', sub_key:'str', redis_message_id:'str', data_ref:'strnone'=None) -> 'None':
        """ Acknowledge a single message after successful processing.
        """
        # Acknowledge the message in the stream ..
        logger.info('ack_message -> sub_key:%s, stream_name:%s, redis_message_id:%s, data_ref:%s, thread:%s',
            sub_key, stream_name, redis_message_id, data_ref, threading.current_thread().name)

        _ = self.redis.xack(stream_name, sub_key, redis_message_id)

        # .. clean up the payload file from disk.
        if data_ref:
            self.disk_store.delete(data_ref)

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
            logger.info('format_messages_for_rest acking -> sub_key:%s, data_ref:%s, redis_message_id:%s, stream_name:%s, thread:%s',
                sub_key, data_ref, redis_message_id, stream_name, threading.current_thread().name)
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
        cursor:'str'='-',
        page_size:'int'=_default_page_size,
        needs_data:'bool'=False,
    ) -> 'browse_result':
        """ Browse messages in a topic without consuming them.
        Uses XRANGE for read-only access that does not affect consumer groups.
        Returns (messages, next_cursor) for cursor-based pagination.
        """

        # Normalize topic name ..
        topic_name = topic_name.lower()
        stream_key = self._get_stream_key(topic_name)

        # .. read a page from the stream ..
        try:
            raw_messages:'anylist' = cast_('anylist', self.redis.xrange(stream_key, min=cursor, count=page_size))
        except ResponseError:
            return [], ''

        if not raw_messages:
            return [], ''

        messages:'anylist' = []

        for _, message_data in raw_messages:

            entry:'anydict' = {
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
                data_ref = message_data['data_ref']
                load_result = self.disk_store.load(data_ref)
                entry['data'] = load_result.data
                entry['data_class'] = load_result.data_class

            messages.append(entry)

        # .. compute next_cursor for the next page ..
        raw_messages_len = len(raw_messages)

        if raw_messages_len < page_size:
            next_cursor = ''

        # .. the next cursor is the last stream ID + 1 sequence number ..
        else:
            last_stream_id = raw_messages[-1][0]

            # .. Redis stream IDs are '<ms>-<seq>', increment the seq.
            parts = last_stream_id.split('-')
            timestamp_part = parts[0]
            sequence_part = parts[1]
            next_sequence = int(sequence_part) + 1
            next_cursor = f'{timestamp_part}-{next_sequence}'

        out = (messages, next_cursor)
        return out

# ################################################################################################################################

    def get_subscribed_topics(self, sub_key:'str') -> 'strlist':
        """ Get list of topics a subscriber is subscribed to.
        """
        subs_key = self._get_subs_key(sub_key)
        topics:'strset' = cast_('strset', self.redis.smembers(subs_key))

        out = list(topics)
        return out

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
            except ResponseError:
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
            except ResponseError:
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
