# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
import time
from json import dumps, loads
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep

# Redis
import redis

# Python 2/3 compatibility
from builtins import bytes

# Zato
from zato.common.api import BROKER, ZATO_NONE
from zato.common.broker_message import KEYS, MESSAGE_TYPE, TOPICS
from zato.common.kvdb.api import LuaContainer
from zato.common.util.api import new_cid, spawn_greenlet

logger = logging.getLogger(__name__)
has_debug = logger.isEnabledFor(logging.DEBUG)

REMOTE_END_CLOSED_SOCKET = 'Socket closed on remote end'
FILE_DESCR_CLOSED_IN_ANOTHER_GREENLET = "Error while reading from socket: (9, 'File descriptor was closed in another greenlet')"

# We use textual messages because some error may have codes whereas different won't.
EXPECTED_CONNECTION_ERRORS = [REMOTE_END_CLOSED_SOCKET, FILE_DESCR_CLOSED_IN_ANOTHER_GREENLET]

NEEDS_TMP_KEY = [v for k,v in TOPICS.items() if k in(
    MESSAGE_TYPE.TO_PARALLEL_ANY,
)]

CODE_RENAMED = 10
CODE_NO_SUCH_FROM_KEY = 11

# ################################################################################################################################

if 0:
    from zato.common.kvdb.api import KVDB

    KVDB = KVDB

# ################################################################################################################################

class BrokerClientAPI(object):
    """ BrokerClient is a function which cannot be used for type completion,
    hence this no-op class that can be used in type hints.
    """
    def __init__(self, kvdb, client_type, topic_callbacks, initial_lua_programs):
        # type: (KVDB, str, dict, dict)
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    def publish(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL, *ignored_args, **ignored_kwargs):
        # type: (dict, str, object, object)
        raise NotImplementedError()

    def invoke_async(self, msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_ANY, expiration=BROKER.DEFAULT_EXPIRATION):
        # type: (dict, str, object, object)
        raise NotImplementedError()

    def on_message(self, msg):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

# ################################################################################################################################
