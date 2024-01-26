# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# dateutil
from dateutil.relativedelta import relativedelta

# Django
from django.template.defaultfilters import date as django_date_filter

# Zato
from zato.common.api import INVOCATION_TARGET
from zato.common.util.api import from_local_to_utc as _from_local_to_utc, from_utc_to_local as _from_utc_to_local

logger = logging.getLogger(__name__)

class _Format:
    def __init__(self, frontend, python):
        self.frontend = frontend
        self.python = python

DATE_FORMATS = {
    'dd/mm/yyyy': 'd/m/Y',
    'dd/mm/yy': 'd/m/y',
    'dd-mm-yyyy': 'd-m-Y',
    'dd.mm.yyyy': 'd.m.Y',
    'dd.mm.yy': 'd.m.y',
    'mm-dd-yy': 'm-d-y',
    'mm-dd-yyyy': 'm-d-Y',
    'yyyy/mm/dd': 'Y/m/d',
    'yyyy-mm-dd': 'Y-m-d',
    'yyyy.mm.dd': 'Y.m.d',
}

MONTH_YEAR_FORMATS = {
    'dd/mm/yyyy': 'm/y',
    'dd/mm/yy': 'm/Y',
    'dd-mm-yyyy': 'm-Y',
    'dd.mm.yyyy': 'm.Y',
    'dd.mm.yy': 'm.y',
    'mm-dd-yy': 'm-y',
    'mm-dd-yyyy': 'm-Y',
    'yyyy/mm/dd': 'Y/m',
    'yyyy-mm-dd': 'Y-m',
    'yyyy.mm.dd': 'Y.m',
}

TIME_FORMATS = {
    '12': 'g:i.s A',
    '24': 'H:i:s',
}

TARGET_TYPE_HUMAN = {
    INVOCATION_TARGET.CHANNEL_AMQP: 'AMQP channel',
    INVOCATION_TARGET.CHANNEL_WMQ: 'IBM MQ channel',
    INVOCATION_TARGET.CHANNEL_ZMQ: 'ZeroMQ channel',
    INVOCATION_TARGET.OUTCONN_AMQP: 'AMQP outgoing connection',
    INVOCATION_TARGET.OUTCONN_WMQ: 'IBM MQ outgoing connection',
    INVOCATION_TARGET.OUTCONN_ZMQ: 'ZeroMQ outgoing connection',
    INVOCATION_TARGET.SERVICE: 'Service',
}

def last_hour_start_stop(now):
    """ Returns an ISO-8601 formatted pair of start/stop timestamps representing
    now-1 hour and now.
    """
    return (now + relativedelta(minutes=-60)).isoformat(), now.isoformat()

def from_utc_to_user(dt, user_profile, format='date_time'):
    """ Converts a datetime object from UTC to a user-selected timezone and datetime format.
    """
    return django_date_filter(
        _from_utc_to_local(dt, user_profile.timezone), getattr(user_profile, '{}_format_py'.format(format)))

def from_user_to_utc(dt, user_profile, format='date_time'):
    """ Converts a datetime object from a user-selected timezone to UTC.
    """
    # The underlying parser gets confused by stuff like '15.08.12 9:56.59 PM',
    # that is, where the seconds separator (.) is different from what separates hours from minutes,
    # so we need replace the dot with semicolon in order to make the parser happy.
    if user_profile.time_format == '12':
        # Reverse the string, replace the first occurence of . with a : and reverse it back
        dt = dt[::-1].replace('.', ':', 1)[::-1]

    if format == 'year':
        dt = '01-01-' + dt

    dt_format = getattr(user_profile, '{}_format_py'.format(format))
    return _from_local_to_utc(dt, user_profile.timezone, dt_format.startswith('d')).replace(tzinfo=None)
