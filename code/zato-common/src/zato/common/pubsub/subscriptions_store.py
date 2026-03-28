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
        logger.info('register_user: username=%s, sec_name=%s, sub_key=%s', username, sec_name, sub_key)

        with self._lock:

            # Store username <-> sec_name mapping
            self._username_to_sec_name[username] = sec_name
            self._sec_name_to_username[sec_name] = username

            logger.info('register_user: stored username_to_sec_name[%s]=%s', username, sec_name)
            logger.info('register_user: stored sec_name_to_username[%s]=%s', sec_name, username)

            # If sub_key provided, store it
            if sub_key:
                self._username_to_sub_key[username] = sub_key
                self._sub_key_to_username[sub_key] = username
                logger.info('register_user: stored username_to_sub_key[%s]=%s', username, sub_key)

            logger.info('register_user: current state - username_to_sec_name=%s', dict(self._username_to_sec_name))

            return sub_key or ''

# ################################################################################################################################

    def get_sub_key_by_username(self, username:'str') -> 'strnone':
        """ Get subscription key for a username.
        """
        with self._lock:
            result = self._username_to_sub_key.get(username)
            logger.info('get_sub_key_by_username: username=%s, result=%s', username, result)
            return result

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
            result = self._username_to_sec_name.get(username)
            logger.info('get_sec_name_by_username: username=%s, result=%s, all_mappings=%s',
                username, result, dict(self._username_to_sec_name))
            return result

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
        logger.info('get_or_create_sub_key: username=%s', username)

        with self._lock:

            # Check if user already has a sub_key
            sub_key = self._username_to_sub_key.get(username)
            logger.info('get_or_create_sub_key: existing sub_key=%s', sub_key)

            if sub_key:
                return sub_key

            # Get sec_name for this user
            sec_name = self._username_to_sec_name.get(username)
            logger.info('get_or_create_sub_key: sec_name=%s, all_sec_names=%s', sec_name, dict(self._username_to_sec_name))

            if not sec_name:
                logger.info('get_or_create_sub_key: no sec_name found for username=%s', username)
                raise ValueError(f'No security definition found for username: {username}')

            # Create new sub_key
            sub_key = new_sub_key(sec_name)
            logger.info('get_or_create_sub_key: created new sub_key=%s', sub_key)

            # Store mappings
            self._username_to_sub_key[username] = sub_key
            self._sub_key_to_username[sub_key] = username

            logger.info('Created new sub_key %s for user %s', sub_key, username)

            return sub_key

# ################################################################################################################################

    def clear_sub_key(self, username:'str') -> 'None':
        """ Clear sub_key for a user so a new one is generated on next subscribe.
        """
        with self._lock:
            sub_key = self._username_to_sub_key.pop(username, None)
            if sub_key:
                _ = self._sub_key_to_username.pop(sub_key, None)
                logger.info('Cleared sub_key for user %s', username)

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

            logger.info('Removed user %s from subscriptions store', username)

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

            logger.info('Updated username from %s to %s in subscriptions store', old_username, new_username)

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
