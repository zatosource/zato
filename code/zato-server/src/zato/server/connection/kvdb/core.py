# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# gevent
from gevent.lock import RLock

# orjson
from orjson import dumps as json_dumps

# Zato
from zato.common.api import ZatoKVDB
from zato.common.in_ram import InRAMStore
from zato.common.ext.dataclasses import dataclass
from zato.common.util.json_ import json_loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strnone
    from zato.server.connection.kvdb.list_ import ListRepo
    from zato.server.connection.kvdb.number import NumberRepo
    from zato.server.connection.kvdb.object_ import ObjectRepo

    ListRepo = ListRepo
    NumberRepo = NumberRepo
    ObjectRepo = ObjectRepo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ObjectCtx:

    # A unique identifer assigned to this event by Zato
    id: 'str'

    # A correlation ID assigned by Zato - multiple events may have the same CID
    cid: 'strnone' = None

    # Timestamp of this event, as assigned by Zato
    timestamp: 'strnone' = None

    # The actual business data
    data: 'any_' = None

# ################################################################################################################################
# ################################################################################################################################

class BaseRepo(InRAMStore):

    def __init__(
        self,
        name,      # type: str
        data_path, # type: str
        sync_threshold=ZatoKVDB.DefaultSyncThreshold, # type: int
        sync_interval=ZatoKVDB.DefaultSyncInterval    # type: int
    ) -> 'None':

        super().__init__(sync_threshold, sync_interval)

        # In-RAM database of objects
        self.in_ram_store = {}

        # Used to synchronise updates
        self.lock = RLock()

        # Our user-visible name
        self.name = name

        # Where we persist data on disk
        self.data_path = data_path

# ################################################################################################################################

    def _append(self, *args:'any_', **kwargs:'any_') -> 'ObjectCtx':
        raise NotImplementedError('BaseRepo._append')

    def _get(self, *args:'any_', **kwargs:'any_') -> 'ObjectCtx':
        raise NotImplementedError('BaseRepo._get')

    def _set(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('BaseRepo._set')

    def _get_list(self, *args:'any_', **kwargs:'any_') -> 'list[ObjectCtx]':
        raise NotImplementedError('BaseRepo._get_list')

    def _delete(self, *args:'any_', **kwargs:'any_') -> 'list[ObjectCtx]':
        raise NotImplementedError('BaseRepo._delete')

    def _remove_all(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('BaseRepo._remove_all')

    def _clear(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise NotImplementedError('BaseRepo._clear')

    def _get_size(self, *args:'any_', **kwargs:'any_') -> 'int':
        raise NotImplementedError('BaseRepo._get_size')

    def _incr(self, *args:'any_', **kwargs:'any_') -> 'int':
        raise NotImplementedError('BaseRepo._incr')

    def _decr(self, *args:'any_', **kwargs:'any_') -> 'int':
        raise NotImplementedError('BaseRepo._decr')

# ################################################################################################################################

    def append(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._append(*args, **kwargs)

# ################################################################################################################################

    def get(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._get(*args, **kwargs)

# ################################################################################################################################

    def set(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._set(*args, **kwargs)

# ################################################################################################################################

    def get_list(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._get_list(*args, **kwargs)

# ################################################################################################################################

    def delete(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._delete(*args, **kwargs)

# ################################################################################################################################

    def remove_all(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._remove_all(*args, **kwargs)

# ################################################################################################################################

    def clear(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._clear(*args, **kwargs)

# ################################################################################################################################

    def get_size(self, *args:'any_', **kwargs:'any_'):
        with self.update_lock:
            return self._get_size(*args, **kwargs)

# ################################################################################################################################

    def incr(self, key, *args:'any_', **kwargs:'any_'):
        lock = self.get_lock(key)
        with lock:
            return self._incr(key, *args, **kwargs)

# ################################################################################################################################

    def decr(self, key, *args:'any_', **kwargs:'any_'):
        lock = self.get_lock(key)
        with lock:
            return self._decr(key, *args, **kwargs)

# ################################################################################################################################

    def _loads(self, data:'bytes') -> 'None':

        try:
            data_ = json_loads(data) # type: dict
        except Exception as e:
            logger.info('KVDB load error (%s -> %s) -> %s', self.name, self.data_path, e)
        else:
            if data_:

                # We may have already some pre-defined keys in RAM that we only need to update ..
                if self.in_ram_store:
                    for key, value in data_.items():
                        self.in_ram_store[key].update(value)

                # .. otherwise, we load all the data as is because we assume know there are no keys in RAM yet.
                self.in_ram_store.update(data_)

# ################################################################################################################################

    def loads(self, data:'bytes') -> 'None':
        with self.update_lock:
            return self._loads(data)

# ################################################################################################################################

    def load_data(self) -> 'None':
        with self.update_lock:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'rb') as f:
                    data = f.read()
                    if data:
                        self._loads(data)
            else:
                logger.info('Skipping repo data path `%s` (%s)', self.data_path, self.name)

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

    def save_data(self) -> 'None':
        with self.update_lock:
            with open(self.data_path, 'wb') as f:
                data = self._dumps()
                f.write(data)

# ################################################################################################################################

    def set_data_path(self, data_path:'str') -> 'None':
        self.data_path = data_path

# ################################################################################################################################

    def sync_state(self) -> 'None':
        self.save_data()

# ################################################################################################################################

    def _get_many(self, object_id_list, add_object_id_key=True):
        # type: (list) -> list
        out = {}

        for object_id in object_id_list: # type: str
            value = self.in_ram_store.get(object_id)
            if value:
                value['object_id'] = object_id
                out[object_id] = value

        return out

# ################################################################################################################################

    def get_many(self, *args:'any_', **kwargs:'any_') -> 'anylist':
        with self.update_lock:
            return self._get_many(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class KVDB:
    """ Manages KVDB repositories.
    """
    def __init__(self):

        # Maps str -> repository objects
        self.repo = {} # type: stranydict

# ################################################################################################################################

    def internal_create_list_repo(
        self,
        repo_name,     # type: str
        data_path='',  # type: str
        max_size=1000, # type: int
        page_size=50   # type: int
    ) -> 'ListRepo':

        # Zato
        from zato.server.connection.kvdb.list_ import ListRepo

        repo = ListRepo(repo_name, data_path, max_size, page_size)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def internal_create_number_repo(
        self,
        repo_name,     # type: str
        data_path='',  # type: str
        max_size=1000, # type: int
        page_size=50   # type: int
    ) -> 'NumberRepo':

        # Zato
        from zato.server.connection.kvdb.number import NumberRepo

        repo = NumberRepo(repo_name, data_path, max_size, page_size)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def internal_create_object_repo(
        self,
        repo_name,     # type: str
        data_path=''   # type: str
    ) -> 'ObjectRepo':

        # Zato
        from zato.server.connection.kvdb.object_ import ObjectRepo

        repo = ObjectRepo(repo_name, data_path)
        return self.repo.setdefault(repo_name, repo)

# ################################################################################################################################

    def get(self, repo_name:'str') -> 'any_':
        return self.repo.get(repo_name)

# ################################################################################################################################

    def append(self, repo_name:'str', ctx:'ObjectCtx') -> 'None':
        repo = self.repo[repo_name] # type: ListRepo
        repo.append(ctx)

# ################################################################################################################################

    def get_object(self, repo_name:'str', object_id:'str') -> 'ObjectCtx':
        repo = self.repo[repo_name] # type: ListRepo
        return repo.get(object_id)

# ################################################################################################################################

    def get_list(self, repo_name:'str', cur_page:'int'=1, page_size:'int'=50) -> 'anylist':
        repo = self.repo[repo_name] # type: ListRepo
        return repo.get_list(cur_page, page_size)

# ################################################################################################################################

    def delete(self, repo_name:'str', object_id:'str') -> 'any_':
        repo = self.repo[repo_name] # type: ListRepo
        return repo.delete(object_id)

# ################################################################################################################################

    def remove_all(self, repo_name:'str') -> 'None':
        repo = self.repo[repo_name] # type: ListRepo
        repo.remove_all()

# ################################################################################################################################

    def get_size(self, repo_name:'str') -> 'int':
        repo = self.repo[repo_name] # type: ListRepo
        return repo.get_size()

# ################################################################################################################################
# ################################################################################################################################
