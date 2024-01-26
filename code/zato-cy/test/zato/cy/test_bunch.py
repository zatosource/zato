# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy
from datetime import datetime
from json import load
from unittest import TestCase

# Bunch
import bunch as _orig_bunch

# Zato
from zato import bunch

curdir = os.path.dirname(os.path.abspath(__file__))

class BunchTestCase(TestCase):

    def setUp(self):
        sample_path = os.path.join(curdir, 'sample.json')
        self._sample_dict = load(open(sample_path))

    def _check_bunch(self, impl, test_data, iters):
        start = datetime.utcnow()
        for _x in range(100):
            impl(test_data)
        return datetime.utcnow() - start

    def test_perf(self):
        test_data = {}
        for x in range(100):
            test_data[x] = deepcopy(self._sample_dict)
            test_data[str(x*2)] = deepcopy(self._sample_dict)
            test_data[(x, x+1, x*2)] = deepcopy(self._sample_dict)
            test_data[(x, x-1, x*3)] = [deepcopy(self._sample_dict)]

        orig_taken = self._check_bunch(_orig_bunch.bunchify, test_data, 10)
        zato_taken = self._check_bunch(bunch.bunchify, test_data, 10)
        self.assertLess(zato_taken, orig_taken)

    def test_bunchify(self):
        test_data = {
            'foo': 'bar',
            123: 456,
            True: False,
            False: True,
            10.0: [1, 2, 3, 'a', 'b', 'c'],
            ('aa', 'bb'): ('cc', 'dd'),
            'qqq': {'zz': {'yy': ([{11:22, 'uu':'44'}, 90, 18.0, 'qwerty'], 'zxc', 89)}}
        }

        bunch.bunchify(test_data)

    def test_set_get(self):
        value = '123'
        b = bunch.Bunch()
        b.a = value

        self.assertEqual(b.a, value)
        self.assertEqual(b['a'], value)
