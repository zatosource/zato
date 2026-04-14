# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads
from logging import getLogger

# zato-broker-core (Rust extension)
from zato_broker_core import (
    BrokerConfig,
    broker_init,
    broker_ping,
    broker_rename,
    broker_stream_xadd,
    broker_stream_xreadgroup,
    broker_stream_xack,
    broker_stream_xgroup_create,
    broker_stream_xgroup_destroy,
    broker_stream_xrange,
    broker_stream_xdel,
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any, Dict, List, Optional

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class BrokerPubSub:

    def __init__(self, client:'BrokerClient', poll_interval:'float'=0.05) -> 'None':
        logger.warning('BrokerPubSub needs to be ported to streams')

    def subscribe(self, *channels:'str', **kwargs:'Any') -> 'None':
        logger.warning('BrokerPubSub.subscribe needs to be ported to streams')

    def unsubscribe(self, *channels:'str') -> 'None':
        logger.warning('BrokerPubSub.unsubscribe needs to be ported to streams')

    def get_message(self, timeout:'float'=1.0) -> 'Optional[Dict]':
        logger.warning('BrokerPubSub.get_message needs to be ported to streams')
        return None

    def close(self) -> 'None':
        logger.warning('BrokerPubSub.close needs to be ported to streams')

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:

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
        broker_init(self._cfg)

    @property
    def cfg(self) -> 'BrokerConfig':
        return self._cfg

    # ############################################################################################################################
    # Pub/sub
    # ############################################################################################################################

    def publish(self, channel:'str', message:'str', data:'bytes'=b'') -> 'int':
        logger.warning('BrokerClient.publish needs to be ported to streams')
        return 0

    def pubsub(self) -> 'BrokerPubSub':
        logger.warning('BrokerClient.pubsub needs to be ported to streams')
        return BrokerPubSub(self)

    # ############################################################################################################################
    # Streams
    # ############################################################################################################################

    def xadd(self, key:'str', fields:'Dict', maxlen:'Optional[int]'=None, payload:'bytes | None'=None) -> 'str':
        fields_json = dumps(fields)
        return broker_stream_xadd(self._cfg, key, fields_json, maxlen=maxlen, payload=payload)

    def xreadgroup(
        self,
        groupname:'str',
        consumername:'str',
        streams:'Dict[str, str]',
        count:'int'=100,
    ) -> 'List':
        result = []
        for stream_key in streams:
            entries = broker_stream_xreadgroup(self._cfg, stream_key, groupname, consumername, count)
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
        return broker_stream_xack(self._cfg, key, groupname, list(ids))

    def xgroup_create(self, key:'str', groupname:'str', id:'str'='$', mkstream:'bool'=False) -> 'None':
        broker_stream_xgroup_create(self._cfg, key, groupname, id, mkstream)

    def xgroup_destroy(self, key:'str', groupname:'str') -> 'None':
        broker_stream_xgroup_destroy(self._cfg, key, groupname)

    def xrange(self, key:'str', min:'str'='-', max:'str'='+', count:'Optional[int]'=None) -> 'List':
        entries = broker_stream_xrange(self._cfg, key, count=count)
        result = []
        for seq_id, fields_json in entries:
            try:
                fields = loads(fields_json)
            except Exception:
                fields = {'data': fields_json}
            result.append((seq_id, fields))
        return result

    def xdel(self, key:'str', *ids:'str') -> 'int':
        return broker_stream_xdel(self._cfg, key, list(ids))

    # ############################################################################################################################
    # Other
    # ############################################################################################################################

    def rename(self, old_key:'str', new_key:'str') -> 'None':
        broker_rename(self._cfg, old_key, new_key)

    def ping(self) -> 'bool':
        return broker_ping(self._cfg)

# ################################################################################################################################
# ################################################################################################################################
