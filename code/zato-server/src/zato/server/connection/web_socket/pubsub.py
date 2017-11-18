# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime, timedelta
from errno import EADDRINUSE
from httplib import BAD_REQUEST, INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from logging import getLogger
from random import randint
from socket import error as SocketError
from traceback import format_exc
from urlparse import urlparse

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, socket, spawn
from gevent.lock import RLock

# pyrapidjson
from rapidjson import loads

# sortedcontainers
from sortedcontainers import SortedList

# ws4py
from ws4py.websocket import WebSocket as _WebSocket
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication

# Zato
from zato.common import CHANNEL, DATA_FORMAT, ParsingException, SEC_DEF_TYPE, WEB_SOCKET
from zato.common.exception import Reportable
from zato.common.time_util import datetime_from_ms
from zato.common.util import new_cid, spawn_greenlet
from zato.server.connection.connector import Connector
from zato.server.connection.web_socket.msg import AuthenticateResponse, ClientInvokeRequest, ClientMessage, copy_forbidden, \
     error_response, ErrorResponse, Forbidden, OKResponse
from zato.server.pubsub import PubSub
from zato.vault.client import VAULT

# For pyflakes
PubSub = PubSub


# ################################################################################################################################

logger = getLogger('zato_web_socket')

# ################################################################################################################################

http404 = b'{} {}'.format(NOT_FOUND, responses[NOT_FOUND])

# ################################################################################################################################

_wsgi_drop_keys = ('ws4py.socket', 'wsgi.errors', 'wsgi.input')

# ################################################################################################################################

VAULT_TOKEN_HEADER=VAULT.HEADERS.TOKEN_RESPONSE

# ################################################################################################################################

class PubSubTask(object):
    """ A background task responsible for delivery of pub/sub messages each WebSocket connections may possible subscribe to.
    """
    def __init__(self, sql_conn_func):
        self.sql_conn_func = sql_conn_func
        self.lock = RLock()

# ################################################################################################################################

class DeliveryTask(object):
    """ Runs a greenlet responsible for delivery of messages for a given sub_key.
    """
    def __init__(self, sub_key, delivery_lock, delivery_list, deliver_pubsub_msg_cb, confirm_pubsub_msg_delivered_cb):
        self.keep_running = True
        self.sub_key = sub_key
        self.delivery_lock = delivery_lock
        self.delivery_list = delivery_list
        self.deliver_pubsub_msg_cb = deliver_pubsub_msg_cb
        self.confirm_pubsub_msg_delivered_cb = confirm_pubsub_msg_delivered_cb

        spawn_greenlet(self.run)

    def _run_delivery(self):
        """ Actually attempts to deliver messages. Each time it runs, it gets all the messages
        that are still to be delivered from self.delivery_list.
        """
        for msg in self.delivery_list:
            try:
                self.deliver_pubsub_msg_cb(msg)

            except Exception, e:
                logger.warn('Could not deliver pub/sub message, e:`%s`', format_exc(e))

                # Do not attempt to deliver any other message, simply return and our
                # parent will sleep for a small amount of time and then re-run us,
                # thanks to which the next time we run we will again iterate over all the messages
                # currently queued up
                return

            else:
                # On successful delivery, remove this messages from SQL and our own delivery_list
                try:
                    self.confirm_pubsub_msg_delivered_cb(self.sub_key, msg.pub_msg_id)
                except Exception, e:
                    logger.warn('Could not update delivery status for msg:`%s`, e:`%s`', msg, format_exc(e))
                else:
                    with self.delivery_lock:
                        self.delivery_list.remove(msg)

        # Indicates that we have successfully delivered all messages currently queued up
        return True

    def run(self, no_msg_sleep_time=1):
        try:
            while self.keep_running:
                logger.warn('DLVLIST %s', hex(id(self.delivery_list)))

                if not self.delivery_list:
                    sleep(no_msg_sleep_time) # No need to wake up too often if there is not much to do
                else:

                    # Get the list of all messaged IDs for which delivery was successful,
                    # indicating whether all currently lined up messages have been
                    # successfully delivered.
                    success = self._run_delivery()

                    # On success, sleep for a moment because we have just run out of all messages.
                    if success:
                        sleep(no_msg_sleep_time)

                    # Otherwise, sleep for a longer time because our endpoint must have returned an error.
                    # After this sleep, self._run_delivery will again attempt to deliver all messages
                    # we queued up. Note that we are the only delivery task for this sub_key  so when we sleep here
                    # for a moment, we do not block other deliveries.
                    else:
                        sleep(randint(10, 20))
        except Exception, e:
            logger.warn('Exception in delivery task for sub_key:`%s`, e:`%s`', self.sub_key, format_exc(e))

    def stop(self):
        logger.warn('Stopping delivery task for sub_key:`%s`', self.sub_key)
        self.keep_running = False

# ################################################################################################################################

class Message(object):
    """ Wrapper for messages adding __cmp__ which uses a custom comparison protocol,
    by priority, then ext_pub_time, then pub_time.
    """
    def __init__(self, msg):
        self.id = msg.id
        self.pub_msg_id = msg.pub_msg_id
        self.pub_correl_id = msg.pub_correl_id
        self.in_reply_to = msg.in_reply_to
        self.ext_client_id = msg.ext_client_id
        self.group_id = msg.group_id
        self.position_in_group = msg.position_in_group
        self.pub_time = msg.pub_time
        self.ext_pub_time = msg.ext_pub_time
        self.data = msg.data
        self.mime_type = msg.mime_type
        self.priority = msg.priority
        self.expiration = msg.expiration
        self.expiration_time = msg.expiration_time

    def __cmp__(self, other, max_pri=9):
        return cmp(
            (max_pri - self.priority, self.ext_pub_time, self.pub_time),
            (max_pri - other.priority, other.ext_pub_time, other.pub_time)
        )

    def __repr__(self):
        return '<Msg id:{} pub_id:{} ext_cli:{} exp:{}>'.format(
            self.id, self.pub_msg_id, self.ext_client_id, datetime_from_ms(self.expiration_time))

    def to_dict(self):
        return {
            'id': self.id,
        }

# ################################################################################################################################

class PubSubTool(object):
    """ A utility object for pub/sub-related tasks.
    """
    def __init__(self, pubsub, web_socket):
        self.pubsub = pubsub # type: PubSub
        self.web_socket = web_socket # type: WebSocket

        # A broad lock for generic pub/sub matters
        self.lock = RLock()

        # Each sub_key will get its own lock for operations related to that key only
        self.sub_key_locks = {}

        # How many messages to send in a single delivery group,
        # may be set individually for each subscription, defaults to 1
        self.batch_size = {}

        # Which sub_keys this WSX client handles
        self.sub_keys = []

        # A sorted list of message references for each sub_key
        self.delivery_lists = {}

        # A pub/sub delivery task for each sub_key
        self.delivery_tasks = {}

        # For each sub key, when was an SQL query last executed
        # that SELECT-ed latest messages for that sub_key.
        self.last_sql_run = {}

# ################################################################################################################################

    def add_sub_key(self, sub_key):
        with self.lock:
            self.sub_keys.append(sub_key)
            self.batch_size[sub_key] = 1
            self.last_sql_run[sub_key] = None

            delivery_list = SortedList()
            delivery_lock = RLock()

            self.delivery_lists[sub_key] = delivery_list
            self.delivery_tasks[sub_key] = DeliveryTask(
                sub_key, delivery_lock, delivery_list, self.web_socket.deliver_pubsub_msg, self.confirm_pubsub_msg_delivered)

            self.sub_key_locks[sub_key] = delivery_lock

# ################################################################################################################################

    def remove_sub_key(self, sub_key):
        with self.lock:
            try:
                self.sub_keys.remove(sub_key)
                del self.batch_size[sub_key]
                del self.last_sql_run[sub_key]
                del self.sub_key_locks[sub_key]

                del self.delivery_lists[sub_key]
                self.delivery_tasks[sub_key].stop()
                del self.delivery_tasks[sub_key]

            except Exception, e:
                logger.warn('Exception during sub_key removal `%s`, e:`%s`', sub_key, format_exc(e))

# ################################################################################################################################

    def remove_all_sub_keys(self):
        sub_keys = deepcopy(self.sub_keys)
        for sub_key in sub_keys:
            self.remove_sub_key(sub_key)

# ################################################################################################################################

    def add_messages_by_sub_key(self, sub_key):
        with self.sub_key_locks[sub_key]:
            messages = self.pubsub.get_sql_messages_by_sub_key(sub_key, self.last_sql_run[sub_key])

            for msg in messages:
                logger.warn('333 %s', msg)
                self.delivery_lists[sub_key].add(Message(msg))

            logger.warn('444 %s', hex(id(self.delivery_lists[sub_key])))

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, sub_key, pub_msg_id):
        self.pubsub.confirm_pubsub_msg_delivered(sub_key, pub_msg_id)

# ################################################################################################################################
