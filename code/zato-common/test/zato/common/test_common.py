# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Nose
from nose.tools import eq_

# Zato
from zato.common.api import soapenv11_namespace, soapenv12_namespace, StatsElem

class StatsElemTestCase(TestCase):
    def test_from_json(self):
        item = {
            'usage_perc_all_services': 1.22, 'all_services_time': 4360,
            'time_perc_all_services': 17.64,
            'mean_trend': '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,769,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0',
            'min_resp_time': 769.0, 'service_name': 'zato.stats.summary.create-summary-by-year',
            'max_resp_time': 769.0, 'rate': 0.0, 'mean_all_services': '63',
            'all_services_usage': 82, 'time': 769.0, 'usage': 1,
            'usage_trend': '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0',
            'mean': 12.61
        }

        stats_elem = StatsElem.from_json(item)

        for k, v in item.items():
            value = getattr(stats_elem, k)
            eq_(v, value)

class TestSOAPNamespace(TestCase):
    def test_soap_ns(self):
        self.assertEqual(soapenv11_namespace, 'http://schemas.xmlsoap.org/soap/envelope/')
        self.assertEqual(soapenv12_namespace, 'http://www.w3.org/2003/05/soap-envelope')
