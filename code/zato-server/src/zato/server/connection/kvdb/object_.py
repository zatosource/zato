# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.server.connection.kvdb.core import BaseRepo

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class ObjectRepo(BaseRepo):
    """ Stores arbitrary objects as key/value pairs, in RAM only, without backing persistent storage.
    """
    def __init__(
        self,
        name='<ObjectRepo-name>',          # type: str
        data_path='<ObjectRepo-data_path>' # type: str
    ) -> 'None':

        super().__init__(name, data_path)

# ################################################################################################################################

    def _get(self, object_id:'str', default:'any_'=None, raise_if_not_found:'bool'=False) -> 'any_':
        value = self.in_ram_store.get(object_id)
        if value:
            return value
        else:
            if raise_if_not_found:
                raise KeyError('Object not found `{}`'.format(object_id))

# ################################################################################################################################

    def _set(self, object_id:'str', value:'any_') -> 'None':
        # type: (object, object) -> None
        self.in_ram_store[object_id] = value
        self.post_modify_state()

# ################################################################################################################################

    def _delete(self, object_id:'str') -> 'None':
        # type: (str) -> None
        self.in_ram_store.pop(object_id, None)

# ################################################################################################################################

    def _remove_all(self) -> 'None':
        self.in_ram_store[:] = []

# ################################################################################################################################

    def _get_size(self) -> 'int':
        # type: () -> int
        return len(self.in_ram_store)

# ################################################################################################################################

    def _get_many(self, object_id_list:'anylist', add_object_id_key:'bool'=True) -> 'anylist':
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
