# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# nose
from nose.tools import eq_

# live test case
from . import LiveTestCase

TEST_SERVICE = 'zato-test-timeout-live.invoke-slow-service'

class TimeoutLiveTestCase(LiveTestCase):

    SERVICES_SOURCE = 'zato_test_timeout_live.py'

    def test_no_timeout(self):
        if not self.should_run:
            return
        response = self.invoke_asi(TEST_SERVICE)['response']
        eq_(response['result'], 'SUCCESS')

    def test_long_timeout(self):
        if not self.should_run:
            return
        request = {'timeout':3}
        response = self.invoke_asi(TEST_SERVICE, request)['response']
        eq_(response['result'], 'SUCCESS')

    def test_short_timeout_no_raise(self):
        if not self.should_run:
            return
        request = {'timeout':1}
        response = self.invoke_asi(TEST_SERVICE, request)['response']
        eq_(response['result'], 'TIMEOUT')

    def test_short_timeout_raise_true(self):
        if not self.should_run:
            return
        request = {'timeout':1, 'raise_timeout':True}
        response = self.invoke_asi(TEST_SERVICE, request)['response']
        eq_(response['result'], 'TIMEOUT')

    def test_short_timeout_raise_false(self):
        if not self.should_run:
            return
        request = {'timeout':1, 'raise_timeout':False}
        response = self.invoke_asi(TEST_SERVICE, request)['response']
        eq_(response['result'], None)
