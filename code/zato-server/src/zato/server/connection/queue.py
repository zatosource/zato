# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta

# gevent
import gevent
from gevent.lock import RLock
from gevent.queue import Empty, Queue

# A set of utilities for constructing greenlets-safe outgoing connection objects.
# Used, for instance, in SOAP Suds and OpenStack Swift outconns.

logger = logging.getLogger(__name__)

# ################################################################################################################################

class _Connection(object):
    """ Meant to be used as a part of a 'with' block - returns a connection from its queue each time 'with' is entered
    assuming the queue isn't empty.
    """
    def __init__(self, client_queue, conn_name):
        self.queue = client_queue
        self.conn_name = conn_name
        self.client = None

    def __enter__(self):
        try:
            self.client = self.queue.get(block=False)
        except Empty:
            self.client = None
            msg = 'No free connections to `{}`'.format(self.conn_name)
            logger.error(msg)
            raise Exception(msg)
        else:
            return self.client

    def __exit__(self, type, value, traceback):
        if self.client:
            self.queue.put(self.client)

# ################################################################################################################################

class ConnectionQueue(object):
    """ Holds connections to resources. Each time it's called a connection is fetched from its underlying queue
    assuming any connection is still available.
    """
    def __init__(self, pool_size, queue_build_cap, conn_name, conn_type, address, add_client_func):
        self.queue = Queue(pool_size)
        self.queue_build_cap = queue_build_cap
        self.conn_name = conn_name
        self.conn_type = conn_type
        self.address = address
        self.add_client_func = add_client_func
        self.keep_connecting = True

        self.logger = logging.getLogger(self.__class__.__name__)

    def __call__(self):
        return _Connection(self.queue, self.conn_name)

    def put_client(self, client):
        self.queue.put(client)
        self.logger.info('Added `%s` client to %s (%s)', self.conn_name, self.address, self.conn_type)

    def _build_queue(self):

        start = datetime.utcnow()
        build_until = start + timedelta(seconds=self.queue_build_cap)

        try:
            while self.keep_connecting:
                while not self.queue.full():

                    gevent.sleep(0.5)

                    now = datetime.utcnow()

                    self.logger.info('%d/%d %s clients obtained to `%s` (%s) after %s (cap: %ss)',
                        self.queue.qsize(), self.queue.maxsize, self.conn_type, self.address, self.conn_name, now - start,
                        self.queue_build_cap)

                    if  now >= build_until:

                        self.logger.warn('Built %s/%s %s clients to `%s` within %s seconds, sleeping until %s',
                            self.queue.qsize(), self.queue.maxsize, self.conn_type, self.address, self.queue_build_cap, build_until)
                        gevent.sleep(self.queue_build_cap)

                        start = datetime.utcnow()
                        build_until = start + timedelta(seconds=self.queue_build_cap)

                self.logger.info(
                    'Obtained %d %s clients to `%s` for `%s`', self.queue.maxsize, self.conn_type, self.address, self.conn_name)

                # Ok, got all the connections
                return
        except KeyboardInterrupt:
            self.keep_connecting = False

    def build_queue(self):
        """ Spawns greenlets to populate the queue and waits up to self.queue_build_cap seconds until the queue is full.
        If it never is, raises an exception stating so.
        """
        for x in range(self.queue.maxsize):
            gevent.spawn(self.add_client_func)

        # Build the queue in background
        gevent.spawn(self._build_queue)

# ################################################################################################################################

class Wrapper(object):
    """ Base class for connections wrappers.
    """
    def __init__(self, config, conn_type, server=None):
        self.conn_type = conn_type
        self.config = config
        self.config.username_pretty = self.config.username or '(None)'
        self.server = server

        self.client = ConnectionQueue(
            self.config.pool_size, self.config.queue_build_cap, self.config.name, self.conn_type, self.config.auth_url,
            self.add_client)

        self.update_lock = RLock()
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_queue(self):
        with self.update_lock:
            if self.config.is_active:
                self.client.build_queue()
            else:
                logger.info('Skip building inactive connection queue for `%s` (%s)', self.client.conn_name, self.client.conn_type)
