# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# keyutils
import keyutils as _keyutils

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class KeyUtils(object):
    """ A higher-level wrapper around Linux kernel's keyutils facilities, i.e. keyctl(2) and related syscalls.
    """
    _user_keyring = _keyutils.KEY_SPEC_USER_KEYRING

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
        key_id = _keyutils.request_key(formatted, self._user_keyring)

        if not key_id:
            raise ValueError('No such key `{}` in proc keyring'.format(formatted))

        return key_id

# ################################################################################################################################

    def user_set(self, key, value, pid=None):
        """ Sets key to value in current user's keyring.
        """
        return _keyutils.add_key(self._format_proc_key(key, pid), value, self._user_keyring)

# ################################################################################################################################

    def user_get(self, key=None, pid=None):
        """ Returns value of key from current user's keyring.
        """
        return _keyutils.read_key(self._get_user_key_id(key, pid))

# ################################################################################################################################

    def user_delete(self, key, pid=None):
        """ Deletes key from current user's keyring.
        """
        return _keyutils.unlink(self._get_user_key_id(key, pid), self._user_keyring)

# ################################################################################################################################
