# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Redis
from redis import ConnectionError, Redis

# Zato
from zato.common.util import new_cid

class RedisPubSubCommonTestCase(TestCase):

    def setUp(self):
        self.key_prefix = 'zato:pubsub:{}:'.format(new_cid())
        self.kvdb = Redis()

        try:
            self.kvdb.ping()
        except ConnectionError:
            self.has_redis = False
        else:
            self.has_redis = True

    def tearDown(self):
        for key in self.kvdb.keys('{}*'.format(self.key_prefix)):
            self.kvdb.delete(key)
