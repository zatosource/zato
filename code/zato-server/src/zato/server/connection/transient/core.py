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

    def internal_create_repo(self, repo_name, max_size=1000, page_size=50):
        # type: (str) -> TransientRepository
        repo = TransientRepository(repo_name, max_size, page_size)
        self.repo[repo_name] = repo
        return repo

# ################################################################################################################################

    def get(self, repo_name):
        # type: (str) -> TransientRepository
        return self.repo.get(repo_name)

# ################################################################################################################################

    def push(self, repo_name, ctx):
        # type: (str, ObjectCtx) -> None
        repo = self.repo[repo_name] # type: TransientRepository
        repo.push(ctx)

# ################################################################################################################################

    def get_object(self, repo_name, object_id):
        # type: (str, str) -> ObjectCtx
        repo = self.repo[repo_name] # type: TransientRepository
        return repo.get(object_id)

# ################################################################################################################################

    def get_list(self, repo_name, cur_page=1, page_size=50):
        # type: (str, int, int) -> None
        repo = self.repo[repo_name] # type: TransientRepository
        return repo.get_list(cur_page, page_size)

# ################################################################################################################################

    def delete(self, repo_name, object_id):
        # type: (str) -> None
        repo = self.repo[repo_name] # type: TransientRepository
        return repo.delete(object_id)

# ################################################################################################################################

    def clear(self, repo_name):
        # type: (str) -> None
        repo = self.repo[repo_name] # type: TransientRepository
        repo.clear()

# ################################################################################################################################

    def get_size(self, repo_name):
        # type: (str) -> int
        repo = self.repo[repo_name] # type: TransientRepository
        return repo.get_size()

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
        # type: (ObjectCtx) -> None
        with self.lock:

            # Push new data ..
            self.in_ram_store.append(ctx)

            # .. and ensure our max_size is not exceeded ..
            if len(self.in_ram_store) > self.max_size:

                # .. we maintain a FIFO list, deleting the oldest entriest first.
                del self.in_ram_store[self.max_size:]

# ################################################################################################################################

    def get(self, object_id):
        # type: (str) -> object
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
                    return item

# ################################################################################################################################

    def clear(self):
        # type: () -> None
        with self.lock:
            self.in_ram_store[:] = []

# ################################################################################################################################

    def get_size(self):
        with self.lock:
            return len(self.in_ram_store)

# ################################################################################################################################
# ################################################################################################################################
