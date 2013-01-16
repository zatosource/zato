# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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
import logging

# dateutil
from dateutil.relativedelta import relativedelta

# Django
from django.template.defaultfilters import date as django_date_filter

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.admin.settings import TECH_ACCOUNT_NAME, TECH_ACCOUNT_PASSWORD
from zato.common import zato_namespace
from zato.common.soap import invoke_admin_service as _invoke_admin_service
from zato.common.util import from_local_to_utc as _from_local_to_utc, from_utc_to_local as _from_utc_to_local

logger = logging.getLogger(__name__)

class _Format(object):
    def __init__(self, frontend, python):
        self.frontend = frontend
        self.python = python

DATE_FORMATS = {
    'dd/mm/yyyy': 'd/m/Y',
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
    'dd/mm/yyyy': 'm/Y',
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

def invoke_admin_service(cluster, soap_action, input_dict):
    """ A thin wrapper around zato.common.soap.invoke_admin_service that adds
    Django session-related information to the request headers.
    """
    zato_message = Element(soap_action.replace(':', '_').replace('.', '_').replace('-', '_') + '_request')
    
    for k, v in input_dict.items():
        setattr(zato_message, k, v)

    headers = {'x-zato-session-type':'zato-admin/tech_acc', 
               'x-zato-user': TECH_ACCOUNT_NAME,
               'x-zato-password': TECH_ACCOUNT_PASSWORD
               }

    request = etree.tostring(zato_message)
    zato_message, soap_response = _invoke_admin_service(cluster, soap_action, request, headers)
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Request:[{}], response:[{}]'.format(request, soap_response))
        
    return zato_message, soap_response

def last_hour_start_stop(now):
    """ Returns a ISO-8601 formatted pair of start/stop timestamps representing
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
