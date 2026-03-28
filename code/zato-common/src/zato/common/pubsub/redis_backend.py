# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from logging import getLogger

# redis
from redis.exceptions import ResponseError

# Zato
from zato.common.util.api import new_msg_id, utcnow

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

class ModuleCtx:
    Stream_Prefix = 'zato:pubsub:stream:'
    Subs_Prefix = 'zato:pubsub:subs:'
    Topic_Subs_Prefix = 'zato:pubsub:topic_subs:'
    Default_Max_Len = 100_000

# ################################################################################################################################
# ################################################################################################################################

class RedisPubSubBackend:
    """ Redis Streams-based pub/sub backend.
    """

    def __init__(self, redis_client:'Redis') -> 'None':
        self.redis = redis_client

# ################################################################################################################################

    def _get_stream_key(self, topic_name:'str') -> 'str':
        return f'{ModuleCtx.Stream_Prefix}{topic_name}'

# ################################################################################################################################

    def _get_subs_key(self, sub_key:'str') -> 'str':
        return f'{ModuleCtx.Subs_Prefix}{sub_key}'

# ################################################################################################################################

    def _get_topic_subs_key(self, topic_name:'str') -> 'str':
        return f'{ModuleCtx.Topic_Subs_Prefix}{topic_name}'

# ################################################################################################################################

    def publish(
        self,
        topic_name:'str',
        data:'any_',
        *,
        priority:'int'=5,
        expiration:'int'=31536000,
        correl_id:'strnone'=None,
        in_reply_to:'strnone'=None,
        ext_client_id:'strnone'=None,
        publisher:'strnone'=None,
    ) -> 'str':
        """ Publish a message to a topic stream.
        """
        # Generate message ID
        msg_id = new_msg_id()

        # Timestamps
        now = utcnow()
        pub_time_iso = now.isoformat()
        expiration_time = now + timedelta(seconds=expiration)
        expiration_time_iso = expiration_time.isoformat()

        # Build message
        message = {
            'msg_id': msg_id,
            'data': data if isinstance(data, str) else str(data),
            'topic_name': topic_name,
            'priority': str(priority),
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': pub_time_iso,
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

        # Add to stream
        stream_key = self._get_stream_key(topic_name)
        _ = self.redis.xadd(stream_key, message, maxlen=ModuleCtx.Default_Max_Len)

        logger.info('Published message %s to topic %s', msg_id, topic_name)

        return msg_id

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Subscribe a user to a topic.
        """
        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        # Add topic to subscriber's set
        _ = self.redis.sadd(subs_key, topic_name)

        # Add subscriber to topic's set
        _ = self.redis.sadd(topic_subs_key, sub_key)

        # Create consumer group if not exists
        try:
            _ = self.redis.xgroup_create(stream_key, sub_key, id='$', mkstream=True)
            logger.info('Created consumer group %s for stream %s', sub_key, stream_key)
        except ResponseError as e:
            if 'BUSYGROUP' in str(e):
                pass  # Group already exists
            else:
                raise

        logger.info('Subscribed %s to topic %s', sub_key, topic_name)

# ################################################################################################################################

    def unsubscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Unsubscribe a user from a topic.
        """
        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        # Remove topic from subscriber's set
        _ = self.redis.srem(subs_key, topic_name)

        # Remove subscriber from topic's set
        _ = self.redis.srem(topic_subs_key, sub_key)

        # Check if subscriber has any remaining subscriptions
        remaining = self.redis.scard(subs_key)

        # If no remaining subscriptions, destroy the consumer group
        if remaining == 0:
            try:
                _ = self.redis.xgroup_destroy(stream_key, sub_key)
                logger.info('Destroyed consumer group %s for stream %s', sub_key, stream_key)
            except ResponseError:
                pass  # Group may not exist

        logger.info('Unsubscribed %s from topic %s', sub_key, topic_name)

# ################################################################################################################################

    def fetch_messages(
        self,
        sub_key:'str',
        max_messages:'int'=50,
        max_len:'int'=5_000_000
    ) -> 'anylist':
        """ Fetch messages for a subscriber from all subscribed topics.
        """
        subs_key = self._get_subs_key(sub_key)

        # Get all topics this subscriber is subscribed to
        topics = self.redis.smembers(subs_key)

        if not topics:
            return []

        # Decode topic names if needed
        topics = [t.decode('utf-8') if isinstance(t, bytes) else t for t in topics]

        # Build streams dict for xreadgroup
        streams = {self._get_stream_key(topic): '>' for topic in topics}

        # Read from all subscribed streams
        try:
            result = self.redis.xreadgroup(
                groupname=sub_key,
                consumername=sub_key,
                streams=streams,
                count=max_messages
            )
        except ResponseError as e:
            if 'NOGROUP' in str(e):
                return []
            raise

        if not result:
            return []

        messages = []
        total_len = 0

        for stream_name, stream_messages in result:
            for redis_msg_id, msg_data in stream_messages:

                # Decode message data
                decoded = {}
                for key, value in msg_data.items():
                    key = key.decode('utf-8') if isinstance(key, bytes) else key
                    value = value.decode('utf-8') if isinstance(value, bytes) else value
                    decoded[key] = value

                # Check max_len constraint
                data_len = len(decoded.get('data', ''))
                if total_len + data_len > max_len:
                    break

                total_len += data_len

                # Convert priority back to int for sorting
                decoded['priority'] = int(decoded.get('priority', 5))
                decoded['_redis_msg_id'] = redis_msg_id
                decoded['_stream_name'] = stream_name

                messages.append(decoded)

                # Acknowledge the message for this consumer group
                stream_name_str = stream_name.decode('utf-8') if isinstance(stream_name, bytes) else stream_name
                _ = self.redis.xack(stream_name_str, sub_key, redis_msg_id)

        # Sort by priority desc, then by pub_time asc
        messages.sort(key=lambda m: (-m['priority'], m.get('pub_time_iso', '')))

        # Remove internal fields before returning
        for msg in messages:
            _ = msg.pop('_redis_msg_id', None)
            _ = msg.pop('_stream_name', None)

        return messages[:max_messages]

# ################################################################################################################################

    def get_subscribed_topics(self, sub_key:'str') -> 'strlist':
        """ Get list of topics a subscriber is subscribed to.
        """
        subs_key = self._get_subs_key(sub_key)
        topics = self.redis.smembers(subs_key)
        return [t.decode('utf-8') if isinstance(t, bytes) else t for t in topics]

# ################################################################################################################################

    def get_topic_subscribers(self, topic_name:'str') -> 'strlist':
        """ Get list of subscribers for a topic.
        """
        topic_subs_key = self._get_topic_subs_key(topic_name)
        subs = self.redis.smembers(topic_subs_key)
        return [s.decode('utf-8') if isinstance(s, bytes) else s for s in subs]

# ################################################################################################################################

    def delete_topic(self, topic_name:'str') -> 'None':
        """ Delete a topic and all its data.
        """
        stream_key = self._get_stream_key(topic_name)
        topic_subs_key = self._get_topic_subs_key(topic_name)

        # Get all subscribers to this topic
        subs = self.get_topic_subscribers(topic_name)

        # Remove topic from each subscriber's set
        for sub_key in subs:
            subs_key = self._get_subs_key(sub_key)
            _ = self.redis.srem(subs_key, topic_name)

            # Destroy consumer group
            try:
                _ = self.redis.xgroup_destroy(stream_key, sub_key)
            except ResponseError:
                pass

        # Delete the stream
        _ = self.redis.delete(stream_key)

        # Delete the topic subscribers set
        _ = self.redis.delete(topic_subs_key)

        logger.info('Deleted topic %s', topic_name)

# ################################################################################################################################

    def rename_topic(self, old_topic_name:'str', new_topic_name:'str') -> 'None':
        """ Rename a topic.
        """
        old_stream_key = self._get_stream_key(old_topic_name)
        new_stream_key = self._get_stream_key(new_topic_name)
        old_topic_subs_key = self._get_topic_subs_key(old_topic_name)
        new_topic_subs_key = self._get_topic_subs_key(new_topic_name)

        # Get all subscribers
        subs = self.get_topic_subscribers(old_topic_name)

        # Rename stream
        try:
            _ = self.redis.rename(old_stream_key, new_stream_key)
        except ResponseError:
            pass  # Stream may not exist

        # Rename topic subscribers set
        try:
            _ = self.redis.rename(old_topic_subs_key, new_topic_subs_key)
        except ResponseError:
            pass  # Set may not exist

        # Update each subscriber's topic set
        for sub_key in subs:
            subs_key = self._get_subs_key(sub_key)
            _ = self.redis.srem(subs_key, old_topic_name)
            _ = self.redis.sadd(subs_key, new_topic_name)

        logger.info('Renamed topic %s to %s', old_topic_name, new_topic_name)

# ################################################################################################################################
# ################################################################################################################################
