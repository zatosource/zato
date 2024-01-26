# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch

# Nose
from nose.tools import eq_

# Zato
from zato.common.kvdb.api import KVDB
from zato.common.test import rand_string, rand_int

# ##############################################################################

class KVDBTestCase(TestCase):
    def test_parse_config(self):

        class FakeSentinel:
            def __init__(self, sentinels, password, socket_timeout):
                self.sentinels = sentinels
                self.password = password
                self.socket_timeout = socket_timeout
                self.master_for_called_with = None

            def master_for(self, master_name):
                self.master_for_called_with = master_name
                return self

        class FakeStrictRedis:
            def __init__(self, **config):
                self.config = config

        class FakeKVDB(KVDB):
            def _get_connection_class(self):
                return FakeSentinel if self.has_sentinel else FakeStrictRedis

        def decrypt_func(password):
            return password

        sentinel1_host, sentinel1_port = 'a-' + rand_string(), rand_int()
        sentinel2_host, sentinel2_port = 'b-' + rand_string(), rand_int()

        password = rand_string()
        socket_timeout = rand_int()
        redis_sentinels_master = rand_string()
        redis_sentinels = ['{}:{}'.format(sentinel1_host, sentinel1_port), '{}:{}'.format(sentinel2_host, sentinel2_port)]

        try:
            config = {'use_redis_sentinels': True}
            kvdb = KVDB(config=config)
            kvdb.init()
        except ValueError as e:
            eq_(e.message, 'kvdb.redis_sentinels must be provided')
        else:
            self.fail('Expected a ValueError (kvdb.redis_sentinels)')

        try:
            config = {'use_redis_sentinels': True, 'redis_sentinels': redis_sentinels}
            kvdb = KVDB(config=config)
            kvdb.init()
        except ValueError as e:
            eq_(e.message, 'kvdb.redis_sentinels_master must be provided')
        else:
            self.fail('Expected a ValueError (kvdb.redis_sentinels_master)')

        config = Bunch({
            'use_redis_sentinels': True,
            'redis_sentinels':redis_sentinels,
            'redis_sentinels_master':redis_sentinels_master,
            'password': password,
            'socket_timeout':socket_timeout
        })
        kvdb = FakeKVDB(config=config, decrypt_func=decrypt_func)
        kvdb.init()

        eq_(sorted(kvdb.conn.sentinels), [(sentinel1_host, sentinel1_port), (sentinel2_host, sentinel2_port)])

        eq_(kvdb.conn.password, password)
        eq_(kvdb.conn.socket_timeout, socket_timeout)
        eq_(kvdb.conn.master_for_called_with, redis_sentinels_master)

        config = {'use_redis_sentinels': False}
        kvdb = FakeKVDB(config=config, decrypt_func=decrypt_func)
        kvdb.init()

        self.assertTrue(isinstance(kvdb.conn, FakeStrictRedis))
