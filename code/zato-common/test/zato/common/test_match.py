# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from unittest import TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import FALSE_TRUE, TRUE_FALSE
from zato.common.match import Matcher

default_config = Bunch({
    'order': FALSE_TRUE,
    '*.zxc': True,
    'abc.*': True,
    '*': False,
    'qwe.*.zxc': False,
})

# ################################################################################################################################

class MatcherTestCase(TestCase):

# ################################################################################################################################

    def test_read_config(self):

        m = Matcher()
        m.read_config(default_config)

        self.assertEqual(m.config, default_config)
        self.assertEqual(m.order1, False)
        self.assertEqual(m.order2, True)
        self.assertIsNone(m.special_case)

        # Note that it's reversed because we match from narrowest
        # to broadest patterns, sorted lexicographically.
        self.assertListEqual(m.items[True], ['abc.*', '*.zxc',])
        self.assertListEqual(m.items[False], ['qwe.*.zxc', '*'])

# ################################################################################################################################

    def test_is_allowed_order_false_true(self):

        m = Matcher()
        m.read_config(default_config)

        self.assertEqual(m.config, default_config)
        self.assertEqual(m.order1, False)
        self.assertEqual(m.order2, True)
        self.assertIsNone(m.special_case)

        # ###########################################################################################
        #
        # The value of 'aaa.zxc' is allowed because
        # 1) We match from False to True
        # 2) qwe.*.zxc does not match it
        # 3) *         says nothing is allowed
        # 4) *.zxc     says it is allowed overriding bullet #3
        #

        is_allowed = m.is_allowed('aaa.zxc')
        self.assertIs(is_allowed, True)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':True})

        # ###########################################################################################
        #
        # The value of 'qwe.333.zxc' is also allowed because
        # 1) We match from False to True
        # 2) qwe.*.zxc disallowes it
        # 3) *         says nothing is allowed
        # 4) *.zxc     this one allows it even though #1 and #2 said no
        #

        is_allowed = m.is_allowed('qwe.333.zxc')
        self.assertIs(is_allowed, True)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':True, 'qwe.333.zxc':True})

        # ###########################################################################################
        #
        # The value of 'qwe.444.aaa' is not allowed
        # 1) We match from False to True
        # 2) qwe.*.zxc does not match it at all
        # 3) *         says nothing is allowed
        # 4) *.zxc     does not match it at all so the last match of #2 is taken into account

        is_allowed = m.is_allowed('qwe.444.aaa')
        self.assertIs(is_allowed, False)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':True, 'qwe.333.zxc':True, 'qwe.444.aaa': False})

# ################################################################################################################################

    def test_is_allowed_order_true_false(self):

        config = deepcopy(default_config)
        config.order = TRUE_FALSE

        m = Matcher()
        m.read_config(config)

        self.assertEqual(m.config, config)
        self.assertEqual(m.order1, True)
        self.assertEqual(m.order2, False)
        self.assertIsNone(m.special_case)

        # ###########################################################################################
        #
        # The value of 'aaa.zxc' is not allowed because
        # 1) We match from True to False
        # 2) *.zxc     says it is allowed
        # 3) qwe.*.zxc matches it and says it's not allowed
        # 4) *         matches again and confirms it's not allowed
        #

        is_allowed = m.is_allowed('aaa.zxc')
        self.assertIs(is_allowed, False)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':False})

        # ###########################################################################################
        #
        # The value of 'qwe.333.zxc' is also not allowed because
        # 1) We match from True to False
        # 2) *.zxc     says it is allowed
        # 3) qwe.*.zxc matches it and says it's not allowed
        # 4) *         matches again and confirms it's not allowed
        #

        is_allowed = m.is_allowed('qwe.333.zxc')
        self.assertIs(is_allowed, False)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':False, 'qwe.333.zxc':False})

        # ###########################################################################################

        config2 = deepcopy(default_config)
        del config2['*']
        config2['*.aaa'] = True
        config2.order = TRUE_FALSE

        m2 = Matcher()
        m2.read_config(config2)

        self.assertEqual(m2.config, config2)
        self.assertEqual(m2.order1, True)
        self.assertEqual(m2.order2, False)

        # ###########################################################################################
        #
        # The value of 'qwe.444.aaa' is allowed
        # 1) We match from True to False
        # 2) *.aaa     matches and allows it
        # 3) *.zxc     does not match
        # 4) abc.*     does not match
        # 5) qwe.*zxc  does not match
        #

        is_allowed = m2.is_allowed('qwe.444.aaa')
        self.assertIs(is_allowed, True)
        self.assertDictEqual(m2.is_allowed_cache, {'qwe.444.aaa':True})

# ################################################################################################################################

    def test_is_allowed_true_only_has_order(self):
        config = Bunch({'order':FALSE_TRUE, 'abc':True, 'zxc':True})

        m = Matcher()
        m.read_config(config)
        self.assertIsNone(m.special_case)

        self.assertTrue(m.is_allowed('abc'))
        self.assertTrue(m.is_allowed('zxc'))

        self.assertFalse(m.is_allowed('111'))
        self.assertFalse(m.is_allowed('222'))

        self.assertDictEqual(m.is_allowed_cache, {'abc':True, 'zxc':True, '111':False, '222':False})

# ################################################################################################################################

    def test_is_allowed_false_only_has_order(self):
        config = Bunch({'order':FALSE_TRUE, 'abc':False, 'zxc':False})

        m = Matcher()
        m.read_config(config)
        self.assertIsNone(m.special_case)

        self.assertFalse(m.is_allowed('abc'))
        self.assertFalse(m.is_allowed('zxc'))

        self.assertFalse(m.is_allowed('111'))
        self.assertFalse(m.is_allowed('222'))

        self.assertDictEqual(m.is_allowed_cache, {'abc':False, 'zxc':False, '111':False, '222':False})

# ################################################################################################################################

    def test_is_allowed_true_only_no_order(self):
        config = Bunch({'abc':True, 'zxc':True})

        m = Matcher()
        m.read_config(config)
        self.assertIsNone(m.special_case)

        self.assertTrue(m.is_allowed('abc'))
        self.assertTrue(m.is_allowed('zxc'))

        self.assertFalse(m.is_allowed('111'))
        self.assertFalse(m.is_allowed('222'))

        self.assertDictEqual(m.is_allowed_cache, {'abc':True, 'zxc':True, '111':False, '222':False})

# ################################################################################################################################

    def test_is_allowed_false_only_no_order(self):
        config = Bunch({'abc':False, 'zxc':False})

        m = Matcher()
        m.read_config(config)
        self.assertIsNone(m.special_case)

        self.assertFalse(m.is_allowed('abc'))
        self.assertFalse(m.is_allowed('zxc'))

        self.assertFalse(m.is_allowed('111'))
        self.assertFalse(m.is_allowed('222'))

        self.assertDictEqual(m.is_allowed_cache, {'abc':False, 'zxc':False, '111':False, '222':False})

# ################################################################################################################################

    def test_is_allowed_no_match(self):

        # No entries at all - we disallow everything in that case
        config = Bunch({'order': FALSE_TRUE})

        m = Matcher()
        m.read_config(config)
        self.assertIsNone(m.special_case)

        self.assertEqual(m.config, config)
        self.assertEqual(m.order1, False)
        self.assertEqual(m.order2, True)

        is_allowed = m.is_allowed('abc')
        self.assertIs(is_allowed, False)
        self.assertDictEqual(m.is_allowed_cache, {'abc':False})

# ################################################################################################################################

    def test_is_allowed_no_order(self):

        # Default order will be FALSE_TRUE
        config = Bunch({'abc':True})

        m = Matcher()
        m.read_config(config)
        self.assertIsNone(m.special_case)

        self.assertEqual(m.config, config)
        self.assertEqual(m.order1, False)
        self.assertEqual(m.order2, True)

# ################################################################################################################################

    def test_is_allowed_cache_is_used(self):

        class FakeCache:
            def __init__(self):
                self.impl = {}
                self.getitem_used = 0
                self.setitem_used = 0

            def __setitem__(self, key, value):
                self.setitem_used += 1
                self.impl[key] = value

            def __getitem__(self, key):
                self.getitem_used += 1
                return self.impl[key]

        m = Matcher()
        m.is_allowed_cache = FakeCache()
        m.read_config(default_config)
        self.assertIsNone(m.special_case)

        self.assertEqual(m.config, default_config)
        self.assertEqual(m.order1, False)
        self.assertEqual(m.order2, True)

        m.is_allowed('aaa.zxc')
        m.is_allowed('aaa.zxc')
        m.is_allowed('aaa.zxc')

        self.assertEqual(m.is_allowed_cache.setitem_used, 1)
        self.assertEqual(m.is_allowed_cache.getitem_used, 3) # It is 3 because the first time we attempted to return the key

    def test_is_allowed_special_case(self):

        # ##################################################################################

        config = Bunch({'order':TRUE_FALSE, '*':False})

        m = Matcher()
        m.read_config(config)
        self.assertIs(m.special_case, False)

        m.is_allowed('aaa.zxc')
        self.assertEqual(m.is_allowed_cache, {})

        # ##################################################################################

        config = Bunch({'order':TRUE_FALSE, '*':True})

        m = Matcher()
        m.read_config(config)
        self.assertIs(m.special_case, True)

        m.is_allowed('aaa.zxc')
        self.assertEqual(m.is_allowed_cache, {})

# ################################################################################################################################
