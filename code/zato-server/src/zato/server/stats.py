# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from datetime import datetime

# dateutil
from dateutil.rrule import MINUTELY, rrule

# Zato
from zato.common import KVDB, scheduler_date_time_format
from zato.common.odb.model import Job, IntervalBasedJob, Service

logger = logging.getLogger(__name__)
                
class MaintenanceTool(object):
    """ A tool for performing maintenance-related tasks, such as deleting the statistics.
    """
    def __init__(self, conn):
        self.conn = conn
        
    def delete(self, start, stop, interval):
        with self.conn.pipeline() as p:
            suffixes = (elem.strftime(':%Y:%m:%d:%H:%M') for elem in rrule(MINUTELY, dtstart=start, until=stop))
            for suffix in suffixes:
                for key in self.conn.keys('{}*{}'.format(KVDB.SERVICE_TIME_AGGREGATED_BY_MINUTE, suffix)):
                    p.delete(key)
                    
            p.execute()
