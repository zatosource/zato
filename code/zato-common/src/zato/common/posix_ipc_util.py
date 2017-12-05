# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
from json import dumps, loads
from logging import getLogger
from mmap import mmap
from time import sleep

# posix-ipc
import posix_ipc as ipc

# Zato
from zato.common import megabyte

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

_shmem_pattern = '/zato-shmem-{}'

# ################################################################################################################################

class SharedMemoryIPC(object):
    """ An IPC object which Zato worker process use to communicate with each other using mmap files
    backed by shared memory. All data in shared memory is kept as a dictionary and serialized as JSON
    each time any read or write is needed.
    """
    def __init__(self):
        self.shmem_name = ''
        self.size = -1

    def create(self, shmem_suffix, size):
        """ Creates all IPC structures.
        """
        self.shmem_name = _shmem_pattern.format(shmem_suffix)
        self.size = size

        # Create share memory
        self._mem = ipc.SharedMemory(self.shmem_name, ipc.O_CREAT, size=self.size)

        # Map memory to mmap
        self._mmap = mmap(self._mem.fd, self.size)

        # Write initial data so that JSON .loads always succeeds
        self.store_initial()

    def store(self, data):
        """ Serializes input data as JSON and stores it in RAM, overwriting any previous data.
        """
        self._mmap.seek(0)
        self._mmap.write(dumps(data))
        self._mmap.flush()

    def store_initial(self):
        """ Stores initial data in shmem unless there is already data in there.
        """
        if self.load(False):
            return
        else:
            self.store({})

    def load(self, needs_loads=True):
        """ Reads in all data from RAM and, optionally, loads it as JSON.
        """
        self._mmap.seek(0)
        data = self._mmap.read(self.size).strip('\x00')
        return loads(data) if needs_loads else data

    def close(self):
        """ Closes all underlying in-RAM structures.
        """
        self._mmap.close()
        try:
            self._mem.unlink()
        except ipc.ExistentialError:
            pass

    def get_parent(self, parent_path, needs_data=True):
        """ Returns element pointed to by parent_path, creating all elements along the way, if neccessary.
        """
        data = self.load()
        parent_path = [elem for elem in parent_path.split('/') if elem]

        # Find or create element that is parent of input key
        current = data
        while parent_path:
            next = parent_path.pop(0)
            current = current.setdefault(next, {})

        return (data, current) if needs_data else current

    def set_key(self, parent, key, value):
        """ Set key to value under element called 'parent'.
        """
        # Get parent to add our key to - will create it if needed
        data, parent = self.get_parent(parent)

        # Set key to value
        parent[key] = value

        # Save it all back
        self.store(data)

    def _get_key(self, parent, key):
        """ Low-level implementation of get_key which does not handle timeouts.
        """
        parent = self.get_parent(parent, False)
        return parent[key]

    def get_key(self, parent, key, timeout=None, _sleep=sleep, _utcnow=datetime.utcnow):
        """ Returns a specific key from parent dictionary.
        """
        try:
            return self._get_key(parent, key)
        except KeyError:
            if timeout:
                now = _utcnow()
                start = now
                until = now + timedelta(seconds=timeout)
                idx = 0

                while now <= until:
                    try:
                        value = self._get_key(parent, key)
                        if value:
                            msg = 'Returning value `%s` for parent/key `%s` `%s` after %s'
                            logger.info(msg, value, parent, key, now - start)
                            return value
                    except KeyError:
                        _sleep(0.1)
                        idx += 1
                        if idx % 10 == 0:
                            logger.info('Waiting for parent/key `%s` `%s` (timeout: %ss)', parent, key, timeout)
                        now = _utcnow()

                # We get here if we did not return the key within timeout seconds,
                # in which case we need to log an error and raise an exception.

                # Same message for logger and exception
                msg = 'Could not get parent/key `{}` `{}` after {}s'.format(parent, key, timeout)
                logger.warn(msg)
                raise KeyError(msg)

            # No exception = re-raise exception immediately
            else:
                raise

# ################################################################################################################################

class ServerStartupIPC(SharedMemoryIPC):
    """ A shared memory-backed IPC object for server startup initialization.
    """
    pubsub_pid = '/pubsub/pid'

    def create(self, deployment_key, size):
        super(ServerStartupIPC, self).create('server-{}'.format(deployment_key), size)

    def set_pubsub_pid(self, pid):
        self.set_key(self.pubsub_pid, 'current', pid)

    def get_pubsub_pid(self, timeout=10):
        return self.get_key(self.pubsub_pid, 'current', timeout)

# ################################################################################################################################
