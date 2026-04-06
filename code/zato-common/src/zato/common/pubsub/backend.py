# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
import json
from logging import getLogger

# zato-broker-core (Rust extension)
from zato_broker_core import (
    BrokerConfig,
    fs_stream_xadd,
    fs_stream_xreadgroup,
    fs_stream_xack,
    fs_stream_xgroup_create,
    fs_stream_xgroup_destroy,
    fs_stream_xdel,
    fs_stream_xrange,
    fs_set_sadd,
    fs_set_srem,
    fs_set_smembers,
    fs_set_scard,
    fs_rename,
    fs_delete_tree,
)

# Zato
from zato.common.util.api import new_msg_id, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
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

class PubSubBackend:
    """ Broker-backed pub/sub backend replacing RedisPubSubBackend.
    Uses Rust extension functions for streams, sets, and key-value operations.
    """

    def __init__(self, broker_client:'any_') -> 'None':
        self._cfg = broker_client._cfg

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
        pub_time:'strnone'=None,
    ) -> 'str':
        topic_name = topic_name.lower()

        msg_id = new_msg_id()

        now = utcnow()
        pub_time_iso = pub_time if pub_time else now.isoformat()
        expiration_time = now + timedelta(seconds=expiration)
        expiration_time_iso = expiration_time.isoformat()

        message = {
            'msg_id': msg_id,
            'data': data if isinstance(data, str) else json.dumps(data),
            'topic_name': topic_name,
            'priority': str(priority),
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': now.isoformat(),
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

        stream_key = self._get_stream_key(topic_name)
        fields_json = json.dumps(message)
        _ = fs_stream_xadd(self._cfg, stream_key, fields_json, maxlen=ModuleCtx.Default_Max_Len)

        return msg_id

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        topic_name = topic_name.lower()

        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        _ = fs_set_sadd(self._cfg, subs_key, [topic_name])
        _ = fs_set_sadd(self._cfg, topic_subs_key, [sub_key])

        try:
            fs_stream_xgroup_create(self._cfg, stream_key, sub_key, '$', True)
        except Exception as e:
            if 'already exists' not in str(e).lower():
                raise

# ################################################################################################################################

    def unsubscribe(self, sub_key:'str', topic_name:'str') -> 'None':
        topic_name = topic_name.lower()

        subs_key = self._get_subs_key(sub_key)
        topic_subs_key = self._get_topic_subs_key(topic_name)
        stream_key = self._get_stream_key(topic_name)

        _ = fs_set_srem(self._cfg, subs_key, [topic_name])
        _ = fs_set_srem(self._cfg, topic_subs_key, [sub_key])

        remaining = fs_set_scard(self._cfg, subs_key)

        if remaining == 0:
            try:
                fs_stream_xgroup_destroy(self._cfg, stream_key, sub_key)
            except Exception:
                pass

# ################################################################################################################################

    def fetch_messages(
        self,
        sub_key:'str',
        max_messages:'int'=50,
        max_len:'int'=5_000_000
    ) -> 'anylist':
        subs_key = self._get_subs_key(sub_key)

        topics = list(fs_set_smembers(self._cfg, subs_key))

        if not topics:
            return []

        messages = []
        total_len = 0

        for topic in topics:
            stream_key = self._get_stream_key(topic)

            try:
                entries = fs_stream_xreadgroup(self._cfg, stream_key, sub_key, sub_key, max_messages)
            except Exception:
                continue

            for seq_id, fields_json in entries:
                try:
                    msg_data = json.loads(fields_json)
                except Exception:
                    msg_data = {'data': fields_json}

                expiration_time_iso = msg_data.get('expiration_time_iso', '')
                if expiration_time_iso:
                    try:
                        expiration_time = datetime.fromisoformat(expiration_time_iso.replace('Z', '+00:00'))
                        now = utcnow()
                        if now > expiration_time:
                            _ = fs_stream_xack(self._cfg, stream_key, sub_key, [seq_id])
                            continue
                    except (ValueError, TypeError):
                        pass

                data_len = len(msg_data.get('data', ''))
                if total_len + data_len > max_len:
                    break

                total_len += data_len

                msg_data['priority'] = int(msg_data.get('priority', 5))
                msg_data['_seq_id'] = seq_id
                msg_data['_stream_key'] = stream_key

                messages.append(msg_data)

                _ = fs_stream_xack(self._cfg, stream_key, sub_key, [seq_id])

        messages.sort(key=lambda m: (-m['priority'], m.get('pub_time_iso', '')))

        formatted_messages = []
        for msg in messages[:max_messages]:
            _ = msg.pop('_seq_id', None)
            _ = msg.pop('_stream_key', None)

            data = msg.pop('data', '')
            meta = {
                'topic_name': msg.get('topic_name', ''),
                'size': len(data) if isinstance(data, str) else 0,
                'priority': msg.get('priority', 5),
                'expiration': int(msg.get('expiration', 31536000)),
                'msg_id': msg.get('msg_id', ''),
                'pub_time_iso': msg.get('pub_time_iso', ''),
                'recv_time_iso': msg.get('recv_time_iso', ''),
                'expiration_time_iso': msg.get('expiration_time_iso', ''),
            }

            if msg.get('correl_id'):
                meta['correl_id'] = msg['correl_id']
            if msg.get('in_reply_to'):
                meta['in_reply_to'] = msg['in_reply_to']
            if msg.get('ext_client_id'):
                meta['ext_client_id'] = msg['ext_client_id']

            formatted_messages.append({
                'data': data,
                'meta': meta
            })

        return formatted_messages

# ################################################################################################################################

    def get_subscribed_topics(self, sub_key:'str') -> 'strlist':
        subs_key = self._get_subs_key(sub_key)
        return list(fs_set_smembers(self._cfg, subs_key))

# ################################################################################################################################

    def get_topic_subscribers(self, topic_name:'str') -> 'strlist':
        topic_subs_key = self._get_topic_subs_key(topic_name)
        return list(fs_set_smembers(self._cfg, topic_subs_key))

# ################################################################################################################################

    def delete_topic(self, topic_name:'str') -> 'None':
        stream_key = self._get_stream_key(topic_name)
        topic_subs_key = self._get_topic_subs_key(topic_name)

        subs = self.get_topic_subscribers(topic_name)

        for sub_key in subs:
            subs_key = self._get_subs_key(sub_key)
            _ = fs_set_srem(self._cfg, subs_key, [topic_name])

            try:
                fs_stream_xgroup_destroy(self._cfg, stream_key, sub_key)
            except Exception:
                pass

        try:
            fs_delete_tree(self._cfg, stream_key)
        except Exception:
            pass

        remaining_subs = list(fs_set_smembers(self._cfg, topic_subs_key))
        if remaining_subs:
            _ = fs_set_srem(self._cfg, topic_subs_key, remaining_subs)

# ################################################################################################################################

    def rename_topic(self, old_topic_name:'str', new_topic_name:'str') -> 'None':
        old_stream_key = self._get_stream_key(old_topic_name)
        new_stream_key = self._get_stream_key(new_topic_name)

        subs = self.get_topic_subscribers(old_topic_name)

        try:
            fs_rename(self._cfg, old_stream_key, new_stream_key)
        except Exception:
            pass

        old_topic_subs_key = self._get_topic_subs_key(old_topic_name)
        new_topic_subs_key = self._get_topic_subs_key(new_topic_name)

        old_members = list(fs_set_smembers(self._cfg, old_topic_subs_key))
        if old_members:
            _ = fs_set_sadd(self._cfg, new_topic_subs_key, old_members)
            _ = fs_set_srem(self._cfg, old_topic_subs_key, old_members)

        for sub_key in subs:
            subs_key = self._get_subs_key(sub_key)
            _ = fs_set_srem(self._cfg, subs_key, [old_topic_name])
            _ = fs_set_sadd(self._cfg, subs_key, [new_topic_name])

# ################################################################################################################################
# ################################################################################################################################
