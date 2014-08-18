# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from itertools import cycle
from logging import getLogger

# simple-rbac
from rbac.acl import Registry as _Registry

# gevent
from gevent.lock import RLock

# Zato
from zato.common.util import make_repr

# ################################################################################################################################

logger = getLogger('zato_rbac')

# ################################################################################################################################

class Registry(_Registry):
    def __init__(self):
        super(Registry, self).__init__()

    def delete_role(self, delete_role):
        del self._roles[delete_role]

        for item in cycle([self._allowed, self._denied]):
            for role, operation, resource in item:
                if role == delete_role:
                    item.remove([role, operation, resource])

# ################################################################################################################################

class RBAC(object):
    def __init__(self):
        self.registry = Registry()
        self.update_lock = RLock()
        self.permissions = set()
        self.role_id_to_name = {}
        self.role_name_to_id = {}
        self.client_def_to_role_id = {}
        self.role_id_to_client_def = {}

# ################################################################################################################################

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

    def create_permission(self, name):
        with self.update_lock:
            self.permissions.add(name)

    def edit_permission(self, old_name, name):
        with self.update_lock:
            self.permissions.remove(old_name)
            self.permissions.add(name)

    def delete_permission(self, name):
        with self.update_lock:
            self.permissions.remove(name)

# ################################################################################################################################

    def _rbac_create_role(self, id, name):
        self.role_id_to_name[id] = name
        self.role_name_to_id[name] = id

    def _rbac_delete_role(self, id, name):
        self.role_id_to_name.pop(id)
        self.role_name_to_id.pop(name)

    def create_role(self, id, name, parent_id):
        with self.update_lock:
            self.registry.add_role(id, parents=[parent_id] if id != parent_id else [])
            self._rbac_create_role(id, name)

    def edit_role(self, id, old_name, name):
        with self.update_lock:
            self._rbac_delete_role(id, old_name)
            self._rbac_create_role(id, name)

    def delete_role(self, id, name):
        logger.warn('delete %r %r', id, name)
        '''with self.update_lock:
            self._rbac_delete_role(id, name)
            self.registry.delete_role(id)'''

# ################################################################################################################################

    def create_client_role(self, client_def, role_id):
        with self.update_lock:
            item_list = self.client_def_to_role_id.setdefault(client_def, set())
            item_list.add(role_id)

    def delete_client_role(self, client_def, role_id):
        with self.update_lock:
            item_list = self.role_id_to_client_def.setdefault(role_id, set())
            item_list.add(client_def)

# ################################################################################################################################
