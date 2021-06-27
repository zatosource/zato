# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.util.search import SearchResults
from zato.server.connection.kvdb.core import BaseRepo, ObjectCtx

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ListRepo(BaseRepo):
    """ Stores arbitrary objects, as a list, in RAM only, without backing persistent storage.
    """
    def __init__(self, name='<ListRepo-name>', data_path='<ListRepo-data_path>', max_size=1000, page_size=50):
        # type: (str, int, int) -> None
        super().__init__(name, data_path)

        # How many objects we will keep at most
        self.max_size = max_size

        # How many objects to return at most in list responses
        self.page_size = page_size

        # In-RAM database of objects
        self.in_ram_store = [] # type: list[ObjectCtx]

        # Used to synchronise updates
        self.lock = RLock()

# ################################################################################################################################

    def _append(self, ctx):
        # type: (ObjectCtx) -> ObjectCtx
        # Push new data ..
        self.in_ram_store.append(ctx)

        # .. and ensure our max_size is not exceeded ..
        if len(self.in_ram_store) > self.max_size:

            # .. we maintain a FIFO list, deleting the oldest entriest first.
            del self.in_ram_store[self.max_size:]

        return ctx

# ################################################################################################################################

    def _get(self, object_id):
        # type: (str) -> object
        for item in self.in_ram_store: # type: ObjectCtx
            if item.id == object_id:
                return item
        else:
            raise KeyError('Object not found `{}`'.format(object_id))

# ################################################################################################################################

    def _get_list(self, cur_page=1, page_size=50):
        # type: (int, int) -> dict
        search_results = SearchResults.from_list(self.in_ram_store, cur_page, page_size)
        return search_results.to_dict()

# ################################################################################################################################

    def _delete(self, object_id):
        # type: (str) -> object
        for item in self.in_ram_store: # type: ObjectCtx
            if item.id == object_id:
                self.in_ram_store.remove(item)
                return item

# ################################################################################################################################

    def _remove_all(self):
        # type: () -> None
        self.in_ram_store[:] = []

# ################################################################################################################################

    def _get_size(self):
        # type: () -> int
        return len(self.in_ram_store)

# ################################################################################################################################
# ################################################################################################################################
