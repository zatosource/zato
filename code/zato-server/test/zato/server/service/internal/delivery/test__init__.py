# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Zato
from zato.server.service.internal import AdminSIO
from zato.server.service.internal.pattern.delivery import GetDetails

# ################################################################################################################################

class GetDetailsTestCase(TestCase):
    def test_sio_subclasses_admin_sio(self):
        """ GH #203 - SimpleIO doesn't subclass AdminSIO.
        """
        self.assertTrue(issubclass(GetDetails.SimpleIO, AdminSIO))