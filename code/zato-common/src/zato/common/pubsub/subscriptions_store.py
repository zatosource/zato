# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.util.api import new_sub_key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SubscriptionsStore:
    """ In-memory store for subscription mappings.
    """

    def __init__(self) -> 'None':
        self._lock = RLock()

        # username -> sub_key
        self._username_to_sub_key:'strdict' = {}

        # sub_key -> username
        self._sub_key_to_username:'strdict' = {}

        # username -> sec_name
        self._username_to_sec_name:'strdict' = {}

        # sec_name -> username
        self._sec_name_to_username:'strdict' = {}

# ################################################################################################################################

    def register_user(self, username:'str', sec_name:'str', sub_key:'strnone'=None) -> 'str':
        """ Register a user with their security definition name and optionally a sub_key.
        """
        with self._lock:
            # Store username <-> sec_name mapping
            self._username_to_sec_name[username] = sec_name
            self._sec_name_to_username[sec_name] = username

            # If sub_key provided, store it
            if sub_key:
                self._username_to_sub_key[username] = sub_key
                self._sub_key_to_username[sub_key] = username

            return sub_key or ''

# ################################################################################################################################

    def get_sub_key_by_username(self, username:'str') -> 'strnone':
        """ Get subscription key for a username.
        """
        with self._lock:
            return self._username_to_sub_key.get(username)

# ################################################################################################################################

    def get_username_by_sub_key(self, sub_key:'str') -> 'strnone':
        """ Get username for a subscription key.
        """
        with self._lock:
            return self._sub_key_to_username.get(sub_key)

# ################################################################################################################################

    def get_sec_name_by_username(self, username:'str') -> 'strnone':
        """ Get security definition name for a username.
        """
        with self._lock:
            return self._username_to_sec_name.get(username)

# ################################################################################################################################

    def get_username_by_sec_name(self, sec_name:'str') -> 'strnone':
        """ Get username for a security definition name.
        """
        with self._lock:
            return self._sec_name_to_username.get(sec_name)

# ################################################################################################################################

    def get_or_create_sub_key(self, username:'str') -> 'str':
        """ Get existing sub_key for username or create a new one.
        """
        with self._lock:

            # Check if user already has a sub_key
            sub_key = self._username_to_sub_key.get(username)

            if sub_key:
                return sub_key

            # Get sec_name for this user
            sec_name = self._username_to_sec_name.get(username)

            if not sec_name:
                raise ValueError(f'No security definition found for username: {username}')

            # Create new sub_key
            sub_key = new_sub_key(sec_name)

            # Store mappings
            self._username_to_sub_key[username] = sub_key
            self._sub_key_to_username[sub_key] = username

            return sub_key

# ################################################################################################################################

    def clear_sub_key(self, username:'str') -> 'None':
        """ Clear sub_key for a user so a new one is generated on next subscribe.
        """
        with self._lock:
            sub_key = self._username_to_sub_key.pop(username, None)
            if sub_key:
                _ = self._sub_key_to_username.pop(sub_key, None)

# ################################################################################################################################

    def remove_user(self, username:'str') -> 'None':
        """ Remove a user and all their mappings.
        """
        with self._lock:

            # Get sub_key if exists
            sub_key = self._username_to_sub_key.pop(username, None)

            if sub_key:
                _ = self._sub_key_to_username.pop(sub_key, None)

            # Get sec_name if exists
            sec_name = self._username_to_sec_name.pop(username, None)

            if sec_name:
                _ = self._sec_name_to_username.pop(sec_name, None)

# ################################################################################################################################

    def update_username(self, old_username:'str', new_username:'str') -> 'None':
        """ Update username in all mappings.
        """
        with self._lock:

            # Update sub_key mapping
            sub_key = self._username_to_sub_key.pop(old_username, None)
            if sub_key:
                self._username_to_sub_key[new_username] = sub_key
                self._sub_key_to_username[sub_key] = new_username

            # Update sec_name mapping
            sec_name = self._username_to_sec_name.pop(old_username, None)
            if sec_name:
                self._username_to_sec_name[new_username] = sec_name
                self._sec_name_to_username[sec_name] = new_username

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Clear all mappings.
        """
        with self._lock:
            self._username_to_sub_key.clear()
            self._sub_key_to_username.clear()
            self._username_to_sec_name.clear()
            self._sec_name_to_username.clear()

# ################################################################################################################################
# ################################################################################################################################
