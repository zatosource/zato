# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.zmq_.mdp import BaseZMQConnection, const, EventReady, EventWorkerReply

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Worker(BaseZMQConnection):
    """ Standalone implementation of a worker for ZeroMQ Majordomo Protocol 0.1 http://rfc.zeromq.org/spec:7
    """
    def __init__(self, service_name, broker_address='tcp://localhost:47047', linger=0, poll_interval=100, log_details=False,
            heartbeat=3, heartbeat_mult=3):
        self.service_name = service_name
        super(Worker, self).__init__(broker_address, linger, poll_interval, log_details)

        self.worker_socket = self.ctx.socket(zmq.DEALER)
        self.worker_socket.linger = self.linger
        self.worker_poller = zmq.Poller()
        self.worker_poller.register(self.worker_socket, zmq.POLLIN)

        # How often, in seconds, to send a heartbeat to the broker
        self.heartbeat = heartbeat

        # If self.heartbeat * self.heartbeat_mult is exceeded, we assume the broker is down
        self.heartbeat_mult = heartbeat_mult

        # When did we last hear from the broker
        self.broker_last_heartbeat = None

        # When did we last send our own heartbeat to the broker
        self.worker_last_heartbeat = None

        self.has_debug = logger.isEnabledFor(logging.DEBUG)

        # Maps event IDs to methods that handle a given one
        self.handle_event_map = {
            const.v01.request_to_worker: self.on_event_request_to_worker,
            const.v01.heartbeat: self.on_event_heartbeat,
            const.v01.disconnect: self.on_event_disconnect,
        }

# ################################################################################################################################

    def notify_ready(self):
        """ Notify the broker that we are ready to handle a new message.
        """
        self.send(EventReady(self.service_name).serialize())

# ################################################################################################################################

    def connect(self):

        # Open ZeroMQ sockets first

        # From worker to broker
        self.client_socket.connect(self.broker_address)

        # From broker to worker
        self.worker_socket.connect(self.broker_address)

        # Ok, we are ready
        self.notify_ready()

# ################################################################################################################################

    def serve_forever(self):

        # To speed up look-ups
        log_details = self.log_details
        has_debug = self.has_debug

        # Main loop
        while self.keep_running:

            try:
                items = self.worker_poller.poll(self.poll_interval)
            except KeyboardInterrupt:
                break

            if items:
                msg = self.worker_socket.recv_multipart()
                if log_details:
                    logger.info('Received msg at %s %s', self.broker_address, msg)

                self.handle(msg)

            else:
                if log_details:
                    logger.info('No items for worker at %s', self.broker_address)

                # ZzZZzzzZ
                #if time_to_heartbeat:
                #    self.send_heartbeat()

# ################################################################################################################################

    def on_event_request_to_worker(self, msg):
        logger.info('In _handle %s', msg)
        return datetime.utcnow().isoformat()

# ################################################################################################################################

    def on_event_heartbeat(self):
        raise NotImplementedError()

# ################################################################################################################################

    def on_event_disconnect(self):
        raise NotImplementedError()

# ################################################################################################################################

    def handle(self, msg):
        logger.info('Handling %s', msg)

        command = msg[2]
        sender_id = msg[3]
        body = msg[4]

        # Hand over the message to an actual implementation and reply if told to
        response = self.handle_event_map[command](body)

        if response:
            self.send(EventWorkerReply(response, sender_id).serialize())

        # Message handled, we are ready to handle a new one
        self.notify_ready()

# ################################################################################################################################

    def send(self, data):
        self.worker_socket.send_multipart(data)

# ################################################################################################################################

if __name__ == '__main__':
    w = Worker(b'My service', 'tcp://localhost:47047')
    w.connect()
    w.serve_forever()

