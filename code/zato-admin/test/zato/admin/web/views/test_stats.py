# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from datetime import datetime
from random import choice, randint
from unittest import TestCase
from uuid import uuid4

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import MO, relativedelta

# mock
from mock import patch

# nose
from nose.tools import eq_

# pytz
from pytz import timezone, utc

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.models import UserProfile
from zato.common.util import from_local_to_utc, now, utcnow

SHIFT_TYPES = 'prev_hour', 'prev_day', 'prev_week'

def shift(base_date, user_profile, shift_type, duration, format):
    if shift_type not in SHIFT_TYPES:
        raise ValueError('Unknown shift_type:[{}]'.format(shift_type))
    
    def get_delta_kwargs(shift_type, duration):
        """ Returns keyword args passed into relativedelta for both start and
        stop dates. The former is a delta relative to the base_date, the latter
        is relative to the resulting start_date.
        """
        if shift_type == 'prev_hour':
            start_kwargs = {'hours':-1}
        elif shift_type == 'prev_day':
            start_kwargs = {'days':-1}
        elif shift_type == 'prev_week':
            start_kwargs = {'weeks':-1}
        else:
            raise ValueError('Unrecognized shift_type:[{}]'.format(shift_type))
        
        if duration == 'hour':
            stop_kwargs = {'hours':1}
        elif duration == 'day':
            stop_kwargs = {'days':1}
            
        return start_kwargs, stop_kwargs
    
    start_delta_kwargs, stop_delta_kwargs = get_delta_kwargs(shift_type, duration)
    utc_base_date = utc.fromutc(from_user_to_utc(base_date, user_profile, format))
    
    utc_start = utc_base_date + relativedelta(**start_delta_kwargs)
    utc_stop = utc_start + relativedelta(**stop_delta_kwargs)
    
    user_start = from_utc_to_user(utc_start, user_profile, format)
    user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
    return utc_start.isoformat(), utc_stop.isoformat(), user_start, user_stop

def get_date_data(stats_type, date_type, user_profile, format):


    def get_today(_user_profile, _format):
        """ user_start is today's midnight but it needs to be in user's TZ. user_stop is current time simply,
        in user's timezone again.
        """
        user_now = now(timezone(_user_profile.timezone)).replace(tzinfo=None)
        user_today_midnight = datetime(user_now.year, user_now.month, user_now.day)
        
        utc_start = from_local_to_utc(user_today_midnight, _user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, _user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, _user_profile, _format)
        user_stop = from_utc_to_user(utc_stop, _user_profile, _format)
        
        return utc_start, utc_stop, user_start, user_stop
    
    if date_type == 'last_hour':
        # stop is what current time is now so return it in UTC and user's TZ
        # along with start which will be equal to stop - 1 hour.
        utc_stop = utc.fromutc(utcnow())
        utc_start = utc.fromutc(utc_stop + relativedelta(hours=-1))
        
        user_start = from_utc_to_user(utc_start, user_profile)
        user_stop = from_utc_to_user(utc_stop, user_profile)
        
        label = 'one hour'
        
    elif date_type == 'today':
        utc_start, utc_stop, user_start, user_stop = get_today(user_profile, format)
        label = 'today'
    
    elif date_type == 'yesterday':
        # Yesterday's start is today's start - 1 day
        today_utc_start, today_utc_stop, today_user_start, today_user_stop = get_today(user_profile, format)
        
        utc_start = today_utc_start + relativedelta(days=-1)
        utc_stop = utc_start + relativedelta(days=1)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
        label = 'yesterday'
        
    elif date_type == 'this_week':
        # This week extends from Monday midnight to right now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_prev_monday = user_now + relativedelta(weekday=MO(-1))
        user_prev_monday = datetime(year=user_prev_monday.year, month=user_prev_monday.month, day=user_prev_monday.day)
        
        utc_start = from_local_to_utc(user_prev_monday, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
        label = 'this week'
        
    elif date_type == 'this_month':
        # From midnight the first day of month up until now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_1st_of_month = datetime(year=user_now.year, month=user_now.month, day=1)
        
        utc_start = from_local_to_utc(user_1st_of_month, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
        label = 'this month'
        
    elif date_type == 'this_year':
        # From midnight the first day of year up until now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_new_year = datetime(year=user_now.year, month=1, day=1)
        
        utc_start = from_local_to_utc(user_new_year, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
        label = 'this year'
    
    else:
        raise ValueError('Unrecognized date_type:[{}]'.format(date_type))
    
    return utc_start.isoformat(), utc_stop.isoformat(), user_start, user_stop, label

class StatsTestCase(TestCase):
    def setUp(self):
        self.user_profile = UserProfile()
        self.user_profile.timezone = 'Europe/Berlin'
        self.user_profile.date_format_py = 'd-m-Y'
        self.user_profile.time_format_py = 'H:i:s'
        self.user_profile.month_year_format_py = 'm-Y'
        self.user_profile.date_time_format_py = 'd-m-Y H:i:s'
        
    def _fake_now(self):
        return datetime(2012, 3, 1, 0, 47, 24, 54903) # 1st of March in a leap year
        
    def _utcnow(self):
        return self._fake_now()
    
    def _now(self, *ignored):
        return self._fake_now()

class TrendsTestCase(StatsTestCase):
    def test_start_stop_last_hour(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            utc_start, utc_stop, user_start, user_stop, label = get_date_data('trends', 'last_hour', self.user_profile, 'date_time')
            eq_(utc_start, '2012-02-29T23:47:24.054903+00:00')
            eq_(utc_stop, '2012-03-01T00:47:24.054903+00:00')
            eq_(user_start, '01-03-2012 00:47:24')
            eq_(user_stop, '01-03-2012 01:47:24')
            eq_(label, 'one hour')
            
    def test_shift_prev_hour(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            now = utcnow()
            utc_start, utc_stop, user_start, user_stop = shift(now, self.user_profile, 'prev_hour', 'hour', 'date_time')
            eq_(utc_start, '2012-02-29T22:47:24.054903+00:00')
            eq_(utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(user_start, '29-02-2012 23:47:24')
            eq_(user_stop, '01-03-2012 00:47:24')
            
    def test_shift_prev_day(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            now = utcnow()
            utc_start, utc_stop, user_start, user_stop = shift(now, self.user_profile, 'prev_day', 'hour', 'date_time')
            eq_(utc_start, '2012-02-28T23:47:24.054903+00:00')
            eq_(utc_stop, '2012-02-29T00:47:24.054903+00:00')
            eq_(user_start, '29-02-2012 00:47:24')
            eq_(user_stop, '29-02-2012 01:47:24')
            
    def test_shift_prev_week(self):
        with patch('zato.common.util._utcnow', self._utcnow):
            now = utcnow()
            utc_start, utc_stop, user_start, user_stop = shift(now, self.user_profile, 'prev_week', 'hour', 'date_time')
            eq_(utc_start, '2012-02-22T23:47:24.054903+00:00')
            eq_(utc_stop, '2012-02-23T00:47:24.054903+00:00')
            eq_(user_start, '23-02-2012 00:47:24')
            eq_(user_stop, '23-02-2012 01:47:24')

class SummaryTestCase(StatsTestCase):
    def test_start_stop_today(self):
        with patch('zato.common.util._now', self._now):
            utc_start, utc_stop, user_start, user_stop, label = get_date_data('summary', 'today', self.user_profile, 'date')
            eq_(utc_start, '2012-02-29T23:00:00+00:00')
            eq_(utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(user_start, '01-03-2012')
            eq_(user_stop, '01-03-2012')
            eq_(label, 'today')
            
    def test_start_stop_yesterday(self):
        with patch('zato.common.util._now', self._now):
            utc_start, utc_stop, user_start, user_stop, label = get_date_data('summary', 'yesterday', self.user_profile, 'date')
            eq_(utc_start, '2012-02-28T23:00:00+00:00')
            eq_(utc_stop, '2012-02-29T23:00:00+00:00')
            eq_(user_start, '29-02-2012')
            eq_(user_stop, '01-03-2012')
            eq_(label, 'yesterday')
            
    def test_start_stop_this_week(self):
        with patch('zato.common.util._now', self._now):
            utc_start, utc_stop, user_start, user_stop, label = get_date_data('summary', 'this_week', self.user_profile, 'date')
            eq_(utc_start, '2012-02-26T23:00:00+00:00')
            eq_(utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(user_start, '27-02-2012')
            eq_(user_stop, '01-03-2012')
            eq_(label, 'this week')
            
    def test_start_stop_this_month(self):
        with patch('zato.common.util._now', self._now):
            utc_start, utc_stop, user_start, user_stop, label = get_date_data('summary', 'this_month', self.user_profile, 'date')
            eq_(utc_start, '2012-02-29T23:00:00+00:00')
            eq_(utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(user_start, '01-03-2012')
            eq_(user_stop, '01-03-2012')
            eq_(label, 'this month')
            
    def test_start_stop_this_year(self):
        with patch('zato.common.util._now', self._now):
            utc_start, utc_stop, user_start, user_stop, label = get_date_data('summary', 'this_year', self.user_profile, 'date')
            eq_(utc_start, '2011-12-31T23:00:00+00:00')
            eq_(utc_stop, '2012-02-29T23:47:24.054903+00:00')
            eq_(user_start, '01-01-2012')
            eq_(user_stop, '01-03-2012')
            eq_(label, 'this year')
            
    def test_shift_prev_day(self):
        now = '01-03-2012'
        utc_start, utc_stop, user_start, user_stop = shift(now, self.user_profile, 'prev_day', 'day', 'date')
        eq_(utc_start, '2012-02-28T23:00:00+00:00')
        eq_(utc_stop, '2012-02-29T23:00:00+00:00')
        eq_(user_start, '29-02-2012')
        eq_(user_stop, '01-03-2012')
        
    def test_shift_prev_week(self):
        now = '01-03-2012'
        utc_start, utc_stop, user_start, user_stop = shift(now, self.user_profile, 'prev_week', 'day', 'date')
        eq_(utc_start, '2012-02-22T23:00:00+00:00')
        eq_(utc_stop, '2012-02-23T23:00:00+00:00')
        eq_(user_start, '23-02-2012')
        eq_(user_stop, '24-02-2012')
