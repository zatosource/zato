# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
import sys

# gevent
from gevent.lock import RLock

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.util.search import SearchResults
from zato.server.connection.transient.core import BaseRepo, ObjectCtx, TransientAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class TransientCounterRepo(BaseRepo):
    """ Stores integer counters for string labels.
    """
    def __init__(self, name='<CounterRepo-name>', max_value=sys.maxsize, allow_negative=True):
        # type: (str, int, int) -> None
        super().__init__(name)

        # We will never allow for a value to be greater than that
        self.max_value = max_value

        # If False, value will never be less than zero
        self.allow_negative = allow_negative

        # In-RAM database of objects
        self.in_ram_store = {} # type: dict[str, int]

# ################################################################################################################################

    def _incr(self, key, incr_by=1):
        # type: (str, int) -> int

        # Get current value or default to 0, if nothing is found ..
        current_value = self.in_ram_store.get(key, 0)

        # .. get the new value ..
        new_value = current_value + incr_by

        # .. make sure we do not exceeded the maximum value allowed ..
        if new_value > self.max_value:
            new_value = self.max_value

        # .. finally, store the new value in RAM.
        self.in_ram_store[key] = new_value

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
        self.in_ram_store.clear()

# ################################################################################################################################

    def _clear(self):
        # type: () -> None
        for key in self.in_ram_store: # type: str
            self.in_ram_store[key] = 0

# ################################################################################################################################
# ################################################################################################################################
