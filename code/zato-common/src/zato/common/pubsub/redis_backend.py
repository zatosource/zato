# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

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
from zato.common.util.api import new_msg_id, utcnow
from zato.server.metrics import zato_pubsub_messages_delivered_total, zato_pubsub_messages_published_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import any_, anydict, anylist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration
_default_max_messages = PubSub.Message.Default_Max_Messages
_default_max_len = PubSub.Message.Default_Max_Len
_default_stream_max_len = 100_000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PublishResult:
    msg_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Stream_Prefix = 'zato:pubsub:stream:'
    Subs_Prefix = 'zato:pubsub:subs:'
    Topic_Subs_Prefix = 'zato:pubsub:topic_subs:'

# ################################################################################################################################
# ################################################################################################################################

class RedisPubSubBackend:
    """ Redis Streams-based pub/sub backend.
    """

    def __init__(self, redis_client:'Redis') -> 'None':
        self.redis = redis_client

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

        # .. normalize topic name to lowercase for case-insensitivity ..
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
        if isinstance(data, str):
            serialized_data = data
        else:
            serialized_data = json.dumps(data)

        # .. build the message ..
        recv_time_iso = now.isoformat()

        message = {
            'msg_id': message_id,
            'data': serialized_data,
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

        counter = zato_pubsub_messages_published_total.labels(topic_name=topic_name)
        _ = counter.inc()

        out = PublishResult()
        out.msg_id = message_id

        return out

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Subscribe a user to a topic.
        """

        # .. normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        # .. add topic to subscriber's set ..
        _ = self.redis.sadd(subs_key, topic_name)

        # .. add subscriber to topic's set ..
        _ = self.redis.sadd(topic_subs_key, sub_key)

        # .. create consumer group if not exists ..
        try:
            _ = self.redis.xgroup_create(stream_key, sub_key, id='0', mkstream=True)
        except ResponseError as error:
            if 'BUSYGROUP' not in error.args[0]:
                raise

# ################################################################################################################################

    def unsubscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Unsubscribe a user from a topic.
        """

        # .. normalize topic name to lowercase for case-insensitivity ..
        topic_name = topic_name.lower()

        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        # .. remove topic from subscriber's set ..
        _ = self.redis.srem(subs_key, topic_name)

        # .. remove subscriber from topic's set ..
        _ = self.redis.srem(topic_subs_key, sub_key)

        # .. check if subscriber has any remaining subscriptions ..
        remaining = self.redis.scard(subs_key)

        # .. if no remaining subscriptions, destroy the consumer group ..
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
        subs_key = self._get_subs_key(sub_key)

        # .. get all topics this subscriber is subscribed to ..
        topics = self.redis.smembers(subs_key)

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

            result = self.redis.xreadgroup(
                groupname=sub_key,
                consumername=sub_key,
                streams=streams,
                count=max_messages,
                block=block_value
            )

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
                    _ = self.redis.xack(stream_name, sub_key, redis_message_id)
                    continue

                # .. check max_len constraint ..
                data_len = len(decoded['data'])

                if total_len + data_len > max_len:
                    break

                total_len += data_len

                # .. convert priority and expiration from string to int once ..
                decoded['priority'] = int(decoded['priority'])
                decoded['expiration'] = int(decoded['expiration'])

                decoded['_redis_message_id'] = redis_message_id
                decoded['_stream_name'] = stream_name

                messages.append(decoded)

        # .. sort by priority desc, then by pub_time asc ..
        def _sort_key(message:'anydict') -> 'tuple':
            negated_priority = -message['priority']
            pub_time = message['pub_time_iso']

            out = (negated_priority, pub_time)
            return out

        messages.sort(key=_sort_key)

        return messages[:max_messages]

# ################################################################################################################################

    def ack_message(self, stream_name:'str', sub_key:'str', redis_message_id:'str') -> 'None':
        """ Acknowledge a single message after successful processing.
        """
        _ = self.redis.xack(stream_name, sub_key, redis_message_id)

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

            redis_message_id = message.pop('_redis_message_id')
            stream_name = message.pop('_stream_name')

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

            # .. acknowledge and count after formatting ..
            self.ack_message(stream_name, sub_key, redis_message_id)

            counter = zato_pubsub_messages_delivered_total.labels(topic_name=message['topic_name'])
            _ = counter.inc()

        return out

# ################################################################################################################################

    @staticmethod
    def _compute_time_since(iso_timestamp:'str', now:'datetime') -> 'str':

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

        delta = now_naive - timestamp_naive

        if delta.total_seconds() < 0:
            delta = timedelta(0)

        out = str(delta)
        return out

# ################################################################################################################################

    def get_subscribed_topics(self, sub_key:'str') -> 'strlist':
        """ Get list of topics a subscriber is subscribed to.
        """
        subs_key = self._get_subs_key(sub_key)
        topics = self.redis.smembers(subs_key)

        out = list(topics)
        return out

# ################################################################################################################################

    def get_topic_subscribers(self, topic_name:'str') -> 'strlist':
        """ Get list of subscribers for a topic.
        """
        topic_subs_key = self._get_topic_subs_key(topic_name)
        subscriptions = self.redis.smembers(topic_subs_key)

        out = list(subscriptions)
        return out

# ################################################################################################################################

    def delete_topic(self, topic_name:'str') -> 'None':
        """ Delete a topic and all its data.
        """
        stream_key = self._get_stream_key(topic_name)
        topic_subs_key = self._get_topic_subs_key(topic_name)

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

        # .. delete the topic subscribers set ..
        _ = self.redis.delete(topic_subs_key)

# ################################################################################################################################

    def rename_topic(self, old_topic_name:'str', new_topic_name:'str') -> 'None':
        """ Rename a topic.
        """
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

        # .. update each subscriber's topic set ..
        for sub_key in subscriptions:
            subs_key = self._get_subs_key(sub_key)
            _ = self.redis.srem(subs_key, old_topic_name)
            _ = self.redis.sadd(subs_key, new_topic_name)

# ################################################################################################################################
# ################################################################################################################################
