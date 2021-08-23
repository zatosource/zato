# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from logging import getLogger
from mmap import mmap
from time import sleep
from traceback import format_exc

# posix-ipc
import posix_ipc as ipc

# Zato
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_shmem_pattern = '/zato-shmem-{}'

# ################################################################################################################################
# ################################################################################################################################

class SharedMemoryIPC(object):
    """ An IPC object which Zato processes use to communicate with each other using mmap files
    backed by shared memory. All data in shared memory is kept as a dictionary and serialized as JSON
    each time any read or write is needed.
    """
    key_name = '<invalid>'

    def __init__(self):
        self.shmem_name = ''
        self.size = -1
        self._mmap = None
        self.running = False

# ################################################################################################################################

    def create(self, shmem_suffix, size, needs_create):
        """ Creates all IPC structures.
        """
        self.shmem_name = _shmem_pattern.format(shmem_suffix)
        self.size = size

        # Create or read share memory
        logger.debug('%s shmem `%s` (%s %s)', 'Creating' if needs_create else 'Opening', self.shmem_name,
            self.size, self.key_name)

        try:
            self._mem = ipc.SharedMemory(self.shmem_name, ipc.O_CREAT if needs_create else 0, size=self.size)
        except ipc.ExistentialError:
            raise ValueError('Could not create shmem `{}` ({}), e:`{}`'.format(self.shmem_name, self.key_name, format_exc()))

        # Map memory to mmap
        self._mmap = mmap(self._mem.fd, self.size)

        # Write initial data so that JSON .loads always succeeds
        self.store_initial()

        self.running = True

# ################################################################################################################################

    def store(self, data):
        """ Serializes input data as JSON and stores it in RAM, overwriting any previous data.
        """
        self._mmap.seek(0)
        self._mmap.write(dumps(data).encode('utf8'))
        self._mmap.flush()

# ################################################################################################################################

    def store_initial(self):
        """ Stores initial data in shmem unless there is already data in there.
        """
        if self.load(False):
            return
        else:
            self.store({})

# ################################################################################################################################

    def load(self, needs_loads=True):
        """ Reads in all data from RAM and, optionally, loads it as JSON.
        """
        self._mmap.seek(0)
        data = self._mmap.read(self.size).strip(b'\x00')
        return loads(data.decode('utf8')) if needs_loads else data

# ################################################################################################################################

    def close(self):
        """ Closes all underlying in-RAM structures.
        """
        if not self.running:
            logger.debug('Skipped close, IPC not running (%s)', self.key_name)
            return
        else:
            logger.info('Closing IPC (%s)', self.key_name)

        self._mmap.close()
        try:
            self._mem.unlink()
        except ipc.ExistentialError:
            pass

# ################################################################################################################################

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

# ################################################################################################################################

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

    def _get_key(self, parent, key):
        """ Low-level implementation of get_key which does not handle timeouts.
        """
        parent = self.get_parent(parent, False)
        return parent[key]

# ################################################################################################################################

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
# ################################################################################################################################

class ServerStartupIPC(SharedMemoryIPC):
    """ A shared memory-backed IPC object for server startup initialization.
    """
    key_name = '/pubsub/pid'

    def create(self, deployment_key, size, needs_create=True):
        super(ServerStartupIPC, self).create('server-{}'.format(deployment_key), size, needs_create)

    def set_pubsub_pid(self, pid):
        self.set_key(self.key_name, 'current', pid)

    def get_pubsub_pid(self, timeout=60):
        return self.get_key(self.key_name, 'current', timeout)

# ################################################################################################################################
# ################################################################################################################################

class ConnectorConfigIPC(SharedMemoryIPC):
    """ A shared memory-backed IPC object for configuration of subprocess-based containers.
    """
    needs_create = False

    key_name = '/connector/config'

    def create(self, deployment_key, size, needs_create=True):
        super(ConnectorConfigIPC, self).create('connector-config-{}'.format(deployment_key), size, needs_create)

    def set_config(self, connector_key, config):
        self.set_key(self.key_name, connector_key, config)

    def get_config(self, connector_key, timeout=60, as_dict=False):
        response = self.get_key(self.key_name, connector_key, timeout)
        if response:
            return loads(response) if as_dict else response

# ################################################################################################################################
# ################################################################################################################################

class CommandStoreIPC(SharedMemoryIPC):
    """ A shared memory-backed IPC object for CLI commands used by Zato.
    """
    needs_create = False

    key_name = '/cli/command/store'

    def create(self, size=100_000, needs_create=True):
        super(CommandStoreIPC, self).create('cli-command-store', size, needs_create)

    def add_parser(self, parser_data):
        self.set_key(self.key_name, 'parser', parser_data)

    def get_config(self, timeout=3):
        return self.get_key(self.key_name, 'parser', timeout)

# ################################################################################################################################
# ################################################################################################################################
