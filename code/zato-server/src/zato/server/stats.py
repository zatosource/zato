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
from traceback import format_exc

# dateutil
from dateutil.rrule import MINUTELY, rrule

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common import KVDB, scheduler_date_time_format
from zato.common.odb.model import Job, IntervalBasedJob, Service
from zato.common.odb.query import _service as _service

logger = logging.getLogger(__name__)

def _get_service_by_name(session, cluster_id, name):
    logger.debug('Looking for name:[{}] in cluster_id:[{}]'.format(name, cluster_id))
    return _service(session, cluster_id).\
           filter(Service.name==name).\
           one()

def add_stats_jobs(cluster_id, odb, stats_jobs):
    """ Adds one of the interval jobs to the ODB. Note that it isn't being added
    directly to the scheduler because we want users to be able to fine-tune the job's
    settings.
    """
    with closing(odb.session()) as session:
        for item in stats_jobs:
            
            try:
                service_id = _get_service_by_name(session, cluster_id, item['service'])[0]
                
                now = datetime.utcnow().strftime(scheduler_date_time_format)
                job = Job(None, item['name'], True, 'interval_based', now, item.get('extra', '').encode('utf-8'),
                          cluster_id=cluster_id, service_id=service_id)
                          
                kwargs = {}
                for name in('seconds', 'minutes'):
                    if name in item:
                        kwargs[name] = item[name]
                        
                ib_job = IntervalBasedJob(None, job, **kwargs)
                
                session.add(job)
                session.add(ib_job)
                session.commit()
            except IntegrityError, e:
                session.rollback()
                logger.debug('Caught an IntegrityError, carrying on anyway, e:[%s]', format_exc(e).decode('utf-8'))
                
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
