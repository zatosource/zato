# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from time import sleep
from unittest import main as unittest_main, TestCase
from uuid import uuid4

# Zato
sys.path.insert(0, '.')
from cache import Cache, KeyExpiredError

# ################################################################################################################################

class CacheTestCace(TestCase):

# ################################################################################################################################

    def test_set_get(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1)
        c.set(key2, expected2)
        c.set(key3, expected3)

        returned1 = c.get(key1)
        self.assertEquals(returned1, expected1)

        returned2 = c.get(key2)
        self.assertEquals(returned2, expected2)

        returned3 = c.get(key3)
        self.assertEquals(returned3, expected3)

# ################################################################################################################################

    def test_set_defaults(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key2_expiry = 1000

        c = Cache()
        c.set(key1, expected1)
        c.set(key2, expected2, key2_expiry)

        returned1 = c.get(key1, True)
        sleep(0.01)

        self.assertEquals(returned1.value, expected1)
        self.assertEquals(returned1.expiry, 0.0)
        self.assertEquals(returned1.expires_at, 0.0)
        self.assertEquals(returned1.hits, 1)
        self.assertEquals(returned1.prev_read, 0.0)
        self.assertEquals(returned1.prev_write, 0.0)
        self.assertLess(returned1.last_read, c.get_timestamp())
        self.assertLess(returned1.last_write, c.get_timestamp())

        returned2 = c.get(key2, True)
        sleep(0.01)

        self.assertEquals(returned2.value, expected2)
        self.assertEquals(returned2.expiry, key2_expiry)
        self.assertLess(c.get_timestamp() - returned2.expires_at, key2_expiry)
        self.assertEquals(returned2.hits, 1)
        self.assertLess(returned2.last_read, c.get_timestamp())
        self.assertLess(returned2.last_write, c.get_timestamp())
        self.assertEquals(returned2.prev_read, 0.0)
        self.assertEquals(returned2.prev_write, 0.0)

# ################################################################################################################################

    def test_set_get_with_details(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1)
        c.set(key2, expected2)
        c.set(key3, expected3)

        # Add one second to be sure that at least that much time elapsed between when keys were stored and current time. 
        now = c.get_timestamp() + 1

        returned1 = c.get(key1, True)
        self.assertEquals(returned1.value, expected1)
        self.assertEquals(returned1.position, 2)
        self.assertLess(returned1.last_read, now)
        self.assertLess(returned1.last_write, now)
        self.assertLess(returned1.prev_read, now)
        self.assertLess(returned1.prev_write, now)

        
        returned2 = c.get(key2, True)
        self.assertEquals(returned2.value, expected2)
        self.assertEquals(returned2.position, 2)
        self.assertLess(returned2.last_read, now)
        self.assertLess(returned2.last_write, now)
        self.assertLess(returned2.prev_read, now)
        self.assertLess(returned2.prev_write, now)

        returned3 = c.get(key3, True)
        self.assertEquals(returned3.value, expected3)
        self.assertEquals(returned3.position, 2)
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
        c.set(key1, expected1)
        c.set(key2, expected2)
        c.set(key3, expected3)

        # The value of max_size is 2 but we added 3 keys and there were no .get in between .set calls,
        # so we now expect that the first key will have been evicted and only key2 and key3 still exist.

        self.assertEquals(len(c), 2)
        self.assertEquals(c.max_size, 2)
        self.assertEquals(c.set_ops, 3)
        self.assertEquals(c.get_ops, 0)
        self.assertEquals(c.index(key3), 0)
        self.assertEquals(c.index(key2), 1)
        self.assertIsNone(c.index(key1))

# ################################################################################################################################

    def test_set_already_exists_no_expiry(self):

        key1, expected1 = 'key1', 'value1'
        expected1_new = 'value1_new'

        c = Cache()
        c.set(key1, expected1)
        c.set(key1, expected1_new)

        returned1_a = c.get(key1)
        returned1_b = c.get(key1, True)

        self.assertEquals(len(c), 1)
        self.assertEquals(returned1_a, expected1_new)
        self.assertEquals(returned1_b.value, expected1_new)

# ################################################################################################################################

    def test_set_already_exists_extend_expiry_on_set_true(self):

        key1, expected1 = 'key1', 'value1'
        expected1_new = 'value1_new'

        c = Cache(extend_expiry_on_set=True)
        c.set(key1, expected1, 0.1)
        sleep(0.11)
        c.set(key1, expected1_new)

        returned1_a = c.get(key1)
        returned1_b = c.get(key1, True)

        self.assertEquals(len(c), 1)
        self.assertEquals(returned1_a, expected1_new)
        self.assertEquals(returned1_b.value, expected1_new)

# ################################################################################################################################

    def test_set_already_exists_extend_expiry_on_set_false(self):

        key1, expected1 = 'key1', 'value1'
        expected1_new = 'value1_new'

        c = Cache(extend_expiry_on_set=False)
        c.set(key1, expected1, 0.1)
        sleep(0.11)

        self.assertRaises(KeyExpiredError, c.set, key1, expected1_new)
        self.assertEquals(len(c), 0)
        self.assertListEqual(c._expired_on_op, [key1])

        deleted = c.delete_expired()
        self.assertEquals(sorted(deleted), [key1])
        self.assertListEqual(c._expired_on_op, [])

# ################################################################################################################################

    def test_hits_per_position(self):

        max_size = 2
        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache(max_size)
        c.set(key1, expected1)
        c.set(key2, expected2)
        c.set(key3, expected3)


        self.assertEquals(len(c.hits_per_position), 2)
        self.assertEquals(c.hits_per_position[0], 0)
        self.assertEquals(c.hits_per_position[1], 0)


        # Right now index0 is key3, so when we look up this key 3 times, we always find it at index0

        c.get('key3')
        c.get('key3')
        c.get('key3')
        self.assertEquals(c.hits_per_position[0], 3)


        # Now get key2 which will be found at index1 and getting it will move it to index0

        c.get('key2')
        self.assertEquals(c.hits_per_position[1], 1)


        # Now key2 is at index0 so getting this key will increase index0's counter

        c.get('key2')
        c.get('key2')
        c.get('key2')
        self.assertEquals(c.hits_per_position[0], 6)


        # Make sure index1's counter is still the same as it was
        self.assertEquals(c.hits_per_position[1], 1)


        # Looking up unknown keys should not increase any counters
        try:
            c.get(uuid4().hex)
        except KeyError:
            pass

        self.assertEquals(len(c.hits_per_position), 2)
        self.assertEquals(c.hits_per_position[0], 6)
        self.assertEquals(c.hits_per_position[1], 1)

# ################################################################################################################################

    def test_del(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1)
        c.set(key2, expected2)
        c.set(key3, expected3)

        c.delete(key1)

        self.assertEquals(len(c), 2)
        self.assertNotIn(key1, c)
        self.assertIn(key2, c)
        self.assertIn(key3, c)

# ################################################################################################################################

    def test_delete_expired(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 0.1)
        c.set(key2, expected2)
        c.set(key3, expected3, 0.03)

        sleep(0.12)

        deleted = c.delete_expired()
        self.assertEquals(sorted(deleted), [key1, key3])

        self.assertEquals(len(c), 1)
        self.assertNotIn(key1, c)
        self.assertIn(key2, c)
        self.assertNotIn(key3, c)

# ################################################################################################################################

    def test_get_deletes_expired_key(self):

        key1, expected1 = 'key1', 'value1'
        key2, expected2 = 'key2', 'value2'
        key3, expected3 = 'key3', 'value3'

        c = Cache()
        c.set(key1, expected1, 0.03)
        c.set(key2, expected2)
        c.set(key3, expected3, 0.05)

        sleep(0.12)

        self.assertRaises(KeyExpiredError, c.get, key1)
        self.assertRaises(KeyExpiredError, c.get, key3)

        self.assertEquals(len(c), 1)
        self.assertNotIn(key1, c)
        self.assertIn(key2, c)
        self.assertNotIn(key3, c)

        # It will be arranged in the same order as .get were called in
        self.assertListEqual(c._expired_on_op, [key1, key3])

        deleted = c.delete_expired()
        self.assertEquals(sorted(deleted), [key1, key3])
        self.assertListEqual(c._expired_on_op, [])

# ################################################################################################################################

if __name__ == '__main__':
    unittest_main()
