# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from decimal import Decimal
from time import sleep
from unittest import main as unittest_main, TestCase
from uuid import uuid4

# Zato
from zato.cache import Cache, KeyExpiredError
from zato.common.py23_ import maxint

# ################################################################################################################################

class CacheTestCace(TestCase):

# ################################################################################################################################

    def test_set_get(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 1.0, None)
        c.set(key2, expected2, 1.0, None)
        c.set(key3, expected3, 1.0, None)

        returned1 = c.get(key1, None, False)
        self.assertEqual(returned1, expected1)

        returned2 = c.get(key2, None, False)
        self.assertEqual(returned2, expected2)

        returned3 = c.get(key3, None, False)
        self.assertEqual(returned3, expected3)

# ################################################################################################################################

    def test_set_defaults(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key2_expiry = 1000

        c = Cache()
        c.set(key1, expected1, 0.0, None)
        c.set(key2, expected2, key2_expiry, None)

        returned1 = c.get(key1, None, True)
        sleep(0.01)

        self.assertEqual(returned1.value, expected1)
        self.assertEqual(returned1.expiry, 0.0)
        self.assertEqual(returned1.expires_at, 0.0)
        self.assertEqual(returned1.hits, 1)
        self.assertEqual(returned1.prev_read, 0.0)
        self.assertEqual(returned1.prev_write, 0.0)
        self.assertLess(returned1.last_read, c.get_timestamp())
        self.assertLess(returned1.last_write, c.get_timestamp())

        returned2 = c.get(key2, None, True)
        sleep(0.01)

        self.assertEqual(returned2.value, expected2)
        self.assertEqual(returned2.expiry, key2_expiry)
        self.assertLess(c.get_timestamp() - returned2.expires_at, key2_expiry)
        self.assertEqual(returned2.hits, 1)
        self.assertLess(returned2.last_read, c.get_timestamp())
        self.assertLess(returned2.last_write, c.get_timestamp())
        self.assertEqual(returned2.prev_read, 0.0)
        self.assertEqual(returned2.prev_write, 0.0)

# ################################################################################################################################

    def test_set_get_with_details(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 1.0, None)
        c.set(key2, expected2, 1.0, None)
        c.set(key3, expected3, 1.0, None)

        # Add one second to be sure that at least that much time elapsed between when keys were stored and current time.
        now = c.get_timestamp() + 1

        returned1 = c.get(key1, None, True)
        self.assertEqual(returned1.value, expected1)
        self.assertEqual(returned1.position, 2)
        self.assertLess(returned1.last_read, now)
        self.assertLess(returned1.last_write, now)
        self.assertLess(returned1.prev_read, now)
        self.assertLess(returned1.prev_write, now)

        returned2 = c.get(key2, None, True)
        self.assertEqual(returned2.value, expected2)
        self.assertEqual(returned2.position, 2)
        self.assertLess(returned2.last_read, now)
        self.assertLess(returned2.last_write, now)
        self.assertLess(returned2.prev_read, now)
        self.assertLess(returned2.prev_write, now)

        returned3 = c.get(key3, None, True)
        self.assertEqual(returned3.value, expected3)
        self.assertEqual(returned3.position, 2)
        self.assertLess(returned3.last_read, now)
        self.assertLess(returned3.last_write, now)
        self.assertLess(returned3.prev_read, now)
        self.assertLess(returned3.prev_write, now)

# ################################################################################################################################

    def test_set_eviction_on_full(self):

        max_size = 2
        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache(max_size)
        c.set(key1, expected1, 1.0, None)
        c.set(key2, expected2, 1.0, None)
        c.set(key3, expected3, 1.0, None)

        # The value of max_size is 2 but we added 3 keys and there were no .get in between .set calls,
        # so we now expect that the first key will have been evicted and only key2 and key3 still exist.

        self.assertEqual(len(c), 2)
        self.assertEqual(c.max_size, 2)
        self.assertEqual(c.set_ops, 3)
        self.assertEqual(c.get_ops, 0)
        self.assertEqual(c.index(key3), 0)
        self.assertEqual(c.index(key2), 1)
        self.assertIsNone(c.index(key1))

# ################################################################################################################################

    def test_set_already_exists_no_expiry(self):

        key1, expected1 = 'key1', 'value1'
        expected1_new = 'value1_new'

        c = Cache()
        c.set(key1, expected1, 1.0, None)
        c.set(key1, expected1_new, 1.0, None)

        returned1_a = c.get(key1, None, False)
        returned1_b = c.get(key1, None, True)

        self.assertEqual(len(c), 1)
        self.assertEqual(returned1_a, expected1_new)
        self.assertEqual(returned1_b.value, expected1_new)

# ################################################################################################################################

    def test_set_already_exists_extend_expiry_on_get_true(self):

        key1, expected1 = 'key1', 'value1'

        # sleep_time is less then expiry but we sleep twice below so the total time
        # is greater than expiry and would have made the key expire
        # had it not been for extend_expiry_on_get=True

        expiry = 0.5
        sleep_time = expiry - expiry * 0.01

        c = Cache(extend_expiry_on_get=True)
        c.set(key1, expected1, expiry, None)

        sleep(sleep_time)

        returned1_a = c.get(key1, None, False)
        returned1_b = c.get(key1, None, True)

        self.assertEqual(returned1_a, expected1)
        self.assertEqual(len(c), 1)
        self.assertEqual(returned1_b.value, expected1)

        sleep(sleep_time)

        returned1_a = c.get(key1, None, False)
        returned1_b = c.get(key1, None, True)

        self.assertEqual(returned1_a, expected1)
        self.assertEqual(len(c), 1)
        self.assertEqual(returned1_b.value, expected1)

# ################################################################################################################################

    def test_set_already_exists_extend_expiry_on_get_false(self):

        key1, expected1 = 'key1', 'value1'

        # Unlike in test_set_already_exists_extend_expiry_on_get_false,
        # in this test case extend_expiry_on_get=False so .get won't extend it.

        expiry = 0.5
        sleep_time = expiry - expiry * 0.01

        c = Cache(extend_expiry_on_get=False)
        c.set(key1, expected1, expiry, None)

        sleep(sleep_time)

        returned1_a = c.get(key1, None, False)
        returned1_b = c.get(key1, None, True)

        self.assertEqual(returned1_a, expected1)
        self.assertEqual(len(c), 1)
        self.assertEqual(returned1_b.value, expected1)

        sleep(sleep_time)

        self.assertRaises(KeyExpiredError, c.get, key1, None, False)

        no_such_key_marker = object()
        value = c.get(key1, no_such_key_marker, True)
        self.assertIs(value, no_such_key_marker)

# ################################################################################################################################

    def test_set_already_exists_extend_expiry_on_set_true(self):

        key1, expected1 = 'key1', 'value1'
        expected1_new = 'value1_new'

        c = Cache(extend_expiry_on_set=True)
        c.set(key1, expected1, 3.0, None)
        sleep(0.11)
        c.set(key1, expected1_new, 0.0, None)

        returned1_a = c.get(key1, None, False)
        returned1_b = c.get(key1, None, True)

        self.assertEqual(len(c), 1)
        self.assertEqual(returned1_a, expected1_new)
        self.assertEqual(returned1_b.value, expected1_new)

# ################################################################################################################################

    def test_set_already_exists_extend_expiry_on_set_false(self):

        key1, expected1 = 'key1', 'value1'
        expected1_new = 'value1_new'

        c = Cache(extend_expiry_on_set=False)
        c.set(key1, expected1, 0.1, None)
        sleep(0.11)

        self.assertRaises(KeyExpiredError, c.set, key1, expected1_new, 0.0, None)
        self.assertEqual(len(c), 0)
        self.assertListEqual(c._expired_on_op, [key1])

        deleted = c.delete_expired()
        self.assertEqual(sorted(deleted), [key1])
        self.assertListEqual(c._expired_on_op, [])

# ################################################################################################################################

    def test_hits_per_position(self):

        max_size = 2
        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache(max_size)
        c.set(key1, expected1, 5.0, None)
        c.set(key2, expected2, 5.0, None)
        c.set(key3, expected3, 5.0, None)

        self.assertEqual(len(c.hits_per_position), 2)
        self.assertEqual(c.hits_per_position[0], 0)
        self.assertEqual(c.hits_per_position[1], 0)

        # Right now index0 is key3, so when we look up this key 3 times, we always find it at index0

        c.get('key3', None, False)
        c.get('key3', None, False)
        c.get('key3', None, False)
        self.assertEqual(c.hits_per_position[0], 3)

        # Now get key2 which will be found at index1 and getting it will move it to index0

        c.get('key2', None, False)
        self.assertEqual(c.hits_per_position[1], 1)

        # Now key2 is at index0 so getting this key will increase index0's counter

        c.get('key2', None, False)
        c.get('key2', None, False)
        c.get('key2', None, False)
        self.assertEqual(c.hits_per_position[0], 6)

        # Make sure index1's counter is still the same as it was
        self.assertEqual(c.hits_per_position[1], 1)

        # Looking up unknown keys should not increase any counters
        try:
            c.get(uuid4().hex, None, False)
        except KeyError:
            pass

        self.assertEqual(len(c.hits_per_position), 2)
        self.assertEqual(c.hits_per_position[0], 6)
        self.assertEqual(c.hits_per_position[1], 1)

# ################################################################################################################################

    def test_del(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 0.0, None)
        c.set(key2, expected2, 0.0, None)
        c.set(key3, expected3, 0.0, None)

        c.delete(key1)

        self.assertEqual(len(c), 2)
        self.assertNotIn(key1, c)
        self.assertIn(key2, c)
        self.assertIn(key3, c)

# ################################################################################################################################

    def test_delete_expired(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 0.1, None)
        c.set(key2, expected2, 0.0, None)
        c.set(key3, expected3, 0.03, None)

        sleep(0.12)

        deleted = c.delete_expired()
        self.assertEqual(sorted(deleted), [key1, key3])

        self.assertEqual(len(c), 1)
        self.assertNotIn(key1, c)
        self.assertIn(key2, c)
        self.assertNotIn(key3, c)

# ################################################################################################################################

    def test_get_deletes_expired_key(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 0.03, None)
        c.set(key2, expected2, 0.0, None)
        c.set(key3, expected3, 0.05, None)

        sleep(0.12)

        self.assertRaises(KeyExpiredError, c.get, key1, None, False)
        self.assertRaises(KeyExpiredError, c.get, key3, None, False)

        self.assertEqual(len(c), 1)
        self.assertNotIn(key1, c)
        self.assertIn(key2, c)
        self.assertNotIn(key3, c)

        # It will be arranged in the same order as .get were called in
        self.assertListEqual(c._expired_on_op, [key1, key3])

        deleted = c.delete_expired()
        self.assertEqual(sorted(deleted), [key1, key3])
        self.assertListEqual(c._expired_on_op, [])

# ################################################################################################################################

    def test_max_item_size_no_exception(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache(max_item_size=6)

        # No exception should be raised by the calls below as all values are not greater than max_item_size
        c.set(key1, expected1, 0.0, None)
        c.set(key2, expected2, 0.0, None)
        c.set(key3, expected3, 0.0, None)

# ################################################################################################################################

    def test_max_item_size_str_value_exceeded(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value33'

        c = Cache(max_item_size=6)

        # The first two must succeed
        c.set(key1, expected1, 0.0, None)
        c.set(key2, expected2, 0.0, None)

        # This fails because expected3 is > than max_item_size
        try:
            c.set(key3, expected3, 0.0, None)
        except ValueError as e:
            self.assertEqual(e.args[0], 'Value too long 7 > 6')
        else:
            self.fail('Expected aValueError to be raised')

# ################################################################################################################################

    def test_max_item_size_number_value(self):

        key1, expected1 = 'key1', maxint
        key2, expected2 = 'key2', 10.0 ** 10
        key3, expected3 = 'key3', Decimal(2.2 ** 2.2)
        key4, expected4 = 'key4', 123.45j+6789

        c = Cache(max_item_size=1)

        # No exception should be raised by the calls below as all values are numbers

        c.set(key1, expected1, 0.0, None)
        c.set(key2, expected2, 0.0, None)
        c.set(key3, expected3, 0.0, None)
        c.set(key4, expected4, 0.0, None)

        returned1 = c.get(key1, None, False)
        self.assertEqual(returned1, expected1)

        returned2 = c.get(key2, None, False)
        self.assertEqual(returned2, expected2)

        returned3 = c.get(key3, None, False)
        self.assertEqual(returned3, expected3)

        returned4 = c.get(key4, None, False)
        self.assertEqual(returned4, expected4)

# ################################################################################################################################

    def test_max_item_size_python_object(self):

        class MyClass:
            a = '1' * 10000
            b = 2.0 ** 20

        instance = MyClass()
        key1, expected1 = 'key1', instance

        c = Cache(max_item_size=1)

        # No exception should be raised by the calls below value is a non-string Python object
        c.set(key1, expected1, 0.0, None)

        returned1 = c.get(key1, None, False)
        self.assertIs(returned1, expected1)

# ################################################################################################################################

if __name__ == '__main__':
    unittest_main()

# ################################################################################################################################
