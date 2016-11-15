# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps
from unittest import TestCase

# Zato
from zato.server.live_browser import match_pattern

# ################################################################################################################################

class PatternMatcherTestCase(TestCase):

    def test_simple(self):

        pattern = set(['aaa', '111', '333'])
        text = dumps({
            'aaa':'111',
            'bbb':222,
            'ccc':'333'
        })
        self.assertTrue(match_pattern(text, pattern))

# ################################################################################################################################

    def test_punctuation_simple(self):

        pattern = set(['aaa', '111', '333'])
        text = dumps({
            'aaa:aaa':'111---qqq',
            'bbb&&&&bbb@@@@zzz':222,
            'ccc':'333'
        })
        self.assertTrue(match_pattern(text, pattern))

# ################################################################################################################################

    def test_punctuation_hyphens(self):

        pattern = set(['aaa', '111', '333-ggg', '111-qqq'])
        text = dumps({
            'aaa:aaa':'111-qqq',
            'bbb&&&&bbb@@@@zzz':111,
            'ccc':'333-ggg'
        })
        self.assertTrue(match_pattern(text, pattern))

# ################################################################################################################################

    def test_xml(self):

        pattern = set(['aaa', '111', '333-ggg', '111-qqq'])
        text = """<?xml version="1.0"?>
        <aaa>
          <ggg>111</ggg>
          <qqq attr="333-ggg"/>
          <ccc>111-qqq</ccc>
        </aaa>
        """
        self.assertTrue(match_pattern(text, pattern))

# ################################################################################################################################
