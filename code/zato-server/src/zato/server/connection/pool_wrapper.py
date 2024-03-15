# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.distlock import PassThrough as PassThroughLock

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, callable_
    from zato.distlock import Lock
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class ConnectionPoolWrapper:
    """ Holds information about all the connection pools of a given type currently running or being built.
    """
    type_:'str'
    items:'anylist'
    server:'ParallelServer'

    def __init__(
        self,
        server:'ParallelServer',
        type_:'str',
    ) -> 'None':
        self.server = server
        self.type_ = type_
        self.items = []

# ################################################################################################################################

    def _lock(self, config_id:'any_') -> 'Lock':

        # A lock to use when we want to ensure that only one connection pool will be built at a time
        # for a given connection definition. Note that we are using its ID
        # instead of name to let the connection be renamed at any time.
        lock_name = f'ConnectionPoolWrapper.{self.type_}.{config_id}'

        # Acquire a lock that will be held across all the connection pools ..
        return self.server.zato_lock_manager(lock_name, block=1200)

# ################################################################################################################################

    def get_update_lock(self, *, is_zato:'bool') -> 'callable_':

        if is_zato:
            return self._lock
        else:
            return PassThroughLock

# ################################################################################################################################

    def get_func_call_lock(self, *, is_zato:'bool') -> 'callable_':

        if is_zato:
            return PassThroughLock
        else:
            return self._lock

# ################################################################################################################################

    def add_item(self, *, config_id:'any_', is_zato:'bool', item:'any_') -> 'None':

        _lock = self.get_func_call_lock(is_zato=is_zato)
        with _lock(config_id):
            self.items.append(item)

# ################################################################################################################################

    def delete_all(self, *, config_id:'any_', is_zato:'bool') -> 'None':

        _lock = self.get_func_call_lock(is_zato=is_zato)
        with _lock(config_id):

            # First, stop all the items ..
            for item in self.items:
                item.delete()

            # .. now, clear the list.
            self.items.clear()

# ################################################################################################################################

    def has_item(self, *, is_zato:'bool', config_id:'any_', item:'any_') -> 'bool':

        _lock = self.get_func_call_lock(is_zato=is_zato)
        with _lock(config_id):
            return item in self.items

# ################################################################################################################################

    def delete_item(self, *, config_id:'any_', is_zato:'bool', item_to_delete:'any_') -> 'None':

        _lock = self.get_func_call_lock(is_zato=is_zato)
        with _lock(config_id):
            for item in self.items:
                if item is item_to_delete:
                    item.delete()

# ################################################################################################################################
# ################################################################################################################################
