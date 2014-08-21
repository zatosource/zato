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
from zato.server.rbac_ import RBAC

logger = getLogger(__name__)

class RBACTestCase(TestCase):

    def test_create_permission(self):

        name = uuid4().hex

        rbac = RBAC()
        rbac.create_permission(name)

        self.assertTrue(name in rbac.permissions)

    def test_edit_permission(self):

        old_name = uuid4().hex
        new_name = uuid4().hex

        rbac = RBAC()
        rbac.create_permission(old_name)
        rbac.edit_permission(old_name, new_name)

        self.assertTrue(old_name not in rbac.permissions)
        self.assertTrue(new_name in rbac.permissions)

    def test_delete_permission(self):

        name = uuid4().hex

        rbac = RBAC()
        rbac.create_permission(name)
        rbac.delete_permission(name)

        self.assertTrue(name not in rbac.permissions)
