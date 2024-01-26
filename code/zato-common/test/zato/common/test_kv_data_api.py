# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# stdlib
from unittest import main

# Zato
from zato.common.kv_data import default_expiry_time, KeyCtx, KVDataAPI
from zato.common.test import ODBTestCase, rand_datetime, rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

cluster_id = 1

# ################################################################################################################################
# ################################################################################################################################

class KVDataAPITestCase(ODBTestCase):

# ################################################################################################################################

    def test_key_ctx(self):

        key = rand_string()
        data_type = 'string'
        creation_time = rand_datetime()

        ctx = KeyCtx()
        ctx.key = key
        ctx.data_type = data_type
        ctx.creation_time = creation_time

        self.assertEqual(ctx.key, key)
        self.assertEqual(ctx.data_type, data_type)
        self.assertEqual(ctx.creation_time, creation_time)

        self.assertIsNone(ctx.value)
        self.assertIsNone(ctx.expiry_time)

# ################################################################################################################################

    def test_session(self):

        kv_data_api = KVDataAPI(cluster_id, self.session_wrapper)

        session = kv_data_api._get_session()

        result = session.execute('SELECT 1+1')
        rows = result.fetchall()

        self.assertListEqual(rows, [(2,)])

# ################################################################################################################################

    def test_set_with_ctx(self):

        key = rand_string()
        value = rand_string()
        data_type = 'text'
        creation_time = rand_datetime(to_string=False) # type: datetime

        ctx = KeyCtx()
        ctx.key = key
        ctx.value = value
        ctx.data_type = data_type
        ctx.creation_time = creation_time

        kv_data_api = KVDataAPI(cluster_id, self.session_wrapper)

        # Set the key ..
        kv_data_api.set_with_ctx(ctx)

        # .. let's get it back ..
        result = kv_data_api.get(key)

        # .. and run all the assertions now.
        self.assertEqual(result.key, ctx.key)
        self.assertEqual(result.value, ctx.value)
        self.assertEqual(result.data_type, ctx.data_type)
        self.assertEqual(result.creation_time, ctx.creation_time)
        self.assertEqual(result.expiry_time, default_expiry_time)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
