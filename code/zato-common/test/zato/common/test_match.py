# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from unittest import TestCase

# Bunch
from bunch import Bunch

# Zato
from zato.common import FALSE_TRUE, TRUE_FALSE
from zato.common.match import Matcher

default_config = Bunch({
    'order': FALSE_TRUE,
    '*.zxc': True,
    'abc.*': True,
    '*': False,
    'qwe.*.zxc': False,
})

class MatcherTestCase(TestCase):
    def test_read_config(self):

        config = deepcopy(default_config)

        m = Matcher()
        m.read_config(config)

        self.assertEquals(m.config, config)
        self.assertEquals(m.order1, False)
        self.assertEquals(m.order2, True)

        # Note that it's reversed because we match from narrowest
        # to broadest patterns, sorted lexicographically.
        self.assertListEqual(m.items[True], [ 'abc.*', '*.zxc',])
        self.assertListEqual(m.items[False], ['qwe.*.zxc', '*'])

    def test_is_allowed_order_false_true(self):

        config = deepcopy(default_config)

        m = Matcher()
        m.read_config(config)

        # ########################################################################################################################
        #
        # The value of 'aaa.zxc' is allowed because
        # 1) We match from True to False
        # 2) qwe.*.zxc does not match it
        # 3) *         says nothing is allowed
        # 4) *.zxc     says it is allowed overriding bullet #3
        #

        is_allowed = m.is_allowed('aaa.zxc')
        self.assertIs(is_allowed, True)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':True})

        # ########################################################################################################################
        #
        # The value of 'qwe.333.zxc' is also allowed because
        # 1) We match from True to False
        # 2) qwe.*.zxc disallowes it
        # 3) *         says nothing is allowed
        # 4) *.zxc     this one allows it even though #1 and #2 said no
        #

        is_allowed = m.is_allowed('qwe.333.zxc')
        self.assertIs(is_allowed, True)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':True, 'qwe.333.zxc':True})

        # ########################################################################################################################
        #
        # The value of 'qwe.444.aaa' is not allowed
        # 1) We match from True to False
        # 2) qwe.*.zxc does not match it at all
        # 3) *         says nothing is allowed
        # 4) *.zxc     does not match it at all so the last match of #2 is taken into account

        is_allowed = m.is_allowed('qwe.444.aaa')
        self.assertIs(is_allowed, False)
        self.assertDictEqual(m.is_allowed_cache, {'aaa.zxc':True, 'qwe.333.zxc':True, 'qwe.444.aaa': False})

    def test_is_allowed_no_match(self):

        # No entries at all - we disallow everything in that case
        config = Bunch({'order': FALSE_TRUE})

        m = Matcher()
        m.read_config(config)

        is_allowed = m.is_allowed('abc')
        self.assertIs(is_allowed, False)
        self.assertDictEqual(m.is_allowed_cache, {'abc':False})

    def test_is_allowed_no_order(self):

        # Default order will be FALSE_TRUE
        config = Bunch({'abc':True})

        m = Matcher()
        m.read_config(config)

        self.assertEquals(m.order1, False)
        self.assertEquals(m.order2, True)
