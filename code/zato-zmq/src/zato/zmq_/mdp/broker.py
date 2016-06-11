# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta
from traceback import format_exc

# gevent
from gevent.lock import RLock

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common import ZMQ
from zato.common.util import new_cid
from zato.zmq_.mdp import const, EventBrokerDisconnect, EventBrokerHeartbeat, EventClientReply, EventWorkerRequest, \
     Service, WorkerData

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Broker(object):
    """ Implements a broker part of the ZeroMQ Majordomo Protocol 0.1 http://rfc.zeromq.org/spec:7
    """
    def __init__(self, config):
        self.address = config.address
        self.poll_interval = config.poll_interval
        self.pool_strategy = config.pool_strategy
        self.keep_running = True
        self.has_debug = logger.isEnabledFor(logging.DEBUG)

        # A hundred years in seconds, used when creating internal workers
        self.y100 = 60 * 60 * 24 * 365 * 100

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

    def serve_forever(self):

        try:

            # Bind first to make sure we can actually start before logging the fact
            self.socket.bind(self.address)

            # Ok, we are actually running now
            logger.info('Starting ZMQ MDP 0.1 broker at %s', self.address)

            # To speed up look-ups
            has_debug = self.has_debug

            # Main loop
            while self.keep_running:

                try:
                    items = self.poller.poll(self.poll_interval)

                    # Periodically send heartbeats to all known workers
                    self.send_heartbeats()

                except KeyboardInterrupt:
                    self.send_disconnect_to_all()
                    break

                if items:
                    msg = self.socket.recv_multipart()
                    if has_debug:
                        logger.info('Received msg at %s %s', self.address, msg)

                    self.handle(msg)

                if has_debug:
                    logger.debug('No items for broker at %s', self.address)

        except Exception, e:
            logger.warn(format_exc(e))

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
        sender_id = msg[0]
        originator = msg[2]
        payload = msg[3:]

        with self.lock:
            func = self.handle_client_message if originator == const.v01.client else self.handle_worker_message
            func(sender_id, *payload)

# ################################################################################################################################

    def dispatch_requests(self, service_name):
        """ Sends all pending requests for that service, assuming there are workers available to handle them,
        or, if pool_strategy is 'single', creates a worker for that service if it does not exist already.
        """
        # Fetch the service object which at this point must exist
        service = self.services[service_name]

        # Clean up expired workers before attempting to deliver any messages
        self.cleanup_workers()

        if not service.has_workers:

            if self.pool_strategy == ZMQ.POOL_STRATEGY_NAME.SINGLE:
                self._add_worker('mdp.{}'.format(new_cid()), service.name, self.y100, const.worker_type.zato)
                service.has_workers = True
            else:
                raise NotImplementedError()

        while service.pending_requests and service.workers:
            req = service.pending_requests.pop(0)
            worker = self.workers.pop(service.workers.pop(0))

            func = self.send_to_worker_zato if worker.type == const.worker_type.zato else self.send_to_worker_zmq
            func(req.serialize(worker.unwrap_id()))

# ################################################################################################################################

    def handle_client_message(self, sender_id, service_name, received_body):
        """ Handles a single message from a client. This is the place where triggers the sending of all pending requests
        to workers for a given service name. Must be called with self.lock held.
        """

        # Create the service object if it does not exist - this may be the case
        # if clients connect before workers.
        service = self.services.setdefault(service_name, Service(service_name))
        service.pending_requests.append(EventWorkerRequest(received_body, sender_id))

        # Ok, we can send the request now to a worker
        self.dispatch_requests(service_name)

# ################################################################################################################################

    def send_to_worker_zmq(self, data):
        """ Sends a message to a ZeroMQ-based worker.
        """
        self.socket.send_multipart(data)

    def send_to_worker_zato(self, worker, msg_id, msg):
        """ Sends a message to a Zato service rather than an actual ZeroMQ socket.
        """
        raise NotImplementedError('send_to_worker_zato')

# ################################################################################################################################

    def handle_worker_message(self, worker_id, *payload):
        """ Handles a single message from a worker. Must be called with self.lock held.
        """
        event = payload[0]
        func = self.handle_event_map[event]
        func(worker_id, payload[1:])

# ################################################################################################################################

    def _add_worker(self, worker_id, service_name, ttl, worker_type):
        """ Adds worker-related configuration, no matter if it is an internal or a ZeroMQ-based one.
        """
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        wd = WorkerData(worker_type, worker_id, service_name, now, None, expires_at)

        # Add to details of workers
        self.workers[wd.id] = wd

        # Add to the list of workers for that service (but do not forget that the service may not have a client yet possibly)
        service = self.services.setdefault(service_name, Service(service_name))
        service.workers.append(wd.id)

        logger.info('Added worker: %s', wd)

# ################################################################################################################################

    def on_event_ready(self, worker_id, service_name):
        """ A worker informs the broker that it is ready to handle messages destined for a given service.
        Must be called with self.lock held.
        """
        self._add_worker(worker_id, service_name[0], const.ttl, const.worker_type.zmq)
        self.dispatch_requests(service_name)

    def on_event_reply(self, worker_id, data):
        recipient, _, body = data
        self.socket.send_multipart(EventClientReply(body, recipient, b'dummy-for-now').serialize())

    def on_event_heartbeat(self, worker_id, _ignored):
        """ Updates heartbeat data for a worker. Must be called with self.lock held.
        """
        wrapped_id = WorkerData.wrap_worker_id(const.worker_type.zmq, worker_id)
        worker = self.workers.get(wrapped_id)

        if not worker:
            logger.warn('No worker found for HB `%s`', wrapped_id)
            return

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=const.ttl)

        worker.last_hb_received = now
        worker.expires_at = expires_at

    def on_event_disconnect(self, worker_id, data):
        """ A worker wishes to disconnect - we need to remove it from all the places that still reference it, if any.
        """
        print(self.workers)
        with self.lock:
            wrapped_id = WorkerData.wrap_worker_id(const.worker_type.zmq, worker_id)

            # Need 'None' because the worker may not exist
            self.workers.pop(wrapped_id, None)

            for service in self.services.values():

                # Likewise, this worker may not exist at all
                if wrapped_id in service.workers:
                    service.workers.remove(wrapped_id)

            print(self.workers)

# ################################################################################################################################

if __name__ == '__main__':
    b = Broker(log_details=True)
    b.serve_forever()
