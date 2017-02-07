# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Arrow
import arrow

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class TimeUtil(object):
    """ A thin layer around Arrow's date/time handling library customized for our needs.
    Default format is always taken from ISO 8601 (so it's sorted lexicographically)
    and default timezone is always UTC.
    """
    def __init__(self, kvdb):
        self.kvdb = kvdb

    def get_format_from_kvdb(self, format):
        """ Returns format stored under a key pointed to by 'format' or raises
        ValueError if the key is missing/has no value.
        """
        key = 'kvdb:date-format:{}'.format(format[5:])
        format = self.kvdb.conn.get(key)
        if not format:
            msg = 'Key [{}] does not exist'.format(key)
            logger.error(msg)
            raise ValueError(msg)

        return format

    def utcnow(self, format='YYYY-MM-DD HH:mm:ss', needs_format=True):
        """ Returns now in UTC formatted as given in 'format'.
        """
        return self.now(format, 'UTC', needs_format)

    def now(self, format='YYYY-MM-DD HH:mm:ss', tz='UTC', needs_format=True):
        """ Returns now in a specified timezone.
        """
        now = arrow.now(tz=tz)
        if needs_format:
            return now.format(format)
        return now

    def today(self, format='YYYY-MM-DD', tz='UTC', needs_format=True):
        """ Returns current day in a given timezone.
        """
        now = arrow.now(tz=tz)
        today = arrow.Arrow(year=now.year, month=now.month, day=now.day)

        if tz != 'UTC':
            today = today.to(tz)

        if format.startswith('kvdb:'):
            format = self.get_format_from_kvdb(format)

        if needs_format:
            return today.format(format)
        else:
            return today

    def reformat(self, value, from_, to):
        """ Reformats value from one datetime format to another, for instance
        from 23-03-2013 to 03/23/13 (MM-DD-YYYY to DD/MM/YY).
        """
        if from_.startswith('kvdb:'):
            from_ = self.get_format_from_kvdb(from_)

        if to.startswith('kvdb:'):
            to = self.get_format_from_kvdb(to)

        try:
            # Arrow compares to str, not basestring
            value = str(value) if isinstance(value, unicode) else value
            from_ = str(from_) if isinstance(from_, unicode) else from_
            return arrow.get(value, from_).format(to)
        except Exception:
            logger.error('Could not reformat value:`%s` from:`%s` to:`%s`',
                value, from_, to)
            raise

# ################################################################################################################################
