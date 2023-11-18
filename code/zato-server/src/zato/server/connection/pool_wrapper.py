# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
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
        return self.server.zato_lock_manager(lock_name)

    def add_item(self, config_id:'any_', item:'any_') -> 'None':

        with self._lock(config_id):
            self.items.append(item)

# ################################################################################################################################

    def delete_all(self, config_id:'any_') -> 'None':

        with self._lock(config_id):

            # First, stop all the items ..
            for item in self.items:
                item.delete()

            # .. now, clear the list.
            self.items.clear()

# ################################################################################################################################

    def has_item(self, item:'any_') -> 'bool':

        with self._lock(item):
            return item in self.items

# ################################################################################################################################

    def delete_item(self, config_id:'any_', item_to_delete:'any_') -> 'None':

        with self._lock(config_id):
            for item in self.items:
                if item is item_to_delete:
                    item.delete()

# ################################################################################################################################
# ################################################################################################################################
