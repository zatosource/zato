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

# Zato
from zato.zmq_.mdp import BaseZMQConnection, EventClientRequest

# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################

class Reply:
    __slots__ = ('service_name', 'body')

    def __init__(self, service_name, body):
        self.service_name = service_name
        self.body = body

# ################################################################################################################################

class Client(BaseZMQConnection):
    """ Standalone implementation of a client for ZeroMQ Majordomo Protocol 0.1 http://rfc.zeromq.org/spec:7
    """
    def send(self, service, body=b'', needs_reply=True, timeout=0.2):
        self.client_socket.send_multipart(EventClientRequest(body, service).serialize())

        if needs_reply:
            now = datetime.utcnow()
            until = now + timedelta(seconds=timeout)

            # Main loop
            while datetime.utcnow() <= until:

                try:
                    items = self.client_poller.poll(self.poll_interval)
                except KeyboardInterrupt:
                    break

                if items:
                    msg = self.client_socket.recv_multipart()

                    # Idx 0 is empty
                    # Idx 1 is const.v01.client
                    # Idx 2 is service name
                    # Idx 3 is body of the reply

                    return Reply(msg[2], msg[3])

            # If we are here it means that a response was expected yet it never arrived
            raise Exception('No response received')

    def connect(self):
        self.client_socket.connect(self.broker_address)

# ################################################################################################################################

if __name__ == '__main__':
    c = Client(log_details=True)
    c.connect()
    for x in range(6):
        try:
            reply = c.send(b'zato.ping', b'{"id":"123", "data":"mydata"}', True)
            print(x, 'Reply', repr(reply.body))
        except Exception as e:
            print(e)
