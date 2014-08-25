# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

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

class RBACTestCase(TestCase):

# ################################################################################################################################

    def xtest_create_permission(self):

        name = rand_string()

        rbac = RBAC()
        rbac.create_permission(name)

        self.assertTrue(name in rbac.permissions)

# ################################################################################################################################

    def xtest_edit_permission(self):

        old_name, new_name = rand_string(2)

        rbac = RBAC()
        rbac.create_permission(old_name)
        rbac.edit_permission(old_name, new_name)

        self.assertTrue(old_name not in rbac.permissions)
        self.assertTrue(new_name in rbac.permissions)

# ################################################################################################################################

    def xtest_delete_permission(self):

        name = rand_string()

        rbac = RBAC()
        rbac.create_permission(name)
        rbac.delete_permission(name)

        self.assertTrue(name not in rbac.permissions)

# ################################################################################################################################

    def xtest_create_role_parent_not_given(self):

        id, name = rand_int(), rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, None)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

# ################################################################################################################################

    def xtest_create_role_parent_different_than_id(self):

        id, parent_id = rand_int(count=2)
        name = rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, parent_id)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set([parent_id]))

# ################################################################################################################################

    def xtest_create_role_parent_same_as_id(self):

        id = parent_id = rand_int()
        name = rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, parent_id)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

# ################################################################################################################################

    def xtest_create_role_parent_hierarchy(self):

        # Unlike in previous tests, here we set the IDs/names manually to ensure they are unique
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

    def xtest_edit_role_parent_not_given(self):

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

    def xtest_edit_role_change_name_only(self):

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

    def xtest_edit_role_change_parent_id_only(self):

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

        # Unlike in previous tests, here we set the IDs/names manually to ensure they are unique
        id1, parent_id1 = 1, 11
        id2, id3, id4 = 2, 3, 4

        parent_id1_new, parent_id2_new, parent_id3_new = 111, 222, 333

        name1, name2, name3, name4 = 'name1', 'name2', 'name3', 'name4'
        name1_new, name2_new, name3_new, name4_new = 'name1_new', 'name2_new', 'name3_new', 'name4_new'

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

# ################################################################################################################################
