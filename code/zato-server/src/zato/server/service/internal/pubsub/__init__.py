# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import OK
from json import dumps
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# requests
import requests

# Zato
from zato.common import PUB_SUB
from zato.server.service.internal import AdminService

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
                    conn = (self.outgoing.plain_http if consumer.callback_type == PUB_SUB.CALLBACK_TYPE.OUTCONN_PLAIN_HTP else \
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
        self.pubsub.impl.move_to_target_queues()
        self.logger.debug('Messages moved to target queues')

    def handle(self):
        interval = float(self.server.fs_server_config.pubsub.move_to_target_queues_interval)

        while True:
            self.logger.debug('Moving messages to target queues, interval %rs', interval)
            spawn(self._move_to_target_queues)
            sleep(interval)

# ################################################################################################################################
