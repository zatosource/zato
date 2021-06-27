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

class ObjectRepo(BaseRepo):
    """ Stores arbitrary objects as key/value pairs, in RAM only, without backing persistent storage.
    """
    def __init__(self, name='<ObjectRepo-name>'):
        # type: (str, int, int) -> None
        super().__init__(name)

        # In-RAM database of objects
        self.in_ram_store = {}

        # Used to synchronise updates
        self.lock = RLock()

# ################################################################################################################################

    def _get(self, object_id, default=None, raise_if_not_found=False):
        # type: (str) -> object
        value = self.in_ram_store.get(object_id)
        if value:
            return value
        else:
            if raise_if_not_found:
                raise KeyError('Object not found `{}`'.format(object_id))

# ################################################################################################################################

    def _set(self, object_id, value):
        # type: (object, object) -> None
        self.in_ram_store[object_id] = value

# ################################################################################################################################

    def _delete(self, object_id):
        # type: (str) -> None
        self.in_ram_store.pop(object_id, None)

# ################################################################################################################################

    def _remove_all(self):
        # type: () -> None
        self.in_ram_store[:] = []

# ################################################################################################################################

    def _get_size(self):
        # type: () -> int
        return len(self.in_ram_store)

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
# ################################################################################################################################
