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

# huTools
from huTools.structured import dict2xml

# Zato
from zato.common import PUB_SUB, ZATO_NONE, ZATO_OK, ZATO_ERROR
from zato.common.pubsub import ItemFull
from zato.server.connection.http_soap import BadRequest, Forbidden, TooManyRequests, Unauthorized
from zato.server.service import Int, Service
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
    class SimpleIO(object):
        input_required = ('item_type', 'item',)
        input_optional = ('max', 'dir', 'format')
        default = ZATO_NONE

# ################################################################################################################################

    def validate_input(self):
        sub_key = self.wsgi_environ.get('HTTP_X_ZATO_PUBSUB_KEY', ZATO_NONE)

        if not self.pubsub.get_consumer_by_sub_key(sub_key):
            raise Unauthorized(self.cid, 'You are not authorized to access this resource', 'Zato pub/sub')

        if self.request.input.item_type not in PUB_SUB.URL_ITEM_TYPE:
            raise BadRequest(self.cid, 'None of the supported resources ({}) found in URL path'.format(
                ', '.join(PUB_SUB.URL_ITEM_TYPE)))

        self.environ.sub_key = sub_key

# ################################################################################################################################

    def _handle_POST_msg(self):

        out = {
            'status': ZATO_OK,
            'results_count': 0,
            'results': []
        }

        max_batch_size = int(self.request.input.max) if self.request.input.max else PUB_SUB.DEFAULT_GET_MAX_BATCH_SIZE
        is_fifo = True if (self.request.input.dir == PUB_SUB.GET_DIR.FIFO or not self.request.input.dir) else False
        get_format = self.request.input.format if self.request.input.format else PUB_SUB.GET_FORMAT.DEFAULT.id
        is_json = get_format == PUB_SUB.GET_FORMAT.JSON.id

        try:
            for item in self.pubsub.get(self.environ.sub_key, max_batch_size, is_fifo, get_format):

                if is_json:
                    out_item = item
                else:
                    out_item = {'metadata': item.to_dict()}
                    out_item['payload'] = item.payload

                out['results'].append(out_item)
                out['results_count'] += 1

        except ItemFull, e:
            raise TooManyRequests(self.cid, e.msg)
        else:
            if is_json:
                content_type = 'application/json'
                out = dumps(out)
            else:
                content_type = 'application/xml'
                out = dict2xml(out)

            self.response.headers['Content-Type'] = content_type
            self.response.payload = out

# ################################################################################################################################

    def handle_POST(self):

        getattr(self, '_handle_POST_{}'.format(self.request.input.item_type))()

    def handle_DELETE(self):
        self.logger.warn('DELETE')

    def handle_PATCH(self):
        self.logger.warn('PATCH')

# ################################################################################################################################
