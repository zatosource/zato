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

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.rbac_ import RBAC

logger = getLogger(__name__)

# ################################################################################################################################

class RBACTestCase(TestCase):

# ################################################################################################################################

    def test_create_permission(self):

        name = rand_string()

        rbac = RBAC()
        rbac.create_permission(name)

        self.assertTrue(name in rbac.permissions)

# ################################################################################################################################

    def test_edit_permission(self):

        old_name, new_name = rand_string(2)

        rbac = RBAC()
        rbac.create_permission(old_name)
        rbac.edit_permission(old_name, new_name)

        self.assertTrue(old_name not in rbac.permissions)
        self.assertTrue(new_name in rbac.permissions)

# ################################################################################################################################

    def test_delete_permission(self):

        name = rand_string()

        rbac = RBAC()
        rbac.create_permission(name)
        rbac.delete_permission(name)

        self.assertTrue(name not in rbac.permissions)

# ################################################################################################################################

    def test_create_role_parent_not_given(self):

        id, name = rand_int(), rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, None)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set())

    def test_create_role_parent_different_than_id(self):

        id, parent_id = rand_int(count=2)
        name = rand_string()

        rbac = RBAC()
        rbac.create_role(id, name, parent_id)

        self.assertEqual(rbac.role_id_to_name[id], name)
        self.assertEqual(rbac.role_name_to_id[name], id)
        self.assertIn(id, rbac.registry._roles)
        self.assertEquals(rbac.registry._roles[id], set([parent_id]))

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
