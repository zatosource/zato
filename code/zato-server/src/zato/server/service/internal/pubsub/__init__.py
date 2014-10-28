# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import OK
from json import dumps, loads
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# Zato
from zato.common import PUB_SUB
from zato.server.service import Service
from zato.server.service.internal import AdminService

logger_overflown = getLogger('zato_pubsub_overflown')

# ################################################################################################################################

class DeleteExpired(AdminService):
    """ Invoked when a server is starting - periodically spawns a greenlet deleting expired messages.
    """
    def _delete_expired(self):
        self.logger.debug('Deleted expired messages %s', self.pubsub.impl.delete_expired())

    def handle(self):
        interval = float(self.server.fs_server_config.pubsub.delete_expired_interval)

        while True:
            self.logger.debug('Deleting expired messages, interval %rs', interval)
            spawn(self._delete_expired)
            sleep(interval)

# ################################################################################################################################

class InvokeCallbacks(AdminService):
    """ Invoked when a server is starting - periodically spawns a greenlet invoking consumer URL callbacks.
    """
    def _reject(self, msg_ids, sub_key, consumer, reason):
        self.pubsub.reject(sub_key, msg_ids)
        self.logger.error('Could not deliver messages `%s`, sub_key `%s` to `%s`, reason `%s`', msg_ids, sub_key, consumer, reason)
        
    def _invoke_callbacks(self):
        callback_consumers = list(self.pubsub.impl.get_callback_consumers())
        self.logger.debug('Callback consumers found `%s`', callback_consumers)

        for consumer in callback_consumers:
            with self.lock(consumer.sub_key):
                msg_ids = []
                request = []

                messages = self.pubsub.get(consumer.sub_key, get_format=PUB_SUB.GET_FORMAT.JSON.id)

                for msg in messages:
                    msg_ids.append(msg['metadata']['msg_id'])
                    request.append(msg)

                # messages is a generator so we still don't know if we had anything.
                if msg_ids:
                    conn = (self.outgoing.plain_http if consumer.callback_type == PUB_SUB.CALLBACK_TYPE.OUTCONN_PLAIN_HTTP else \
                        self.outgoing.soap)[consumer.callback_name].conn
                    try:
                        response = conn.post(self.cid, data=dumps(request), headers={'content-type': 'application/json'})
                    except Exception, e:
                        self._reject(msg_ids, consumer.sub_key, consumer, format_exc(e))
                    else:
                        if response.status_code == OK:
                            self.pubsub.acknowledge(consumer.sub_key, msg_ids)
                        else:
                            self._reject(
                                msg_ids, consumer.sub_key, consumer, '`{}` `{}`'.format(response.status_code, response.text))

    def handle(self):
        # TODO: self.logger's name should be 'zato_pubsub' so it got logged to the same location
        # the rest of pub/sub does.

        interval = float(self.server.fs_server_config.pubsub.invoke_callbacks_interval)

        while True:
            self.logger.debug('Invoking pub/sub callbacks, interval %rs', interval)
            spawn(self._invoke_callbacks)
            sleep(interval)

# ################################################################################################################################

class MoveToTargetQueues(AdminService):
    """ Invoked when a server is starting - periodically spawns a greenlet moving published messages to recipient queues.
    """
    def _move_to_target_queues(self):

        overflown = []

        for item in self.pubsub.impl.move_to_target_queues():
            for result, target_queue, msg_id in item:
                if result == PUB_SUB.MOVE_RESULT.OVERFLOW:
                    self.logger.warn('Message overflow, queue:`%s`, msg_id:`%s`', target_queue, msg_id)
                    overflown.append((target_queue[target_queue.rfind(':')+1:], msg_id))

        if overflown:
            self.invoke_async(StoreOverflownMessages.get_name(), overflown, to_json_string=True)

        self.logger.debug('Messages moved to target queues')

    def handle(self):
        interval = float(self.server.fs_server_config.pubsub.move_to_target_queues_interval)

        while True:
            self.logger.debug('Moving messages to target queues, interval %rs', interval)
            spawn(self._move_to_target_queues)
            sleep(interval)

# ################################################################################################################################

class StoreOverflownMessages(AdminService):
    """ Stores on filesystem messages that were above a consumer's max backlog and marks them as rejected by the consumer.
    """
    def handle(self):

        acks = {}

        for sub_key, msg_id in loads(self.request.payload):
            logger_overflown.warn('%s - %s - %s', msg_id, self.pubsub.get_consumer_by_sub_key(sub_key).name,
                self.pubsub.get_message(msg_id))

            msg_ids = acks.setdefault(sub_key, [])
            msg_ids.append(msg_id)

        for consumer_sub_key, msg_ids in acks.iteritems():
            self.pubsub.acknowledge(sub_key, msg_id)

# ################################################################################################################################

class RESTHandler(Service):
    """ Handles calls to pub/sub from REST clients.
    """
    def handle_POST(self):
        self.logger.warn('POST')

    def handle_GET(self):
        self.logger.warn('GET')

    def handle_DELETE(self):
        self.logger.warn('DELETE')

    def handle_PATCH(self):
        self.logger.warn('PATCH')

# ################################################################################################################################
