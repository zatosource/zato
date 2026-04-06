# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads
from logging import getLogger
from threading import RLock

# gevent
from gevent import sleep, spawn

# zato-broker-core (Rust extension)
from zato_broker_core import (
    BrokerConfig,
    fs_init,
    fs_ping,
    fs_publish,
    fs_poll,
    fs_update_cursor,
    fs_read_cursor,
    fs_kv_get,
    fs_kv_set,
    fs_kv_delete,
    fs_kv_keys,
    fs_list_lpush,
    fs_list_ltrim,
    fs_list_lrange,
    fs_set_sadd,
    fs_set_srem,
    fs_set_smembers,
    fs_set_scard,
    fs_stream_xadd,
    fs_stream_xreadgroup,
    fs_stream_xack,
    fs_stream_xgroup_create,
    fs_stream_xgroup_destroy,
    fs_stream_xrange,
    fs_stream_xdel,
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any, Dict, List, Optional, Set

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class BrokerPubSub:
    """ Pub/sub subscription object compatible with the Redis pubsub interface.
    Polls broker channels in a background greenlet.
    """

    def __init__(self, client:'BrokerClient', poll_interval:'float'=0.05) -> 'None':
        self._client = client
        self._poll_interval = poll_interval
        self._channels:'Dict[str, int]' = {} # channel -> cursor
        self._running = False
        self._greenlet = None
        self._lock = RLock()
        self._messages:'list' = []

    def subscribe(self, *channels:'str', **kwargs:'Any') -> 'None':
        with self._lock:
            for ch in channels:
                if ch not in self._channels:
                    try:
                        cursor = fs_read_cursor(self._client._cfg, ch, self._client._subscriber_id)
                    except Exception:
                        cursor = 0
                    self._channels[ch] = cursor

            if not self._running:
                self._running = True
                self._greenlet = spawn(self._poll_loop)

    def unsubscribe(self, *channels:'str') -> 'None':
        with self._lock:
            if channels:
                for ch in channels:
                    self._channels.pop(ch, None)
            else:
                self._channels.clear()

            if not self._channels:
                self._running = False

    def get_message(self, timeout:'float'=1.0) -> 'Optional[Dict]':
        elapsed = 0.0
        step = min(self._poll_interval, timeout) if timeout > 0 else self._poll_interval

        while elapsed < timeout:
            with self._lock:
                if self._messages:
                    return self._messages.pop(0)
            sleep(step)
            elapsed += step

        with self._lock:
            if self._messages:
                return self._messages.pop(0)

        return None

    def close(self) -> 'None':
        self._running = False
        with self._lock:
            self._channels.clear()
            self._messages.clear()

        if self._greenlet:
            self._greenlet.kill()
            self._greenlet = None

    def _poll_loop(self) -> 'None':
        while self._running:
            try:
                with self._lock:
                    channels_snapshot = dict(self._channels)

                for channel, cursor in channels_snapshot.items():
                    try:
                        messages = fs_poll(self._client._cfg, channel, cursor)
                    except Exception:
                        continue

                    for seq, data in messages:
                        msg = {
                            'type': 'message',
                            'channel': channel,
                            'data': data,
                            'pattern': None,
                        }
                        with self._lock:
                            self._messages.append(msg)
                            self._channels[channel] = seq

                        try:
                            fs_update_cursor(
                                self._client._cfg, channel,
                                self._client._subscriber_id, seq,
                            )
                        except Exception:
                            pass

            except Exception as e:
                logger.warning('BrokerPubSub poll error: %s', e)

            sleep(self._poll_interval)

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:
    """ Broker client wrapping all Rust functions.
    Provides the same method signatures as a Redis client for pub/sub,
    key-value, lists, sets, and streams.
    """

    def __init__(
        self,
        root_dir:'str',
        poll_interval:'float'=0.05,
        log_dir:'str'='',
        do_fsync:'bool'=True,
        subscriber_id:'str'='default',
    ) -> 'None':
        self._root_dir = root_dir
        self._poll_interval = poll_interval
        self._subscriber_id = subscriber_id

        if not log_dir:
            log_dir = os.path.join(root_dir, 'logs')

        self._cfg = BrokerConfig(root_dir, log_dir, do_fsync)

        os.makedirs(log_dir, exist_ok=True)
        fs_init(self._cfg)

    @property
    def cfg(self) -> 'BrokerConfig':
        return self._cfg

    # ############################################################################################################################
    # Pub/sub
    # ############################################################################################################################

    def publish(self, channel:'str', message:'str') -> 'int':
        return fs_publish(self._cfg, channel, message)

    def pubsub(self) -> 'BrokerPubSub':
        return BrokerPubSub(self, poll_interval=self._poll_interval)

    # ############################################################################################################################
    # Key-value
    # ############################################################################################################################

    def get(self, key:'str') -> 'Optional[str]':
        return fs_kv_get(self._cfg, key)

    def set(self, key:'str', value:'str', ex:'Optional[int]'=None, nx:'bool'=False) -> 'Optional[bool]':
        return fs_kv_set(self._cfg, key, value, ex=ex, nx=nx)

    def delete(self, *keys:'str') -> 'int':
        return fs_kv_delete(self._cfg, list(keys))

    def keys(self, pattern:'str') -> 'List[str]':
        return fs_kv_keys(self._cfg, pattern)

    # ############################################################################################################################
    # Lists
    # ############################################################################################################################

    def lpush(self, key:'str', *values:'str') -> 'int':
        return fs_list_lpush(self._cfg, key, list(values))

    def ltrim(self, key:'str', start:'int', stop:'int') -> 'None':
        fs_list_ltrim(self._cfg, key, start, stop)

    def lrange(self, key:'str', start:'int', stop:'int') -> 'List[str]':
        return fs_list_lrange(self._cfg, key, start, stop)

    # ############################################################################################################################
    # Sets
    # ############################################################################################################################

    def sadd(self, key:'str', *members:'str') -> 'int':
        return fs_set_sadd(self._cfg, key, list(members))

    def srem(self, key:'str', *members:'str') -> 'int':
        return fs_set_srem(self._cfg, key, list(members))

    def smembers(self, key:'str') -> 'Set[str]':
        return set(fs_set_smembers(self._cfg, key))

    def scard(self, key:'str') -> 'int':
        return fs_set_scard(self._cfg, key)

    # ############################################################################################################################
    # Streams
    # ############################################################################################################################

    def xadd(self, key:'str', fields:'Dict', maxlen:'Optional[int]'=None) -> 'str':
        fields_json = dumps(fields)
        return fs_stream_xadd(self._cfg, key, fields_json, maxlen=maxlen)

    def xreadgroup(
        self,
        groupname:'str',
        consumername:'str',
        streams:'Dict[str, str]',
        count:'int'=100,
    ) -> 'List':
        result = []
        for stream_key in streams:
            entries = fs_stream_xreadgroup(self._cfg, stream_key, groupname, consumername, count)
            if entries:
                parsed = []
                for seq_id, fields_json in entries:
                    try:
                        fields = loads(fields_json)
                    except Exception:
                        fields = {'data': fields_json}
                    parsed.append((seq_id, fields))
                result.append((stream_key, parsed))
        return result

    def xack(self, key:'str', groupname:'str', *ids:'str') -> 'int':
        return fs_stream_xack(self._cfg, key, groupname, list(ids))

    def xgroup_create(self, key:'str', groupname:'str', id:'str'='$', mkstream:'bool'=False) -> 'None':
        fs_stream_xgroup_create(self._cfg, key, groupname, id, mkstream)

    def xgroup_destroy(self, key:'str', groupname:'str') -> 'None':
        fs_stream_xgroup_destroy(self._cfg, key, groupname)

    def xrange(self, key:'str', min:'str'='-', max:'str'='+', count:'Optional[int]'=None) -> 'List':
        entries = fs_stream_xrange(self._cfg, key, count=count)
        result = []
        for seq_id, fields_json in entries:
            try:
                fields = loads(fields_json)
            except Exception:
                fields = {'data': fields_json}
            result.append((seq_id, fields))
        return result

    def xdel(self, key:'str', *ids:'str') -> 'int':
        return fs_stream_xdel(self._cfg, key, list(ids))

    # ############################################################################################################################
    # Other
    # ############################################################################################################################

    def rename(self, old_key:'str', new_key:'str') -> 'None':
        from zato_broker_core import fs_rename
        fs_rename(self._cfg, old_key, new_key)

    def ping(self) -> 'bool':
        return fs_ping(self._cfg)

# ################################################################################################################################
# ################################################################################################################################
