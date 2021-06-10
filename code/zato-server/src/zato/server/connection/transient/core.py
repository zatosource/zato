# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.util.search import SearchResults

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ObjectCtx:

    # A unique identifer assigned to this event by Zato
    id: str

    # A correlation ID assigned by Zato - multiple events may have the same CID
    cid: str = None

    # Timestamp of this event, as assigned by Zato
    timestamp: str = None

    # The actual business data
    data: object = None

# ################################################################################################################################
# ################################################################################################################################

class TransientAPI:
    """ Manages named transient repositories.
    """
    def __init__(self):
        self.repo = {} # str -> TransientRepository objects
        self.lock = RLock()

# ################################################################################################################################

    def get(self, name):
        # type: (str) -> TransientRepository
        pass

# ################################################################################################################################

    def push(self, name):
        pass

# ################################################################################################################################

    def get_object(self, repo_name, object_id):
        # type: (str, str) -> None
        pass

# ################################################################################################################################

    def get_list(self, name):
        # type: (str) -> None
        pass

# ################################################################################################################################

    def delete(self, name, object_id):
        # type: (str) -> None
        pass

# ################################################################################################################################

    def clear(self, name):
        # type: (str) -> None
        pass

# ################################################################################################################################
# ################################################################################################################################

class TransientRepository:
    """ Stores arbitrary objects, as a list, in RAM only, without backing persistent storage.
    """
    def __init__(self, name='<TransientRepository-name>', max_size=1000, page_size=50):
        # type: (str, int, int) -> None

        # Our user-visible name
        self.name = name

        # How many objects we will keep at most
        self.max_size = max_size

        # How many objects to return at most in list responses
        self.page_size = page_size

        # In-RAM database of objects
        self.in_ram_store = [] # type: list[ObjectCtx]

        # Used to synchronise updates
        self.lock = RLock()

# ################################################################################################################################

    def push(self, ctx):
        # type: (ObjectCtx)
        with self.lock:

            # Push new data ..
            self.in_ram_store.append(ctx)

            # .. and ensure our max_size is not exceeded ..
            if len(self.in_ram_store) > self.max_size:

                # .. we maintain a FIFO list, deleting the oldest entriest first.
                del self.in_ram_store[self.max_size:]

# ################################################################################################################################

    def get_size(self):
        with self.lock:
            return len(self.in_ram_store)

# ################################################################################################################################

    def get(self, object_id):
        # type: (str) -> None
        with self.lock:
            for item in self.in_ram_store: # type: ObjectCtx
                if item.id == object_id:
                    return item
            else:
                raise KeyError('Object not found `{}`'.format(object_id))

# ################################################################################################################################

    def get_list(self, cur_page=1, page_size=50):
        # type: (int, int) -> dict
        with self.lock:
            search_results = SearchResults.from_list(self.in_ram_store, cur_page, page_size)
            return search_results.to_dict()

# ################################################################################################################################

    def delete(self, object_id):
        # type: (str) -> None
        with self.lock:
            for item in self.in_ram_store: # type: ObjectCtx
                if item.id == object_id:
                    self.in_ram_store.remove(item)
                    break

# ################################################################################################################################

    def clear(self):
        with self.lock:
            self.in_ram_store[:] = []

# ################################################################################################################################
# ################################################################################################################################
