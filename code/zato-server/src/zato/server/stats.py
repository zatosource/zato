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
import logging
from contextlib import closing
from datetime import datetime
from traceback import format_exc

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MINUTELY, rrule

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common import KVDB, scheduler_date_time_format
from zato.common.odb.model import Job, IntervalBasedJob, Service
from zato.common.odb.query import _service as _service

logger = logging.getLogger(__name__)

def _get_service_by_impl_name(session, cluster_id, impl_name):
    return _service(session, cluster_id).\
           filter(Service.impl_name==impl_name).\
           one()

def add_stats_jobs(cluster_id, odb, stats_jobs):
    """ Adds one of the interval jobs to the ODB. Note that it isn't being added
    directly to the scheduler because we want users to be able to fine-tune the job's
    settings.
    """
    with closing(odb.session()) as session:
        for item in stats_jobs:
            
            try:
                service_id = _get_service_by_impl_name(session, cluster_id, item['service'])[0]
                
                now = datetime.now().strftime(scheduler_date_time_format)
                job = Job(None, item['name'], True, 'interval_based', now, item.get('extra', '').encode('utf-8'),
                          cluster_id=cluster_id, service_id=service_id)
                ib_job = IntervalBasedJob(None, job, seconds=item['seconds'])
                
                session.add(job)
                session.add(ib_job)
                session.commit()
            except IntegrityError, e:
                session.rollback()
                msg = 'Caught an IntegrityError, carrying on anyway, e:[{}]]'.format(format_exc(e))
                logger.debug(msg)
                
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
                    print(33, key)
                    
            p.execute()

