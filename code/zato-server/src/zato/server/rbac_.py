# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from itertools import chain
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
    def __init__(self, delete_role_callback):
        super(Registry, self).__init__()
        self.delete_role_callback = delete_role_callback

    def delete_role(self, delete_role):

        self.delete_role_callback(delete_role)

        # Delete the role itself.
        del self._roles[delete_role]

        # Recursively delete any children along with their own children.
        for child_id, child_parents in self._roles.items():
            if delete_role in child_parents:
                self.delete_role(child_id)

        # Remove the role from any permissions it may have been involved in.
        for item in chain(self._allowed, self._denied):
            for role, operation, resource in item:
                if role == delete_role:
                    item.remove([role, operation, resource])

    def delete_resource(self, delete_resource):
        del self._resources[delete_resource]

        # Remove the resource from any grants it may have been involved in.
        for item in chain(self._allowed, self._denied):
            for role, operation, resource in item:
                if resource == delete_resource:
                    item.remove([role, operation, resource])

# ################################################################################################################################

class RBAC(object):
    def __init__(self):
        self.registry = Registry(self._delete_callback)
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

    def _rbac_create_role(self, id, name, parent_id):
        self.role_id_to_name[id] = name
        self.role_name_to_id[name] = id
        self.registry.add_role(id, parents=[parent_id] if parent_id and id != parent_id else [])

    def _delete_callback(self, id):
        self._rbac_delete_role(id, self.role_id_to_name[id])

    def _rbac_delete_role(self, id, name):
        self.role_id_to_name.pop(id)
        self.role_name_to_id.pop(name)

    def create_role(self, id, name, parent_id):
        with self.update_lock:
            self._rbac_create_role(id, name, parent_id)

    def edit_role(self, id, old_name, name, parent_id):
        with self.update_lock:
            self._rbac_delete_role(id, old_name)
            self.registry._roles[id].clear() # Roles can have one parent only
            self._rbac_create_role(id, name, parent_id)

    def delete_role(self, id, name):
        with self.update_lock:
            self.registry.delete_role(id)

# ################################################################################################################################

    def create_client_role(self, client_def, role_id):
        with self.update_lock:

            if role_id not in self.role_id_to_name:
                raise ValueError('Role `{}` not found among `{}`'.format(role_id, self.role_id_to_name))

            self.client_def_to_role_id.setdefault(client_def, set()).add(role_id)
            self.role_id_to_client_def.setdefault(role_id, set()).add(client_def)

    def delete_client_role(self, client_def, role_id):
        with self.update_lock:
            self.client_def_to_role_id[client_def].remove(role_id)
            self.role_id_to_client_def[role_id].remove(client_def)

# ################################################################################################################################

    def create_resource(self, resource):
        with self.update_lock:
            self.registry.add_resource(resource)

    def delete_resource(self, resource):
        with self.update_lock:
            self.registry.delete_resource(resource)

# ################################################################################################################################

    def create_role_permission(self, role_id, resource_def, perm_id):
        with self.update_lock:
            pass

    def delete_role_permission(self, role_id, resource_def, perm_id):
        with self.update_lock:
            pass

# ################################################################################################################################
