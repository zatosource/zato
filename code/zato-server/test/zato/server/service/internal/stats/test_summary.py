# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# dateutil
from dateutil.parser import parse

# nose
from nose.tools import eq_

# Zato
from zato.common.test import ServiceTestCase
from zato.server.service.internal.stats.summary import GetSummaryByRange

class GetSummaryByRangeTestCase(ServiceTestCase):
    
    def test_get_slice_period_type(self):
        
        service = GetSummaryByRange()

        def _check_expected(orig_start, orig_stop, by_mins, by_hours_mins, by_days_hours_mins, by_months_days_hours_mins):
            start = parse(orig_start)
            stop = parse(orig_stop)
            
            delta, result = service._get_slice_period_type(start, stop, orig_start, orig_stop)
            
            expected = {
                'by_mins': by_mins,
                'by_hours_mins': by_hours_mins,
                'by_days_hours_mins': by_days_hours_mins,
                'by_months_days_hours_mins': by_months_days_hours_mins,
                }
            for k, v in expected.items():
                eq_(result[k], v, 'start:[{}], stop:[{}], result:[{}], k:[{}], values:[{}], delta:[{}]'.format(
                    start, stop, result, k, str((by_mins, by_hours_mins, by_days_hours_mins, by_months_days_hours_mins)),
                str((delta))))
        
        # Minutes only 1)
        start = '2012-10-14T23:56:49'
        stop = '2012-10-15T00:56:49'
        _check_expected(start, stop, True, False, False, False)
        
        # Minutes only 2)
        start = '2007-01-18T19:18:11'
        stop = '2007-01-18T19:38:19'
        _check_expected(start, stop, True, False, False, False)

        # Hours and minutes 1)
        start = '2012-10-14T22:56:49'
        stop = '2012-10-15T00:56:49'
        _check_expected(start, stop, False, True, False, False)
        
        # Hours and minutes 2)
        start = '2009-03-21T03:19:11'
        stop = '2009-03-21T17:32:39'
        _check_expected(start, stop, False, True, False, False)
        
        # Days, hours and minutes 1)
        start = '2012-10-13T22:56:49'
        stop = '2012-10-15T00:56:49'
        _check_expected(start, stop, False, False, True, False)
        
        # Days, hours and minutes 2) (leap year)
        start = '2012-02-28T23:56:49'
        stop = '2012-03-01T00:01:12'
        _check_expected(start, stop, False, False, True, False)

        # Months, days, hours and minutes 1)
        start = '2010-10-13T22:56:49'
        stop = '2012-10-15T00:56:49'
        _check_expected(start, stop, False, False, False, True)
        
        # Months, days, hours and minutes 2)
        start = '208-08-11T18:01:34'
        stop = '2012-11-23T03:42:15'
        _check_expected(start, stop, False, False, False, True)
