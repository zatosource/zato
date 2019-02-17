# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# cryptography
from cryptography.hazmat.backends import default_backend

# ################################################################################################################################

class CryptoBackendTestCase(TestCase):
    def test_crypto_backend_available(self):
        """ Will raise an exception if the cryptography's package backend cannot be instantiated,
        which can happen if we hit upon https://github.com/pyca/cryptography/commit/30e199e0fb220a17b3089508a59d29a2924f10e4
        """
        default_backend()

# ################################################################################################################################
