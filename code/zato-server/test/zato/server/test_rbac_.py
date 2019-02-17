# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from unittest import TestCase
from uuid import uuid4

# simple-rbac
from rbac.acl import get_family

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.rbac_ import RBAC

logger = getLogger(__name__)

# ################################################################################################################################

class RoleTestCase(TestCase):

# ################################################################################################################################

    def test_create_role_parent_not_given(self):

        id, name = rand_int(), rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, None)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

# ################################################################################################################################

    def test_create_role_parent_different_than_id(self):

        id, parent_id = 1, 11
        name = rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, parent_id)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set([parent_id]))

# ################################################################################################################################

    def test_create_role_parent_same_as_id(self):

        id = parent_id = rand_int()
        name = rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, parent_id)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

# ################################################################################################################################

    def test_create_role_parent_hierarchy(self):

        id1, parent_id1 = 1, 11
        id2, id3, id4 = 2, 3, 4

        name1, name2, name3, name4 = 'name1', 'name2', 'name3', 'name4'

        rbac = RBAC()
        rbac.create_role(id1, name1, parent_id1)
        rbac.create_role(id2, name2, id1)
        rbac.create_role(id3, name3, id1)
        rbac.create_role(id4, name4, id2)

        self.assertEqual(rbac.role_id_to_name[id1], name1)
        self.assertEqual(rbac.role_id_to_name[id2], name2)
        self.assertEqual(rbac.role_id_to_name[id3], name3)
        self.assertEqual(rbac.role_id_to_name[id4], name4)

        self.assertIn(id1, rbac.registry._roles)
        self.assertIn(id2, rbac.registry._roles)
        self.assertIn(id3, rbac.registry._roles)
        self.assertIn(id4, rbac.registry._roles)

        self.assertEquals(rbac.registry._roles[id1], set([parent_id1]))
        self.assertEquals(rbac.registry._roles[id2], set([id1]))
        self.assertEquals(rbac.registry._roles[id3], set([id1]))
        self.assertEquals(rbac.registry._roles[id4], set([id2]))

        self.assertEquals(sorted(get_family(rbac.registry._roles, id1)), [None, id1, parent_id1])
        self.assertEquals(sorted(get_family(rbac.registry._roles, id2)), [None, id1, id2, parent_id1])
        self.assertEquals(sorted(get_family(rbac.registry._roles, id3)), [None, id1, id3, parent_id1])
        self.assertEquals(sorted(get_family(rbac.registry._roles, id4)), [None, id1, id2, id4, parent_id1])

# ################################################################################################################################

    def test_edit_role_parent_not_given(self):

        id = rand_int()
        old_name, new_name = rand_string(2)

        rbac = RBAC()
        rbac.create_role(id, old_name, None)
        rbac.edit_role(id, old_name, new_name, None)

        self.assertEqual(rbac.role_id_to_name[id], new_name)
        self.assertEqual(rbac.role_name_to_id[new_name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

# ################################################################################################################################

    def test_edit_role_change_name_only(self):

        id, parent_id = rand_int(count=2)
        old_name, new_name = rand_string(2)

        rbac = RBAC()
        rbac.create_role(id, old_name, parent_id)
        rbac.edit_role(id, old_name, new_name, parent_id)

        self.assertEqual(rbac.role_id_to_name[id], new_name)
        self.assertEqual(rbac.role_name_to_id[new_name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set([parent_id]))

# ################################################################################################################################

    def test_edit_role_change_parent_id_only(self):

        id = rand_int()
        old_parent_id, new_parent_id = uuid4().int, uuid4().int # Using uuid4 to make sure they really are unique
        old_name = new_name = rand_string()

        rbac = RBAC()
        rbac.create_role(id, old_name, old_parent_id)
        rbac.edit_role(id, old_name, new_name, new_parent_id)

        self.assertEqual(rbac.role_id_to_name[id], new_name)
        self.assertEqual(rbac.role_name_to_id[new_name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set([new_parent_id]))

# ################################################################################################################################

    def test_edit_role_parent_hierarchy(self):

        id1, parent_id1 = 1, 11
        id2, id3, id4 = 2, 3, 4

        parent_id1_new, parent_id2_new, parent_id3_new = 111, 222, 333

        name1, name2, name3, name4 = 'name1', 'name2', 'name3', 'name4'
        name1_new, name3_new, name4_new = 'name1_new', 'name3_new', 'name4_new'

        rbac = RBAC()
        rbac.create_role(id1, name1, parent_id1)
        rbac.create_role(id2, name2, id1)
        rbac.create_role(id3, name3, id1)
        rbac.create_role(id4, name4, id2)

        # Changing only the name here
        rbac.edit_role(id1, name1, name1_new, parent_id1)
        self.assertEqual(rbac.role_id_to_name[id1], name1_new)
        self.assertIn(id1, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id1], set([parent_id1]))
        self.assertEquals(sorted(get_family(rbac.registry._roles, id1)), [None, id1, parent_id1])

        # Changing the id1's parent ID here
        rbac.edit_role(id1, name1_new, name1_new, parent_id1_new)
        self.assertEqual(rbac.role_id_to_name[id1], name1_new)
        self.assertIn(id1, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id1], set([parent_id1_new]))
        self.assertEquals(sorted(get_family(rbac.registry._roles, id1)), [None, id1, parent_id1_new])

        # Changing both name and parent ID of id3
        rbac.edit_role(id3, name3, name3_new, parent_id3_new)
        self.assertEqual(rbac.role_id_to_name[id3], name3_new)
        self.assertIn(id3, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id3], set([parent_id3_new]))
        self.assertEquals(sorted(get_family(rbac.registry._roles, id3)), [None, id3, parent_id3_new])

        # id4 should have parent_id2_new as one of its predecessors as a result of the first edit
        # whereas the second one should update id4's name.
        rbac.edit_role(id2, name2, name2, parent_id2_new)
        rbac.edit_role(id4, name4, name4_new, id2)

        self.assertEquals(sorted(get_family(rbac.registry._roles, id4)), [None, id2, id4, parent_id2_new])
        self.assertEqual(rbac.role_id_to_name[id4], name4_new)

# ################################################################################################################################

    def test_delete_role_parent_not_given(self):

        id, name = rand_int(), rand_string()

        rbac = RBAC()

        # Create and confirm it was added
        rbac.create_role(id, name, None)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

        # Delete and confirm the action
        rbac.delete_role(id, name)

        self.assertNotIn(id, rbac.role_id_to_name)
        self.assertNotIn(name, rbac.role_name_to_id)
        self.assertNotIn(id, rbac.registry._roles)

# ################################################################################################################################

    def test_delete_role_parent_hierarchy_delete_root_id(self):

        id1, parent_id1 = 1, 11
        id2, id3, id4 = 2, 3, 4

        name1, name2, name3, name4 = 'name1', 'name2', 'name3', 'name4'

        rbac = RBAC()
        rbac.create_role(id1, name1, parent_id1)
        rbac.create_role(id2, name2, id1)
        rbac.create_role(id3, name3, id1)
        rbac.create_role(id4, name4, id2)

        rbac.delete_role(id1, name1)

        self.assertNotIn(id1, rbac.role_id_to_name)
        self.assertNotIn(id2, rbac.role_id_to_name)
        self.assertNotIn(id3, rbac.role_id_to_name)
        self.assertNotIn(id4, rbac.role_id_to_name)

        self.assertNotIn(name1, rbac.role_name_to_id)
        self.assertNotIn(name2, rbac.role_name_to_id)
        self.assertNotIn(name3, rbac.role_name_to_id)
        self.assertNotIn(name4, rbac.role_name_to_id)

        self.assertNotIn(id1, rbac.registry._roles)
        self.assertNotIn(id2, rbac.registry._roles)
        self.assertNotIn(id3, rbac.registry._roles)
        self.assertNotIn(id4, rbac.registry._roles)

# ################################################################################################################################

    def test_delete_role_parent_hierarchy_delete_branch(self):

        id1, parent_id1 = 1, 11
        id2, id3, id4 = 2, 3, 4

        name1, name2, name3, name4 = 'name1', 'name2', 'name3', 'name4'

        rbac = RBAC()
        rbac.create_role(id1, name1, parent_id1)
        rbac.create_role(id2, name2, id1)
        rbac.create_role(id3, name3, id1)
        rbac.create_role(id4, name4, id2)

        rbac.delete_role(id2, name2)

        self.assertIn(id1, rbac.role_id_to_name)
        self.assertNotIn(id2, rbac.role_id_to_name)
        self.assertIn(id3, rbac.role_id_to_name)
        self.assertNotIn(id4, rbac.role_id_to_name)

        self.assertIn(name1, rbac.role_name_to_id)
        self.assertNotIn(name2, rbac.role_name_to_id)
        self.assertIn(name3, rbac.role_name_to_id)
        self.assertNotIn(name4, rbac.role_name_to_id)

        self.assertIn(id1, rbac.registry._roles)
        self.assertNotIn(id2, rbac.registry._roles)
        self.assertIn(id3, rbac.registry._roles)
        self.assertNotIn(id4, rbac.registry._roles)

# ################################################################################################################################

    def test_delete_role_parent_hierarchy_delete_leaf(self):

        id1, parent_id1 = 1, 11
        id2, id3, id4 = 2, 3, 4

        name1, name2, name3, name4 = 'name1', 'name2', 'name3', 'name4'

        rbac = RBAC()
        rbac.create_role(id1, name1, parent_id1)
        rbac.create_role(id2, name2, id1)
        rbac.create_role(id3, name3, id1)
        rbac.create_role(id4, name4, id2)

        rbac.delete_role(id4, name4)

        self.assertIn(id1, rbac.role_id_to_name)
        self.assertIn(id2, rbac.role_id_to_name)
        self.assertIn(id3, rbac.role_id_to_name)
        self.assertNotIn(id4, rbac.role_id_to_name)

        self.assertIn(name1, rbac.role_name_to_id)
        self.assertIn(name2, rbac.role_name_to_id)
        self.assertIn(name3, rbac.role_name_to_id)
        self.assertNotIn(name4, rbac.role_name_to_id)

        self.assertIn(id1, rbac.registry._roles)
        self.assertIn(id2, rbac.registry._roles)
        self.assertIn(id3, rbac.registry._roles)
        self.assertNotIn(id4, rbac.registry._roles)

# ################################################################################################################################

class PermissionTestCase(TestCase):

# ################################################################################################################################

    def test_create_permission(self):

        id1, name1 = 1, 'name1'
        id2, name2 = 2, 'name2'

        rbac = RBAC()
        rbac.create_permission(id1, name1)
        rbac.create_permission(id2, name2)

        self.assertEquals(rbac.permissions[id1], name1)
        self.assertEquals(rbac.permissions[id2], name2)

# ################################################################################################################################

    def test_edit_permission_exists(self):

        id1, name1 = 1, 'name1'
        id2, name2 = 2, 'name2'

        new_name1 = 'new_name1'

        rbac = RBAC()
        rbac.create_permission(id1, name1)
        rbac.create_permission(id2, name2)
        rbac.edit_permission(id1, new_name1)

        self.assertEquals(rbac.permissions[id1], new_name1)
        self.assertEquals(rbac.permissions[id2], name2)

# ################################################################################################################################

    def test_edit_permission_does_not_exist(self):

        id, name = 1, 'name'

        rbac = RBAC()
        rbac.create_permission(id, name)
        self.assertRaises(ValueError, rbac.edit_permission, 1234, 'new_name')

# ################################################################################################################################

    def test_delete_permission_no_client_permission(self):

        id, name = 1, 'name'

        rbac = RBAC()
        rbac.create_permission(id, name)
        rbac.delete_permission(id)

        self.assertTrue(id not in rbac.permissions)

# ################################################################################################################################

    def test_delete_permission_has_role_permission(self):

        role_id1, role_name1 = 1, 'role_name1'
        role_id2, role_name2 = 2, 'role_name2'

        perm_id1, perm_name1 = 11, 'perm_name1'
        perm_id2, perm_name2 = 22, 'perm_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_role_permission_allow(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_allow(role_id1, perm_id2, res_name1)

        rbac.create_role_permission_allow(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_allow(role_id2, perm_id2, res_name2)

        self.assertIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

        rbac.delete_permission(perm_id1)

        self.assertNotIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertNotIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

# ################################################################################################################################

class ClientRoleTestCase(TestCase):

# ################################################################################################################################

    def test_create_client_role_valid_role(self):
        client_def1 = 'def1'
        client_def2 = 'def2'

        role_id1, role_name1 = 1, 'name1'
        role_id2, role_name2 = 2, 'name2'
        role_id3, role_name3 = 3, 'name3'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)
        rbac.create_role(role_id3, role_name3, None)

        rbac.create_client_role(client_def1, role_id1)
        rbac.create_client_role(client_def1, role_id2)

        rbac.create_client_role(client_def2, role_id2)
        rbac.create_client_role(client_def2, role_id3)

        self.assertEquals(rbac.client_def_to_role_id[client_def1], set([role_id1, role_id2]))
        self.assertEquals(rbac.client_def_to_role_id[client_def2], set([role_id2, role_id3]))

        self.assertEquals(rbac.role_id_to_client_def[role_id1], set([client_def1]))
        self.assertEquals(rbac.role_id_to_client_def[role_id2], set([client_def1, client_def2]))

# ################################################################################################################################

    def test_create_client_role_invalid_role(self):
        client_def = rand_string()
        role_id = rand_int()

        rbac = RBAC()
        self.assertRaises(ValueError, rbac.create_client_role, client_def, role_id)

# ################################################################################################################################

    def test_delete_client_role(self):

        client_def1 = 'def1'
        client_def2 = 'def2'

        role_id1, role_name1 = 1, 'name1'
        role_id2, role_name2 = 2, 'name2'
        role_id3, role_name3 = 3, 'name3'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)
        rbac.create_role(role_id3, role_name3, None)

        rbac.create_client_role(client_def1, role_id1)
        rbac.create_client_role(client_def1, role_id2)

        rbac.create_client_role(client_def2, role_id2)
        rbac.create_client_role(client_def2, role_id3)

        rbac.delete_client_role(client_def1, role_id1)
        rbac.delete_client_role(client_def2, role_id3)

        self.assertEquals(rbac.client_def_to_role_id[client_def1], set([role_id2]))
        self.assertEquals(rbac.client_def_to_role_id[client_def2], set([role_id2]))

        rbac.delete_client_role(client_def1, role_id2)
        rbac.delete_client_role(client_def2, role_id2)

        self.assertEquals(rbac.client_def_to_role_id[client_def1], set([]))
        self.assertEquals(rbac.client_def_to_role_id[client_def2], set([]))

# ################################################################################################################################

class ResourceTestCase(TestCase):

# ################################################################################################################################

    def test_create_resource(self):
        name1, name2 = 'name1', 'name2'

        rbac = RBAC()
        rbac.create_resource(name1)
        rbac.create_resource(name2)

        self.assertEquals(rbac.registry._resources[name1], set())
        self.assertEquals(rbac.registry._resources[name2], set())

# ################################################################################################################################

    def test_delete_resource_no_roles(self):
        name1, name2 = 'name1', 'name2'

        rbac = RBAC()
        rbac.create_resource(name1)
        rbac.create_resource(name2)
        rbac.delete_resource(name2)

        self.assertEquals(rbac.registry._resources[name1], set())
        self.assertNotIn(name2, rbac.registry._resources)

    def test_delete_resource_has_roles(self):
        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1, perm_id2 = 11, 22
        perm_name1, perm_name2 = 'perm_name1', 'perm_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_role_permission_allow(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_allow(role_id1, perm_id2, res_name1)

        rbac.create_role_permission_allow(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_allow(role_id2, perm_id2, res_name2)

        self.assertIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

        rbac.delete_resource(res_name1)

        self.assertNotIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertNotIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

# ################################################################################################################################

class RolePermissionAllowTestCase(TestCase):

    def test_create_role_permission_allow(self):

        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1, perm_id2 = 11, 22
        perm_name1, perm_name2 = 'perm_name1', 'perm_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_role_permission_allow(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_allow(role_id1, perm_id2, res_name1)

        rbac.create_role_permission_allow(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_allow(role_id2, perm_id2, res_name2)

        self.assertIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

    def test_delete_role_permission_allow(self):

        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1, perm_id2 = 11, 22
        perm_name1, perm_name2 = 'perm_name1', 'perm_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_role_permission_allow(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_allow(role_id1, perm_id2, res_name1)

        rbac.create_role_permission_allow(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_allow(role_id2, perm_id2, res_name2)

        self.assertIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

        rbac.delete_role_permission_allow(role_id1, perm_id1, res_name1)
        rbac.delete_role_permission_allow(role_id2, perm_id1, res_name2)

        self.assertNotIn((role_id1, perm_id1, res_name1), rbac.registry._allowed)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._allowed)

        self.assertNotIn((role_id2, perm_id1, res_name2), rbac.registry._allowed)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._allowed)

# ################################################################################################################################

class RolePermissionDeleteTestCase(TestCase):

    def test_create_role_permission_deny(self):

        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1, perm_id2 = 11, 22
        perm_name1, perm_name2 = 'perm_name1', 'perm_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_role_permission_deny(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_deny(role_id1, perm_id2, res_name1)

        rbac.create_role_permission_deny(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_deny(role_id2, perm_id2, res_name2)

        self.assertIn((role_id1, perm_id1, res_name1), rbac.registry._denied)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._denied)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._denied)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._denied)

    def test_delete_role_permission_deny(self):

        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1, perm_id2 = 11, 22
        perm_name1, perm_name2 = 'perm_name1', 'perm_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_role_permission_deny(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_deny(role_id1, perm_id2, res_name1)

        rbac.create_role_permission_deny(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_deny(role_id2, perm_id2, res_name2)

        self.assertIn((role_id1, perm_id1, res_name1), rbac.registry._denied)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._denied)

        self.assertIn((role_id2, perm_id1, res_name2), rbac.registry._denied)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._denied)

        rbac.delete_role_permission_deny(role_id1, perm_id1, res_name1)
        rbac.delete_role_permission_deny(role_id2, perm_id1, res_name2)

        self.assertNotIn((role_id1, perm_id1, res_name1), rbac.registry._denied)
        self.assertIn((role_id1, perm_id2, res_name1), rbac.registry._denied)

        self.assertNotIn((role_id2, perm_id1, res_name2), rbac.registry._denied)
        self.assertIn((role_id2, perm_id2, res_name2), rbac.registry._denied)

# ################################################################################################################################

class IsAllowedTestCase(TestCase):

    def test_is_role_allowed_basic(self):

        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1, perm_id2 = 11, 22
        perm_name1, perm_name2 = 'perm_name1', 'perm_name2'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, None)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)
        rbac.create_permission(perm_id2, perm_name2)

        rbac.create_role_permission_allow(role_id1, perm_id1, res_name1)
        rbac.create_role_permission_allow(role_id2, perm_id1, res_name2)
        rbac.create_role_permission_deny(role_id2, perm_id2, res_name2)

        self.assertTrue(rbac.is_role_allowed(role_id1, perm_id1, res_name1))
        self.assertTrue(rbac.is_role_allowed(role_id2, perm_id1, res_name2))

        # Denied implicitly because there is no explicit 'allow'
        self.assertFalse(rbac.is_role_allowed(role_id1, perm_id2, res_name1))

        # Denied explicitly
        self.assertFalse(rbac.is_role_allowed(role_id2, perm_id2, res_name2))

    def test_is_role_allowed_parent_hierarchy(self):

        role_id1, role_id2 = 1, 2
        role_name1, role_name2 = 'role_name1', 'role_name2'

        res_name1, res_name2 = 'res_name1', 'res_name2'

        perm_id1 = 11
        perm_name1 = 'perm_name1'

        rbac = RBAC()

        rbac.create_role(role_id1, role_name1, None)
        rbac.create_role(role_id2, role_name2, role_id1)

        rbac.create_resource(res_name1)
        rbac.create_resource(res_name2)

        rbac.create_permission(perm_id1, perm_name1)

        rbac.create_role_permission_allow(role_id2, perm_id1, res_name1)
        rbac.create_role_permission_deny(role_id2, perm_id1, res_name2)

        self.assertTrue(rbac.is_role_allowed(role_id2, perm_id1, res_name1))
        self.assertFalse(rbac.is_role_allowed(role_id2, perm_id1, res_name2))

        # Denied implicitly because there is no explicit 'allow'
        self.assertFalse(rbac.is_role_allowed(role_id1, perm_id1, res_name1))
        self.assertFalse(rbac.is_role_allowed(role_id1, perm_id1, res_name2))

# ################################################################################################################################
