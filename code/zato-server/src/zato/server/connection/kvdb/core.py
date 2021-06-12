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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.connection.kvdb.list_ import ListRepo

    ListRepo = ListRepo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

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

class BaseRepo:

    def __init__(self, name):
        # type: (str) -> None

        # Our user-visible name
        self.name = name

        # Used during modifications to the repository
        self.lock = RLock()

# ################################################################################################################################

    def _append(self, *args, **kwargs):
        # type: (object, object) -> ObjectCtx
        raise NotImplementedError('BaseRepo._append')

    def _get(self, *args, **kwargs):
        # type: (object, object) -> ObjectCtx
        raise NotImplementedError('BaseRepo._get')

    def _get_list(self, *args, **kwargs):
        # type: (object, object) -> list[ObjectCtx]
        raise NotImplementedError('BaseRepo._get_list')

    def _delete(self, *args, **kwargs):
        # type: (object, object) -> list[ObjectCtx]
        raise NotImplementedError('BaseRepo._delete')

    def _remove_all(self, *args, **kwargs):
        # type: (object, object) -> None
        raise NotImplementedError('BaseRepo._remove_all')

    def _clear(self, *args, **kwargs):
        # type: (object, object) -> None
        raise NotImplementedError('BaseRepo._clear')

    def _get_size(self, *args, **kwargs):
        # type: (object, object) -> int
        raise NotImplementedError('BaseRepo._get_size')

    def _incr(self, *args, **kwargs):
        # type: (object, object) -> int
        raise NotImplementedError('BaseRepo._incr')

    def _decr(self, *args, **kwargs):
        # type: (object, object) -> int
        raise NotImplementedError('BaseRepo._decr')

# ################################################################################################################################

    def append(self, *args, **kwargs):
        with self.lock:
            return self._append(*args, **kwargs)

# ################################################################################################################################

    def get(self, *args, **kwargs):
        with self.lock:
            return self._get(*args, **kwargs)

# ################################################################################################################################

    def get_list(self, *args, **kwargs):
        with self.lock:
            return self._get_list(*args, **kwargs)

# ################################################################################################################################

    def delete(self, *args, **kwargs):
        with self.lock:
            return self._delete(*args, **kwargs)

# ################################################################################################################################

    def remove_all(self, *args, **kwargs):
        with self.lock:
            return self._remove_all(*args, **kwargs)

# ################################################################################################################################

    def clear(self, *args, **kwargs):
        with self.lock:
            return self._clear(*args, **kwargs)

# ################################################################################################################################

    def get_size(self, *args, **kwargs):
        with self.lock:
            return self._get_size(*args, **kwargs)

# ################################################################################################################################

    def incr(self, *args, **kwargs):
        with self.lock:
            return self._incr(*args, **kwargs)

# ################################################################################################################################

    def decr(self, *args, **kwargs):
        with self.lock:
            return self._decr(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class KVDB:
    """ Manages KVDB repositories.
    """
    def __init__(self):
        self.repo = {} # Maps str -> repository objects

# ################################################################################################################################

    def internal_create_list_repo(self, repo_name, max_size=1000, page_size=50):
        # type: (str) -> TransientListRepo

        # Zato
        from zato.server.connection.kvdb.list_ import ListRepo

        repo = ListRepo(repo_name, max_size, page_size)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def get(self, repo_name):
        # type: (str) -> TransientListRepo
        return self.repo.get(repo_name)

# ################################################################################################################################

    def append(self, repo_name, ctx):
        # type: (str, ObjectCtx) -> None
        repo = self.repo[repo_name] # type: TransientListRepo
        repo.append(ctx)

# ################################################################################################################################

    def get_object(self, repo_name, object_id):
        # type: (str, str) -> ObjectCtx
        repo = self.repo[repo_name] # type: TransientListRepo
        return repo.get(object_id)

# ################################################################################################################################

    def get_list(self, repo_name, cur_page=1, page_size=50):
        # type: (str, int, int) -> None
        repo = self.repo[repo_name] # type: TransientListRepo
        return repo.get_list(cur_page, page_size)

# ################################################################################################################################

    def delete(self, repo_name, object_id):
        # type: (str) -> None
        repo = self.repo[repo_name] # type: TransientListRepo
        return repo.delete(object_id)

# ################################################################################################################################

    def remove_all(self, repo_name):
        # type: (str) -> None
        repo = self.repo[repo_name] # type: TransientListRepo
        repo.remove_all()

# ################################################################################################################################

    def get_size(self, repo_name):
        # type: (str) -> int
        repo = self.repo[repo_name] # type: TransientListRepo
        return repo.get_size()

# ################################################################################################################################
# ################################################################################################################################
