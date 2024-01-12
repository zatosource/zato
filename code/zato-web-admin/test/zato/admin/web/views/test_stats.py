# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

from datetime import datetime
from unittest import TestCase
import os

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Django
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
django.setup()

# mock
from mock import patch

# nose
from nose.tools import eq_

# pytz
from pytz import utc

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.models import UserProfile
from zato.admin.web.views.stats import get_default_date, shift
from zato.common.util.api import utcnow

class StatsTestCase(TestCase):
    def setUp(self):
        self.user_profile = UserProfile()
        self.user_profile.timezone = 'Europe/Berlin'
        self.user_profile.date_format_py = 'd-m-Y'
        self.user_profile.time_format_py = 'H:i:s'
        self.user_profile.month_year_format_py = 'm-Y'
        self.user_profile.date_time_format_py = 'd-m-Y H:i:s'

    def _fake_now(self):
        return datetime(2012, 3, 1, 0, 47, 24, 54903, tzinfo=utc) # 1st of March in a leap year

    def _utcnow(self):
        return self._fake_now()

    def _now(self, *ignored):
        return self._fake_now()

class TrendsTestCase(StatsTestCase):
    def test_start_stop_last_hour(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            info = get_default_date('last_hour', self.user_profile, 'date_time')
            eq_(info.utc_start, '2012-02-29T23:47:24.054903+00:00')
            eq_(info.utc_stop, '2012-03-01T00:47:24.054903+00:00')
            eq_(info.user_start, '01-03-2012 00:47:24')
            eq_(info.user_stop, '01-03-2012 01:47:24')
            eq_(info.label, 'Last hour')
            eq_(info.step, 'hour')

    def test_shift_prev_hour(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            now = utcnow()
            info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'last_hour_prev', 'hour', 'date_time')
            eq_(info.utc_start, '2012-02-29T23:47:24.054903+00:00')
            eq_(info.utc_stop, '2012-03-01T00:47:24.054903+00:00')
            eq_(info.user_start, '01-03-2012 00:47:24')
            eq_(info.user_stop, '01-03-2012 01:47:24')
            eq_(info.step, None)

    def test_shift_prev_hour2(self):
        now = parse_datetime('2012-10-30T21:09:02.141791+00:00')
        info = shift(now, '2012-10-30 23:09:02', self.user_profile, 'last_hour_prev', 'hour', 'date_time')
        eq_(info.utc_start, '2012-10-30T20:09:02.141791+00:00')
        eq_(info.utc_stop, '2012-10-30T21:09:02.141791+00:00')
        eq_(info.user_start, '30-10-2012 21:09:02')
        eq_(info.user_stop, '30-10-2012 22:09:02')
        eq_(info.step, None)

    def test_shift_prev_day(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            now = utcnow()
            info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'today_prev_day', 'hour', 'date_time')
            eq_(info.utc_start, '2012-02-29T00:47:24.054903+00:00')
            eq_(info.utc_stop, '2012-02-29T01:47:24.054903+00:00')
            eq_(info.user_start, '29-02-2012 01:47:24')
            eq_(info.user_stop, '29-02-2012 02:47:24')
            eq_(info.step, None)

    def test_shift_prev_week(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            now = utcnow()
            info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'today_prev_day_week', 'hour', 'date_time')
            eq_(info.utc_start, '2012-02-23T00:47:24.054903+00:00')
            eq_(info.utc_stop, '2012-02-23T01:47:24.054903+00:00')
            eq_(info.user_start, '23-02-2012 01:47:24')
            eq_(info.user_stop, '23-02-2012 02:47:24')
            eq_(info.step, None)

class SummaryTestCase(StatsTestCase):
    def test_start_stop_today(self):
        with patch('zato.common.util._now', self._now):
            info = get_default_date('today', self.user_profile, 'date')
            eq_(info.utc_start, '2012-02-29T23:00:00+00:00')
            eq_(info.utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(info.user_start, '01-03-2012')
            eq_(info.user_stop, '')
            eq_(info.label, 'Today')
            eq_(info.step, 'day')

    def test_start_stop_yesterday(self):
        with patch('zato.common.util._now', self._now):
            info = get_default_date('yesterday', self.user_profile, 'date')
            eq_(info.utc_start, '2012-02-28T23:00:00+00:00')
            eq_(info.utc_stop, '2012-02-29T23:00:00+00:00')
            eq_(info.user_start, '29-02-2012')
            eq_(info.user_stop, '')
            eq_(info.label, 'Yesterday')
            eq_(info.step, 'day')

    def test_start_stop_this_week(self):
        with patch('zato.common.util._now', self._now):
            info = get_default_date('this_week', self.user_profile, 'date')
            eq_(info.utc_start, '2012-02-26T23:00:00+00:00')
            eq_(info.utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(info.user_start, '27-02-2012')
            eq_(info.user_stop, '01-03-2012') # The date now() returns
            eq_(info.label, 'This week')
            eq_(info.step, 'week')

    def test_start_stop_this_month(self):
        with patch('zato.common.util._now', self._now):
            info = get_default_date('this_month', self.user_profile, 'month_year')
            eq_(info.utc_start, '2012-02-29T23:00:00+00:00')
            eq_(info.utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(info.user_start, '03-2012')
            eq_(info.user_stop, '')
            eq_(info.label, 'This month')
            eq_(info.step, 'month')

    def test_start_stop_this_year(self):
        with patch('zato.common.util._now', self._now):
            info = get_default_date('this_year', self.user_profile, 'year')
            eq_(info.utc_start, '2011-12-31T23:00:00+00:00')
            eq_(info.utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(info.user_start, '2012')
            eq_(info.user_stop, '')
            eq_(info.label, 'This year')
            eq_(info.step, 'year')

    def test_shift_prev_day_by_day(self):
        now = parse_datetime('2012-03-21T00:39:19+00:00')
        info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'today_prev_day', 'day', 'date')
        eq_(info.utc_start, '2012-03-20T00:39:19+00:00')
        eq_(info.utc_stop, '2012-03-21T00:39:19+00:00')
        eq_(info.user_start, '20-03-2012')
        eq_(info.user_stop, '21-03-2012')
        eq_(info.step, None)

    def test_shift_prev_week_by_day(self):
        now = parse_datetime('2012-03-21T00:39:19+00:00')
        info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'today_prev_day_week', 'day', 'date')
        eq_(info.utc_start, '2012-03-14T00:39:19+00:00')
        eq_(info.utc_stop, '2012-03-15T00:39:19+00:00')
        eq_(info.user_start, '14-03-2012')
        eq_(info.user_stop, '15-03-2012')
        eq_(info.step, None)

    def test_shift_prev_week_by_week(self):
        now = parse_datetime('2012-10-22T00:00:00+00:00')
        info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'today_prev_day_week', 'week', 'date')
        eq_(info.utc_start, '2012-10-15T00:00:00+00:00')
        eq_(info.utc_stop, '2012-10-22T00:00:00+00:00')
        eq_(info.user_start, '15-10-2012')
        eq_(info.user_stop, '22-10-2012')
        eq_(info.step, None)

    def test_shift_prev_month_by_month(self):
        now = parse_datetime('2012-10-01T00:00:00+00:00')
        info = shift(now, from_utc_to_user(now, self.user_profile, 'month_year'), self.user_profile, 'this_month_prev_month', 'month', 'month_year')
        eq_(info.utc_start, '2012-08-31T22:00:00+00:00')
        eq_(info.utc_stop, '2012-09-30T22:00:00+00:00')
        eq_(info.user_start, '09-2012')
        eq_(info.user_stop, '10-2012')
        eq_(info.step, None)

    def test_shift_prev_year_by_year(self):
        now = parse_datetime('2012-01-01T00:00:00+00:00')
        info = shift(now, from_utc_to_user(now, self.user_profile), self.user_profile, 'this_year_prev', 'year', 'year')
        eq_(info.utc_start, '2011-01-01T00:00:00+00:00')
        eq_(info.utc_stop, '2012-01-01T00:00:00+00:00')
        eq_(info.user_start, '2011')
        eq_(info.user_stop, '2012')
        eq_(info.step, None)
