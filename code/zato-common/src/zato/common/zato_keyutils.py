# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from logging import getLogger

# Zato
from zato.common.util.posix_ipc import SharedMemoryIPC

# keyutils
try:
    import keyutils as _keyutils
except ImportError:
    # Only available on linux2.
    pass


# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class LinuxKeyUtils(object):
    """ A higher-level wrapper around Linux kernel's keyutils facilities, i.e. keyctl(2) and related syscalls.
    """

# ################################################################################################################################

    def __init__(self, default_key=None, default_pid=None):
        self.default_key = default_key
        self.default_pid = default_pid

# ################################################################################################################################

    def _format_proc_key(self, key, pid):
        """ Prepends a process PID to key, if such a PID is given on input.
        This lets parent processes store data with their PIDs as prefix which in turn lets child processes
        access only these keys they have interest in, i.e. only those that were created by their parents.
        """
        prefix = '{}-'.format(pid) if pid else ''
        return '{}{}'.format(prefix, key)

# ################################################################################################################################

    def _get_user_key_id(self, key=None, pid=None):
        """ Returns ID under which a given key name is known.
        """
        key = key or self.default_key
        pid = pid or self.default_pid

        formatted = self._format_proc_key(key, pid)
        key_id = _keyutils.request_key(formatted, _keyutils.KEY_SPEC_USER_KEYRING)

        if not key_id:
            raise ValueError('No such key `{}` in proc keyring'.format(formatted))

        return key_id

# ################################################################################################################################

    def user_set(self, key, value, pid=None):
        """ Sets key to value in current user's keyring.
        """
        return _keyutils.add_key(self._format_proc_key(key, pid), value, _keyutils.KEY_SPEC_USER_KEYRING)

# ################################################################################################################################

    def user_get(self, key=None, pid=None):
        """ Returns value of key from current user's keyring.
        """
        return _keyutils.read_key(self._get_user_key_id(key, pid))

# ################################################################################################################################

    def user_delete(self, key, pid=None):
        """ Deletes key from current user's keyring.
        """
        return _keyutils.unlink(self._get_user_key_id(key, pid), _keyutils.KEY_SPEC_USER_KEYRING)
# ################################################################################################################################

class IpcKeyUtils(LinuxKeyUtils):
    """ An IPC-based stand-in for the Linux keyring API, for OSes that don't support it.
    """
    KEYRING_SIZE = 65536

# ################################################################################################################################

    def __init__(self, default_key=None, default_pid=None):
        super(IpcKeyUtils, self).__init__(default_key, default_pid)
        self.uid_shmem = SharedMemoryIPC()
        self.uid_shmem.create('uid-keyring', self.KEYRING_SIZE)

# ################################################################################################################################

    def _get_user_key_id(self, key=None, pid=None):
        """ Returns ID under which a given key name is known.
        """
        key = key or self.default_key
        pid = pid or self.default_pid
        return self._format_proc_key(key, pid)

# ################################################################################################################################

    def user_set(self, key, value, pid=None):
        """ Sets key to value in current user's keyring.
        """
        keyring = self.uid_shmem.load()
        keyring[self._format_proc_key(key, pid)] = value
        self.uid_shmem.store(keyring)

# ################################################################################################################################

    def user_get(self, key=None, pid=None):
        """ Returns value of key from current user's keyring.
        """
        keyring = self.uid_shmem.load()
        return keyring[self._get_user_key_id(key)]

# ################################################################################################################################

    def user_delete(self, key, pid=None):
        """ Deletes key from current user's keyring.
        """
        keyring = self.uid_shmem.load()
        keyring.pop(self._get_user_key_id(key), None)
        self.uid_shmem.store(keyring)

# ################################################################################################################################

def KeyUtils(*args, **kwargs):
    """Factory function that returns an implementation appropriate for the active platform.
    """
    if sys.platform == 'linux2':
        klass = LinuxKeyUtils
    else:
        klass = IpcKeyUtils

    return klass(*args, **kwargs)

# ################################################################################################################################
