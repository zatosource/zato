# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps, loads
from mmap import mmap

# posix-ipc
import posix_ipc as ipc

# Zato
from zato.common import megabyte

# ################################################################################################################################

_shmem_pattern = '/zato-shmem-{}'
_shmem_size = megabyte * 100

# ################################################################################################################################

class SharedMemoryIPC(object):
    """ An IPC object which Zato worker process use to communicate with each other using mmap files
    backed by shared memory. All data in shared memory is kept as a dictionary and serialized as JSON
    each time any read or write is needed.
    """
    def __init__(self):
        self.shmem_name = ''
        self.size = -1

    def create(self, shmem_suffix, size=_shmem_size):
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

    def get_parent(self, parent_path):
        """ Returns element pointed to by parent_path, creating all elements along the way, if neccessary.
        """
        data = self.load()
        parent_path = [elem for elem in parent_path.split('/') if elem]

        # Find or create element that is parent of input key
        current = data
        while parent_path:
            next = parent_path.pop(0)
            current = current.setdefault(next, {})

        return data, current

    def set_key(self, parent, key, value):
        """ Set key to value under element called 'parent'.
        """
        # Get parent to add our key to - will create it if needed
        data, parent = self.get_parent(parent)

        # Set key to value
        parent[key] = value

        # Save it all back
        self.store(data)

# ################################################################################################################################

class ServerStartupIPC(SharedMemoryIPC):
    """ A shared memory-backed IPC object for server startup initialization.
    """
    def create(self, deployment_key):
        super(ServerStartupIPC, self).create('startup-{}'.format(deployment_key))

    def set_pubsub_sub_key_pid(self, sub_key, pid):
        self.set_key('/pubsub/sub_key_to_pid', sub_key, pid)

# ################################################################################################################################
