# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.test import enrich_with_static_config
from zato.server.service.internal.notif.cloud.openstack.swift import RunNotifier

class SwiftTestCase(TestCase):
    def test_name_matches(self):

        enrich_with_static_config(RunNotifier)
        service = RunNotifier()

        test_data = (
            ('**', 'abc', False, True),
            ('**', 'abc', True, False),

            ('a**', 'abc', False, True),
            ('a**', 'abc', True, False),

            ('a*', 'abc/def', False, False),
            ('a*', 'abc/def', True, True),

            ('a*/*', 'abc/def', False, True),
            ('a*/*', 'abc/def', True, False),

            ('a*/d?f', 'abc/def', False, True),
            ('a*/d?f', 'abc/def', True, False),

            ('a*\\\*', r'abc\def', False, True),
            ('a*\\\*', r'abc\def', True, False),

        )

        for pattern, string, negate, expected in test_data:
            result = service._name_matches(pattern, string, negate)
            self.assertEquals(result, expected, '`{}` != `{}`, {} {} {}'.format(result, expected, pattern, string, negate))
