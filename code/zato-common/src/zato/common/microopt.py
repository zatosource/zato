# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import LogRecord
from sys import exc_info

def logging_Logger_log(self, level, msg, args, exc_info=None, extra=None, _LogRecord=LogRecord, _exc_info=exc_info):
    """ Overrides logging.Logger._log to gain a tiny but tangible performance boost (1%-3%).
    """
    try:
        fn, lno, func = self.findCaller()
    except ValueError:
        fn, lno, func = "(unknown file)", 0, "(unknown function)"

    if exc_info:
        if not isinstance(exc_info, tuple):
            exc_info = _exc_info()

    record = _LogRecord(self.name, level, fn, lno, msg, args, exc_info, func)

    if extra is not None:
        record.__dict__.update(extra)

    if not self.disabled:
        if self.filters:
            if self.filter(record):
                self.callHandlers(record)
        else:
            self.callHandlers(record)
