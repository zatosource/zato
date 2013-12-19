# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# nose
from nose.tools import eq_

# Zato
from zato.common.test import rand_string
from zato.server.service import Dict
from zato.server.service.reqresp.sio import ValidationException

class SIOTestCase(TestCase):
    def test_dict_no_keys_specified(self):
        d = Dict('d')
        value = {rand_string(): rand_string(), rand_string(): rand_string()}

        ret_value = d.from_json(value)
        eq_(value, ret_value)

    def test_dict_keys_all_exist(self):
        d = Dict('d', 'k1', 'k2')
        value = {'k1':'v1', 'k2':'v2', 'k3':'v3'} # k3 is superfluous and should not be returned

        ret_value = d.from_json(value)
        eq_(sorted(ret_value.items()), [('k1', 'v1'), ('k2', 'v2')])

    def test_dict_keys_missing_no_default_value(self):
        d = Dict('d', 'k1', 'k2', 'k3', 'k4')
        value = {'k1':'v1', 'k2':'v2', 'k3':'v3'} # k4 doesn't exist so an exception should be raised

        try:
            d.from_json(value)
        except ValidationException, e:
            eq_(e.name, 'd')
            eq_(sorted(e.value.items()), [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')])
            eq_(e.missing_elem, 'k4')
        else:
            self.fail('Expected a ValidationException here')

    def test_dict_keys_missing_has_default_value(self):
        default = rand_string()
        d = Dict('d', 'k1', 'k2', 'k3', 'k4', default=default)
        value = {'k1':'v1', 'k2':'v2', 'k3':'v3'} # k4 doesn't exist but no exception is raised because a default value is set

        ret_value = d.from_json(value)
        eq_(sorted(ret_value.items()), [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3'), ('k4', default)])
