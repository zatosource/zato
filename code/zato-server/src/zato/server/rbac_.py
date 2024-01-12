# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# simple-rbac
from rbac.acl import Registry as _Registry

# gevent
from gevent.lock import RLock

# Zato
from zato.common.api import ZATO_NONE
from zato.common.util.api import make_repr, wait_for_dict_key

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
        self.delete_from_permissions('role', delete_role)

    def delete_resource(self, delete_resource):
        """ Remove the resource from any grants it may have been involved in but only if we actually had it.
        """
        if self._resources.pop(delete_resource, ZATO_NONE) != ZATO_NONE:
            self.delete_from_permissions('resource', delete_resource)

    def delete_from_permissions(self, compare_name, delete_item):

        reg_del = {'_allowed':[], '_denied':[]}
        name_to_idx = {'role':0, 'operation':1, 'resource':2}

        for name in reg_del:
            item = getattr(self, name)
            for values in item:
                if values[name_to_idx[compare_name]] == delete_item:
                    reg_del[name].append(values)

        for name in reg_del:
            item = getattr(self, name)
            for value in reg_del[name]:
                del item[value]

    def delete_allow(self, config):
        del self._allowed[config]

    def delete_deny(self, config):
        del self._denied[config]

# ################################################################################################################################

class RBAC:
    def __init__(self):
        self.registry = Registry(self._delete_callback)
        self.update_lock = RLock()
        self.permissions = {}
        self.http_permissions = {}
        self.role_id_to_name = {}
        self.role_name_to_id = {}
        self.client_def_to_role_id = {}
        self.role_id_to_client_def = {}

# ################################################################################################################################

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

    def create_permission(self, id, name):
        with self.update_lock:
            self.permissions[id] = name

    def edit_permission(self, id, new_name):
        with self.update_lock:
            if not id in self.permissions:
                raise ValueError('Permission ID `{}` ({}) not found among `{}`'.format(id, new_name, self.permissions))
            self.permissions[id] = new_name

    def delete_permission(self, id):
        with self.update_lock:
            del self.permissions[id]
            self.registry.delete_from_permissions('operation', id)

    def set_http_permissions(self):
        """ Maps HTTP verbs to CRUD permissions.
        """
        verb_map = {
            'GET': 'Read',
            'POST': 'Create',
            'PATCH': 'Update',
            'PUT': 'Update',
            'DELETE': 'Delete',
        }

        for verb, target_perm_name in verb_map.items():
            for perm_id, perm_name in self.permissions.items():
                if target_perm_name == perm_name:
                    self.http_permissions[verb] = perm_id
                    break

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

            self.client_def_to_role_id.setdefault(client_def, []).append(role_id)
            self.role_id_to_client_def.setdefault(role_id, []).append(client_def)

    def delete_client_role(self, client_def, role_id):
        with self.update_lock:
            self.client_def_to_role_id[client_def].remove(role_id)
            self.role_id_to_client_def[role_id].remove(client_def)

    def wait_for_client_role(self, role_id):
        wait_for_dict_key(self.role_id_to_name, role_id)

# ################################################################################################################################

    def create_resource(self, resource):
        with self.update_lock:
            self.registry.add_resource(resource)

    def delete_resource(self, resource):
        with self.update_lock:
            self.registry.delete_resource(resource)

# ################################################################################################################################

    def create_role_permission_allow(self, role_id, perm_id, resource):
        with self.update_lock:
            self.registry.allow(role_id, perm_id, resource)

    def create_role_permission_deny(self, role_id, perm_id, resource):
        with self.update_lock:
            self.registry.deny(role_id, perm_id, resource)

    def delete_role_permission_allow(self, role_id, perm_id, resource):
        with self.update_lock:
            self.registry.delete_allow((role_id, perm_id, resource))

    def delete_role_permission_deny(self, role_id, perm_id, resource):
        with self.update_lock:
            self.registry.delete_deny((role_id, perm_id, resource))

# ################################################################################################################################

    def is_role_allowed(self, role_id, perm_id, resource):
        """ Returns True/False depending on whether a given role is allowed to obtain a selected permission for a resource.
        """
        return self.registry.is_allowed(role_id, perm_id, resource)

    def is_client_allowed(self, client_def, perm_id, resource):
        """ Returns True/False depending on whether a given client is allowed to obtain a selected permission for a resource.
        All of the client's roles are consulted and if any is allowed, True is returned. If none is, False is returned.
        """
        roles = self.client_def_to_role_id.get(client_def, ZATO_NONE)
        return self.registry.is_any_allowed(roles, perm_id, resource) if roles != ZATO_NONE else False

    def is_http_client_allowed(self, client_def, http_verb, resource):
        """ Same as is_client_allowed but accepts a HTTP verb rather than a permission ID.
        """
        return self.is_client_allowed(client_def, self.http_permissions[http_verb], resource)

# ################################################################################################################################
