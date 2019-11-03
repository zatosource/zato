# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta
from time import sleep
from traceback import format_exc

# gevent
import gevent
from gevent.lock import RLock
from gevent.queue import Empty, Queue

# A set of utilities for constructing greenlets-safe outgoing connection objects.
# Used, for instance, in SOAP Suds and OpenStack Swift outconns.

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
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
        self.is_building_conn_queue = False
        self.queue_building_stopped = False
        self.lock = RLock()

        # How many add_client_func instances are running currently,
        # must be updated with self.lock held.
        self.in_progress_count = 0

        self.logger = logging.getLogger(self.__class__.__name__)

    def __call__(self):
        return _Connection(self.queue, self.conn_name)

    def put_client(self, client):
        with self.lock:
            if self.queue.full():
                is_accepted = False
                msg = 'Skipped adding a superfluous `%s` client to %s (%s)'
                log_func = self.logger.info
            else:
                self.queue.put(client)
                is_accepted = True
                msg = 'Added `%s` client to %s (%s)'
                log_func = self.logger.info

            log_func(msg, self.conn_name, self.address, self.conn_type)
            return is_accepted

    def _build_queue(self):

        start = datetime.utcnow()
        build_until = start + timedelta(seconds=self.queue_build_cap)
        suffix = 's ' if self.queue.maxsize > 1 else ' '

        try:
            self.is_building_conn_queue = True
            while self.keep_connecting and not self.queue.full():
                gevent.sleep(5)
                now = datetime.utcnow()

                self.logger.info('%d/%d %s clients obtained to `%s` (%s) after %s (cap: %ss)',
                    self.queue.qsize(), self.queue.maxsize,
                    self.conn_type, self.address, self.conn_name, now - start, self.queue_build_cap)

                if now >= build_until:

                    # Log the fact that the queue is not full yet
                    self.logger.info('Built %s/%s %s clients to `%s` within %s seconds, sleeping until %s (UTC)',
                        self.queue.qsize(), self.queue.maxsize, self.conn_type, self.address, self.queue_build_cap,
                        datetime.utcnow() + timedelta(seconds=self.queue_build_cap))

                    # Sleep for a predetermined time
                    gevent.sleep(self.queue_build_cap)

                    # Spawn additional greenlets to fill up the queue but make sure not to spawn
                    # more greenlets than there are slots in the queue still available.
                    with self.lock:
                        if self.in_progress_count < self.queue.maxsize:
                            self._spawn_add_client_func(self.queue.maxsize - self.in_progress_count)

                    start = datetime.utcnow()
                    build_until = start + timedelta(seconds=self.queue_build_cap)

            if self.keep_connecting:
                self.logger.info('Obtained %d %s client%sto `%s` for `%s`', self.queue.maxsize, self.conn_type, suffix,
                    self.address, self.conn_name)
            else:
                self.logger.info('Skipped building a queue to `%s` for `%s`', self.address, self.conn_name)
                self.queue_building_stopped = True

            # Ok, got all the connections
            self.is_building_conn_queue = False
            return
        except KeyboardInterrupt:
            self.keep_connecting = False
            self.queue_building_stopped = True

    def _spawn_add_client_func_no_lock(self, count):
        for x in range(count):
            gevent.spawn(self.add_client_func)
            self.in_progress_count += 1

    def _spawn_add_client_func(self, count=1):
        """ Spawns as many greenlets to populate the connection queue as there are free slots in the queue available.
        """
        with self.lock:
            if self.queue.full():
                logger.info('Queue already full (c:%d) (%s %s)', count, self.address, self.conn_name)
                return
            self._spawn_add_client_func_no_lock(count)

    def decr_in_progress_count(self):
        with self.lock:
            self.in_progress_count -= 1

    def build_queue(self):
        """ Spawns greenlets to populate the queue and waits up to self.queue_build_cap seconds until the queue is full.
        If it never is, raises an exception stating so.
        """
        self._spawn_add_client_func(self.queue.maxsize)

        # Build the queue in background
        gevent.spawn(self._build_queue)

# ################################################################################################################################
# ################################################################################################################################

class Wrapper(object):
    """ Base class for queue-based connections wrappers.
    """
    def __init__(self, config, conn_type, server=None):
        self.conn_type = conn_type
        self.config = config
        self.config.username_pretty = self.config.username or '(None)'
        self.server = server

        self.client = ConnectionQueue(
            self.config.pool_size, self.config.queue_build_cap, self.config.name, self.conn_type, self.config.auth_url,
            self.add_client)

        self.delete_requested = False
        self.update_lock = RLock()
        self.logger = logging.getLogger(self.__class__.__name__)

# ################################################################################################################################

    def build_queue(self):
        with self.update_lock:
            if self.config.is_active:
                try:
                    self.client.build_queue()
                except Exception:
                    logger.warn('Could not build client queue `%s`', format_exc())
            else:
                logger.info('Skipped building an inactive connection queue for `%s` (%s)',
                    self.client.conn_name, self.client.conn_type)

    # Not all connection types will be queue-based
    build_wrapper = build_queue

# ################################################################################################################################

    def delete_queue_connections(self, reason=None):
        for item in self.client.queue.queue:
            try:
                logger.info('Deleting connection from queue for `%s`', self.config.name)

                # Some connections (e.g. LDAP) want to expose .delete to user API
                # which conflicts with our own needs.
                delete_func = getattr(item, 'zato_delete_impl', None)
                if not delete_func:
                    delete_func = getattr(item, 'delete', None)
                delete_func(reason) if reason else delete_func()
            except Exception:
                logger.warn('Could not delete connection from queue for `%s`, e:`%s`', self.config.name, format_exc())

# ################################################################################################################################

    def delete(self):
        """ Deletes all connections from queue and sets flag that disallow for this client to connect again.
        """
        with self.update_lock:

            # Tell the client that it is to stop connecting and that it will be deleted in a moment
            self.delete_requested = True
            self.client.keep_connecting = False

            # Actuall delete all connections
            self.delete_queue_connections()

            # In case the client was in the process of building a queue of connections,
            # wait until it has stopped doing it.
            if self.client.is_building_conn_queue:
                while not self.client.queue_building_stopped:
                    sleep(1)
                    self.logger.info('Waiting for queue building stopped flag `%s` (%s %s)',
                        self.client.address, self.client.conn_type, self.client.conn_name)

            # Reset flags that will allow this client to reconnect in the future
            self.delete_requested = False
            self.client.keep_connecting = True
            self.client.queue_building_stopped = False
            self.client.is_building_conn_queue = False

# ################################################################################################################################
# ################################################################################################################################
