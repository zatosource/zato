# -*- coding: utf-8 -*-

# flake8: noqa
# pylint: disable=all

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent import spawn
from gevent.lock import RLock

# ZeroMQ
import zmq.green as zmq

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring

# Zato
from zato.common.api import CHANNEL, ZMQ
from zato.common.util.api import new_cid, wait_until_port_free
from zato.zmq_.mdp import const, EventBrokerDisconnect, EventBrokerHeartbeat, EventClientReply, EventWorkerRequest, \
     Service, WorkerData

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Broker:
    """ Implements a broker part of the ZeroMQ Majordomo Protocol 0.1 http://rfc.zeromq.org/spec:7
    """
    def __init__(self, config, on_message_callback):
        self.config = config
        self.on_message_callback = on_message_callback
        self.address = config.address
        self.poll_interval = config.poll_interval
        self.pool_strategy = config.pool_strategy
        self.service_source = config.service_source
        self.keep_running = True
        self.tcp_port = int(self.address.split(':')[-1])

        # A hundred years in seconds, used when creating internal workers
        self.y100 = 60 * 60 * 24 * 365 * 100

        # So they do not have to be looked up on each request or event
        self.has_info = logger.isEnabledFor(logging.INFO)
        self.has_debug = logger.isEnabledFor(logging.DEBUG)
        self.has_pool_strategy_simple = self.pool_strategy == ZMQ.POOL_STRATEGY_NAME.SINGLE
        self.has_service_source_zato = self.service_source == ZMQ.SERVICE_SOURCE_NAME.ZATO
        self.zato_service_name = config.service_name
        self.zato_channel = CHANNEL.ZMQ

        if self.has_pool_strategy_simple:
            self.workers_pool_initial = 1
            self.workers_pool_mult = 0
            self.workers_pool_max = 1
        else:
            self.workers_pool_initial = config.workers_pool_initial
            self.workers_pool_mult = config.workers_pool_mult
            self.workers_pool_max = config.workers_pool_max

        # Maps service names to workers registered to handle requests to that service
        self.services = {}

        # Details about each worker, mapped by worker_id:Worker object
        self.workers = {}

        # Held upon most operations on sockets
        self.lock = RLock()

        # How often, in seconds, to send a heartbeat to workers
        self.heartbeat = config.heartbeat

        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.ROUTER)
        self.socket.linger = config.linger
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        # Maps event IDs to methods that handle a given one
        self.handle_event_map = {
            const.v01.ready: self.on_event_ready,
            const.v01.reply_from_worker: self.on_event_reply,
            const.v01.heartbeat: self.on_event_heartbeat,
            const.v01.disconnect: self.on_event_disconnect,
        }

# ################################################################################################################################

    def close(self, linger):
        self.keep_running = False
        self.socket.close(linger)

        # Wait at most 10 seconds until the port is released
        if not wait_until_port_free(self.tcp_port, 10):
            logger.warning('Port `%s` was not released within 10s', self.tcp_port)

# ################################################################################################################################

    def serve_forever(self):

        # To speed up look-ups
        has_debug = self.has_debug

        try:

            # Bind first to make sure we can actually start before logging the fact
            self.socket.bind(self.address)

            # Ok, we are actually running now
            logger.info('Starting ZMQ MDP 0.1 broker at %s', self.address)

        except Exception:
            logger.warning('Could not bind to `%s`, e:`%s`', self.address, format_exc())

        # Main loop
        while self.keep_running:

            try:
                items = self.poller.poll(self.poll_interval)

                # Periodically send heartbeats to all known workers
                self.send_heartbeats()

                if items:
                    msg = self.socket.recv_multipart()

                    if has_debug:
                        logger.info('Received msg at %s %s', self.address, msg)

                    spawn(self.handle, msg)

                if has_debug:
                    logger.debug('No items for broker at %s', self.address)

            except KeyboardInterrupt:
                self.send_disconnect_to_all()
                break

            except Exception:
                logger.warning(format_exc())

# ################################################################################################################################

    def cleanup_workers(self):
        """ Goes through all the workers and deletes any that are expired in any place they are referred to.
        Must be called with self.lock held.
        """
        now = datetime.utcnow()

        # All workers that are found to have expired
        expired = []

        # Find expired workers
        for worker in self.workers.values():
            if now >= worker.expires_at:
                expired.append(worker.id)

        # Remove expired workers from their main dict and any service that may depend on it
        for item in expired:
            del self.workers[item]

            for service in self.services.values():
                service.workers.remove(item)

# ################################################################################################################################

    def send_disconnect_to_all(self):
        """ Sends a disconnect event to all workers.
        """
        with self.lock:

            # No point in connecting to invalid workers
            self.cleanup_workers()

            for worker in self.workers.values():
                self.send_to_worker_zmq(EventBrokerDisconnect().serialize(worker.unwrap_id()))

# ################################################################################################################################

    def send_heartbeats(self):
        """ Cleans up expired workers and sends heartbeats to any remaining ones.
        """
        now = datetime.utcnow()

        with self.lock:

            # Make sure we send heartbeats only to workers that have not expired already
            self.cleanup_workers()

            for worker in self.workers.values():

                # Do not send heart-beats to internal workers, only to actual wire-based ZeroMQ ones
                if worker.type == const.worker_type.zmq:

                    # We have never sent a HB to this worker or we have sent a HB at least once so we do it again now
                    if not worker.last_hb_sent or now >= worker.last_hb_sent + timedelta(seconds=self.heartbeat):
                        self._send_heartbeat(worker, now)

# ################################################################################################################################

    def _send_heartbeat(self, worker, now):
        self.send_to_worker_zmq(EventBrokerHeartbeat(worker.unwrap_id()).serialize())
        worker.last_hb_sent = now

# ################################################################################################################################

    def handle(self, msg):
        """ Handles a message received from the socket.
        """
        try:
            sender_id = msg[0]
            originator = msg[2]
            payload = msg[3:]

            func = self.handle_client_message if originator == const.v01.client else self.handle_worker_message
            func(sender_id, *payload)

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def _add_workers(self, service, n):
        """ Adds n workers to a service
        """
        logger.info(
            'ZeroMQ MDP channel `%s` adding %s worker{} for `%s`'.format('' if n==1 else 's'),
            self.config.name, n, service.name)

        for _x in range(n):
            self._add_worker('mdp.{}'.format(new_cid()), service.name, self.y100, const.worker_type.zato)

    def add_workers(self, service):
        """ Logic to add a pool of workers to the service - how many to add in each batch and what the limit is
        has been already precomputed in __init__. This method assumes that the fact that it is being invoked
        means that the service has no workers available at this moment.
        """
        with self.lock:

            # Ok, it's the first time around so we just assign the initial batch of workers
            if not service.has_initialized_workers:
                self._add_workers(service, self.workers_pool_initial)
                service.has_initialized_workers = True
                service.len_current_workers = self.workers_pool_initial

            # Expand the worker pool with as many workers as possible but without exceeding the limit
            else:
                how_many_to_add = service.len_current_workers * self.workers_pool_mult

                # Make sure we do not add workers beyond the limit
                if service.len_current_workers + how_many_to_add > self.workers_pool_max:
                    how_many_to_add = self.workers_pool_max - service.len_current_workers

                self._add_workers(service, how_many_to_add)
                service.len_current_workers += how_many_to_add

            if service.len_current_workers >= self.workers_pool_max:
                service.has_max_workers = True

# ################################################################################################################################

    def dispatch_requests(self, service_name):
        """ Sends all pending requests for that service, assuming there are workers available to handle them,
        or, if pool_strategy is 'single', creates a worker for that service if it does not exist already.
        """
        # Fetch the service object which at this point must exist
        service = self.services[service_name]

        # Clean up expired workers before attempting to deliver any messages
        self.cleanup_workers()

        if not service.workers:

            if service.has_max_workers:
                msg = 'ZeroMQ MDP channel `%s` cannot add more workers for service `%s` (reached max=%s)'
                logger.warning(msg, self.config.name, service_name, self.workers_pool_max)
                return

            self.add_workers(service)

        while service.pending_requests and service.workers:
            req = service.pending_requests.pop(0)
            worker = self.workers.pop(service.workers.pop(0))

            if worker.type == const.worker_type.zato:
                self.send_to_worker_zato(req, worker, service_name)
            else:
                self.send_to_worker_zmq(req.serialize(worker.unwrap_id()))

# ################################################################################################################################

    def handle_client_message(self, sender_id, service_name, received_body):
        """ Handles a single message from a client. This is the place where triggers the sending of all pending requests
        to workers for a given service name.
        """
        # Create the service object if it does not exist - this may be the case
        # if clients connect before workers.
        with self.lock:
            service = self.services.setdefault(service_name, Service(service_name))
            service.pending_requests.append(EventWorkerRequest(received_body, sender_id))

        # Ok, we can send the request now to a worker
        self.dispatch_requests(service_name)

# ################################################################################################################################

    def send_to_worker_zmq(self, data):
        """ Sends a message to a ZeroMQ-based worker.
        """
        self.socket.send_multipart(data)

    def _invoke_service(self, service, request):
        return self.on_message_callback({
                'cid': new_cid(),
                'service': service,
                'channel': self.zato_channel,
                'payload': request
        }, self.zato_channel, None, needs_response=True)

    def send_to_worker_zato(self, request, worker, zmq_service_name):
        """ Sends a message to a Zato service rather than an actual ZeroMQ socket.
        """
        try:

            # If the caller wants to invoke a pre-defined service then we let it in
            # since the person who created this channel knows what they are doing.

            if self.has_service_source_zato:
                is_allowed = True
                service = self.zato_service_name

            # However, if the caller wants to invoke a service by its name then we first need
            # to consult a user-defined authorization service and ask if the caller is allowed to do it.
            else:
                is_allowed = self._invoke_service(self.zato_service_name, request)
                service = zmq_service_name

            # Invoke the final service and return response to the caller - note however that if the caller
            # is not allowed to invoke that service then no response is ever returned.
            if is_allowed:

                # Always need to respond with bytes - this is what PyZMQ API requires
                response = self._invoke_service(service, request)

                if isinstance(response, basestring) and not isinstance(response, bytes):
                    response = response.encode('utf-8')

                else:
                    response = (b'%s' % response) if response is not None else b''

                self._reply(request.client, response)

            else:
                logger.warning('Client `%r` is not allowed to invoke `%s` through `%s`', request.client, service, self.zato_service_name)

        finally:
            # Whether the service was invoked or not we need to add this worker back to the pool
            # (we actually add a new one for the same service but it amounts to the same thing).
            with self.lock:
                self._add_worker(worker.id, worker.service_name, self.y100, const.worker_type.zato)

# ################################################################################################################################

    def handle_worker_message(self, worker_id, *payload):
        """ Handles a single message from a worker.
        """
        event = payload[0]
        func = self.handle_event_map[event]
        func(worker_id, payload[1:])

# ################################################################################################################################

    def _add_worker(self, worker_id, service_name, ttl, worker_type, log_added=True):
        """ Adds worker-related configuration, no matter if it is an internal or a ZeroMQ-based one.
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl)
        wd = WorkerData(worker_type, worker_id, service_name, now, None, expires_at)

        # Add to details of workers
        self.workers[wd.id] = wd

        # Add to the list of workers for that service (but do not forget that the service may not have a client yet possibly)
        service = self.services.setdefault(service_name, Service(service_name))
        service.workers.append(wd.id)

# ################################################################################################################################

    def _reply(self, recipient, body):
        self.socket.send_multipart(EventClientReply(body, recipient, b'dummy-for-now').serialize())

# ################################################################################################################################

    def on_event_ready(self, worker_id, service_name):
        """ A worker informs the broker that it is ready to handle messages destined for a given service.
        Must be called with self.lock held.
        """
        service_name = service_name[0]

        if self.has_info:
            logger.info('Worker `%r` ready for `%s`',
                WorkerData.wrap_worker_id(const.worker_type.zmq, worker_id), service_name)

        with self.lock:
            self._add_worker(worker_id, service_name, const.ttl, const.worker_type.zmq)

        self.dispatch_requests(service_name)

    def on_event_reply(self, worker_id, data):
        recipient, _, body = data
        self._reply(recipient, body)

    def on_event_heartbeat(self, worker_id, _ignored):
        """ Updates heartbeat data for a worker.
        """
        with self.lock:
            wrapped_id = WorkerData.wrap_worker_id(const.worker_type.zmq, worker_id)
            worker = self.workers.get(wrapped_id)

            if not worker:
                logger.warning('No worker found for HB `%s`', wrapped_id)
                return

            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=const.ttl)

            worker.last_hb_received = now
            worker.expires_at = expires_at

    def on_event_disconnect(self, worker_id, data):
        """ A worker wishes to disconnect - we need to remove it from all the places that still reference it, if any.
        """
        with self.lock:
            wrapped_id = WorkerData.wrap_worker_id(const.worker_type.zmq, worker_id)

            # Need 'None' because the worker may not exist
            self.workers.pop(wrapped_id, None)

            for service in self.services.values():

                # Likewise, this worker may not exist at all
                if wrapped_id in service.workers:
                    service.workers.remove(wrapped_id)

# ################################################################################################################################

if __name__ == '__main__':

    config = Bunch()

    config.name = 'Just testing'
    config.address = 'tcp://*:47047'
    config.poll_interval = 100
    config.pool_strategy = 'simple'
    config.service_source = ZMQ.SERVICE_SOURCE_NAME.ZATO
    config.service_impl_name = 'zzz.MyService'
    config.service_name = 'zzz.my-service'
    config.workers_pool_initial = 10
    config.workers_pool_mult = 2
    config.workers_pool_max = 250
    config.heartbeat = 3
    config.linger = 0

    def on_message_callback(msg, channel, action, args=None, **kwargs):
        logger.info('Got MDP message %s %s %s', msg, channel, action)
        return 'zzz'

    b = Broker(config, on_message_callback)
    b.serve_forever()
