# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta

# gevent
from gevent.lock import RLock

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.zmq_.mdp import const, EventClientReply, EventWorkerRequest, EventWorkerReply, Service, WorkerData

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Broker(object):
    """ Standalone implementation of a broker for ZeroMQ Majordomo Protocol 0.1 http://rfc.zeromq.org/spec:7
    """
    def __init__(self, address='tcp://*:47047', linger=0, poll_interval=100, log_details=False):
        self.address = address
        self.poll_interval = poll_interval
        self.keep_running = True
        self.log_details = log_details
        self.has_debug = logger.isEnabledFor(logging.DEBUG)

        # Maps service names to workers registered to handle requests to that service
        self.services = {}

        # Details about each worker, mapped by worker_id:Worker object 
        self.workers = {}

        self.lock = RLock()

        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.ROUTER)
        self.socket.linger = linger
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

        # Bind first to make sure we can actually start before logging the fact
        self.socket.bind(self.address)

        # Ok, we are actually running now
        logger.info('Starting ZMQ MDP 0.1 broker at %s', self.address)

        # To speed up look-ups
        log_details = self.log_details
        has_debug = self.has_debug

        # Main loop
        while self.keep_running:

            try:
                items = self.poller.poll(self.poll_interval)
            except KeyboardInterrupt:
                break

            if items:
                msg = self.socket.recv_multipart()
                if has_debug:
                    logger.info('Received msg at %s %s', self.address, msg)

                self.handle(msg)

            elif has_debug:
                logger.debug('No items for broker at %s', self.address)

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

    def handle(self, msg):
        """ Handles a message received from the socket.
        """
        sender_id = msg[0]
        originator = msg[2]
        payload = msg[3:]

        with self.lock:
            func = self.handle_client if originator == const.v01.client else self.handle_worker
            func(sender_id, *payload)

# ################################################################################################################################

    def handle_client(self, sender_id, service_name, received_body):
        """ Handles a single request from a client. This is the place where triggers the sending of all pending requests
        to workers for a given service name. Must be called with self.lock held.
        """

        # Create the service object if it does not exist - this may be the case
        # if clients connect before workers.
        service = self.services.setdefault(service_name, Service(service_name))
        service.pending_requests.append(EventWorkerRequest(received_body, sender_id))

        # Clean up expired workers before attempting to deliver any messages
        self.cleanup_workers()

        while service.pending_requests and service.workers:
            req = service.pending_requests.pop(0)
            worker = self.workers.pop(service.workers.pop(0))

            func = self.send_to_worker_zato if worker.type == const.worker_type.zato else self.send_to_worker_zmq
            func(req.serialize(worker.unwrap_id()))

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

    def handle_worker(self, sender_id, *payload):
        """ Handles a single request from a worker. Must be called with self.lock held.
        """
        event = payload[0]
        func = self.handle_event_map[event]
        func(sender_id, payload[1:])

# ################################################################################################################################

    def on_event_ready(self, sender_id, service_name):
        """ A worker informs the broker that it is ready to handle messages destined for a given service.
        Must be called with self.lock held.
        """
        service_name = service_name[0]

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=const.ttl)
        wd = WorkerData(const.worker_type.zmq, sender_id, service_name, expires_at)

        # Add to details of workers
        self.workers[wd.id] = wd

        # Add to the list of workers for that service (but do not forget that the service may not have a client yet possibly)
        service = self.services.setdefault(service_name, Service(service_name))
        service.workers.append(wd.id)

        logger.info('Added worker: %s', wd)

    def on_event_reply(self, sender_id, data):
        recipient, _, body = data
        self.socket.send_multipart(EventClientReply(body, recipient, b'dummy-for-now').serialize())

    def on_event_heartbeat(self):
        raise NotImplementedError()

    def on_event_disconnect(self):
        raise NotImplementedError()

# ################################################################################################################################

if __name__ == '__main__':
    b = Broker(log_details=1)
    b.serve_forever()
