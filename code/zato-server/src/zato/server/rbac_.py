# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# simple-rbac
from rbac.acl import Registry

# gevent
from gevent.lock import RLock

logger = getLogger('zato_rbac')

class RBAC(object):
    def __init__(self):
        self.registry = Registry()
        self.update_lock = RLock()
        self.permissions = set()

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
