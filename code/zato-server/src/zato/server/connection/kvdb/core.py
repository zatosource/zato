# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# orjson
from orjson import dumps as json_dumps

# simdjson
from simdjson import loads as json_loads

# Zato
from zato.common.in_ram import InRAMStore
from zato.common.ext.dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.connection.kvdb.list_ import ListRepo
    from zato.server.connection.kvdb.number import NumberRepo
    from zato.server.connection.kvdb.object_ import ObjectRepo

    NumberRepo = NumberRepo
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

class BaseRepo(InRAMStore):

    sync_state = None

    def __init__(self, name, sync_threshold=120_000, sync_interval=120_000):
        # type: (str, int, int) -> None

        super().__init__(sync_threshold, sync_interval)

        # Our user-visible name
        self.name = name

# ################################################################################################################################

    def _append(self, *args, **kwargs):
        # type: (object, object) -> ObjectCtx
        raise NotImplementedError('BaseRepo._append')

    def _get(self, *args, **kwargs):
        # type: (object, object) -> ObjectCtx
        raise NotImplementedError('BaseRepo._get')

    def _set(self, *args, **kwargs):
        # type: (object, object) -> None
        raise NotImplementedError('BaseRepo._set')

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
        with self.update_lock:
            return self._append(*args, **kwargs)

# ################################################################################################################################

    def get(self, *args, **kwargs):
        with self.update_lock:
            return self._get(*args, **kwargs)

# ################################################################################################################################

    def set(self, *args, **kwargs):
        with self.update_lock:
            return self._set(*args, **kwargs)

# ################################################################################################################################

    def get_list(self, *args, **kwargs):
        with self.update_lock:
            return self._get_list(*args, **kwargs)

# ################################################################################################################################

    def delete(self, *args, **kwargs):
        with self.update_lock:
            return self._delete(*args, **kwargs)

# ################################################################################################################################

    def remove_all(self, *args, **kwargs):
        with self.update_lock:
            return self._remove_all(*args, **kwargs)

# ################################################################################################################################

    def clear(self, *args, **kwargs):
        with self.update_lock:
            return self._clear(*args, **kwargs)

# ################################################################################################################################

    def get_size(self, *args, **kwargs):
        with self.update_lock:
            return self._get_size(*args, **kwargs)

# ################################################################################################################################

    def incr(self, key, *args, **kwargs):
        lock = self.get_lock(key)
        with lock:
            return self._incr(key, *args, **kwargs)

# ################################################################################################################################

    def decr(self, key, *args, **kwargs):
        lock = self.get_lock(key)
        with lock:
            return self._decr(key, *args, **kwargs)

# ################################################################################################################################

    def _loads(self, data):
        # type: (bytes) -> None
        data = json_loads(data) # type: dict
        if data:
            for key, value in data.items():
                self.in_ram_store[key].update(value)

# ################################################################################################################################

    def loads(self, data):
        # type: (bytes) -> int
        with self.update_lock:
            return self._loads(data)

# ################################################################################################################################

    def load_path(self, path):
        # type: (str) -> None
        with self.update_lock:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    data = f.read()
                    if data:
                        self._loads(data)

# ################################################################################################################################

    def _dumps(self):
        # type: () -> bytes
        return json_dumps(self.in_ram_store)

# ################################################################################################################################

    def dumps(self):
        # type: () -> bytes
        with self.update_lock:
            return self._dumps()

# ################################################################################################################################

    def save_path(self, path):
        # type: () -> bytes
        with self.update_lock:
            with open(path, 'wb') as f:
                data = self._dumps()
                f.write(data)

# ################################################################################################################################
# ################################################################################################################################

class KVDB:
    """ Manages KVDB repositories.
    """
    def __init__(self):
        self.repo = {} # Maps str -> repository objects

# ################################################################################################################################

    def internal_create_list_repo(self, repo_name, max_size=1000, page_size=50):
        # type: (str) -> ListRepo

        # Zato
        from zato.server.connection.kvdb.list_ import ListRepo

        repo = ListRepo(repo_name, max_size, page_size)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def internal_create_number_repo(self, repo_name, max_size=1000, page_size=50):
        # type: (str) -> NumberRepo

        # Zato
        from zato.server.connection.kvdb.number import NumberRepo

        repo = NumberRepo(repo_name, max_size, page_size)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def internal_create_object_repo(self, repo_name):
        # type: (str) -> ObjectRepo

        # Zato
        from zato.server.connection.kvdb.object_ import ObjectRepo

        repo = ObjectRepo(repo_name)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def get(self, repo_name):
        # type: (str) -> ListRepo
        return self.repo.get(repo_name)

# ################################################################################################################################

    def append(self, repo_name, ctx):
        # type: (str, ObjectCtx) -> None
        repo = self.repo[repo_name] # type: ListRepo
        repo.append(ctx)

# ################################################################################################################################

    def get_object(self, repo_name, object_id):
        # type: (str, str) -> ObjectCtx
        repo = self.repo[repo_name] # type: ListRepo
        return repo.get(object_id)

# ################################################################################################################################

    def get_list(self, repo_name, cur_page=1, page_size=50):
        # type: (str, int, int) -> None
        repo = self.repo[repo_name] # type: ListRepo
        return repo.get_list(cur_page, page_size)

# ################################################################################################################################

    def delete(self, repo_name, object_id):
        # type: (str) -> None
        repo = self.repo[repo_name] # type: ListRepo
        return repo.delete(object_id)

# ################################################################################################################################

    def remove_all(self, repo_name):
        # type: (str) -> None
        repo = self.repo[repo_name] # type: ListRepo
        repo.remove_all()

# ################################################################################################################################

    def get_size(self, repo_name):
        # type: (str) -> int
        repo = self.repo[repo_name] # type: ListRepo
        return repo.get_size()

# ################################################################################################################################
# ################################################################################################################################
