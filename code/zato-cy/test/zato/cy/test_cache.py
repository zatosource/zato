# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from unittest import main as unittest_main, TestCase
from uuid import uuid4

# Zato
sys.path.insert(0, '.')
from cache import Cache

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
        self.assertEquals(returned1['value'], expected1)
        self.assertEquals(returned1['position'], 2)
        self.assertLess(returned1['last_read'], now)
        self.assertLess(returned1['last_write'], now)
        self.assertLess(returned1['prev_read'], now)
        self.assertLess(returned1['prev_write'], now)

        
        returned2 = c.get(key2, True)
        self.assertEquals(returned2['value'], expected2)
        self.assertEquals(returned2['position'], 2)
        self.assertLess(returned2['last_read'], now)
        self.assertLess(returned2['last_write'], now)
        self.assertLess(returned2['prev_read'], now)
        self.assertLess(returned2['prev_write'], now)

        returned3 = c.get(key3, True)
        self.assertEquals(returned3['value'], expected3)
        self.assertEquals(returned3['position'], 2)
        self.assertLess(returned3['last_read'], now)
        self.assertLess(returned3['last_write'], now)
        self.assertLess(returned3['prev_read'], now)
        self.assertLess(returned3['prev_write'], now)

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
        c.get(uuid4().hex)

        self.assertEquals(len(c.hits_per_position), 2)
        self.assertEquals(c.hits_per_position[0], 6)
        self.assertEquals(c.hits_per_position[1], 1)

# ################################################################################################################################

if __name__ == '__main__':
    unittest_main()
