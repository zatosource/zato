# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import json
import logging
from contextlib import closing

logger = logging.getLogger(__name__)

class SchedulerODBAdapter:

    def __init__(self, odb, cluster_id):
        self.odb = odb
        self.cluster_id = cluster_id

    def get_scheduler_jobs_json(self):
        from zato.common.odb.model import Job, IntervalBasedJob

        logger.info('SchedulerODBAdapter.get_scheduler_jobs_json: cluster_id=%s, odb=%s',
            self.cluster_id, type(self.odb).__name__)

        with closing(self.odb.session()) as session:
            jobs = session.query(Job).filter_by(cluster_id=self.cluster_id).all()
            logger.info('SchedulerODBAdapter: found %d Job rows for cluster_id=%s', len(jobs), self.cluster_id)

            result = {}
            for job in jobs:
                logger.info('SchedulerODBAdapter: job id=%s, name=%s, is_active=%s, job_type=%s, service=%s, start_date=%s',
                    job.id, job.name, job.is_active, job.job_type,
                    job.service.name if job.service else '(none)', job.start_date)

                entry = {
                    'id': str(job.id),
                    'name': job.name,
                    'is_active': job.is_active,
                    'job_type': job.job_type,
                    'service': job.service.name if job.service else '',
                    'start_date': job.start_date.isoformat() if job.start_date else '',
                    'extra': job.extra or '',
                }

                interval = session.query(IntervalBasedJob).filter_by(job_id=job.id).first()
                if interval:
                    entry['weeks'] = interval.weeks or 0
                    entry['days'] = interval.days or 0
                    entry['hours'] = interval.hours or 0
                    entry['minutes'] = interval.minutes or 0
                    entry['seconds'] = interval.seconds or 0
                    entry['repeats'] = interval.repeats

                result[str(job.id)] = entry

        out = json.dumps(result)
        logger.info('SchedulerODBAdapter: returning %d jobs, json length=%d', len(result), len(out))
        return out

    def get_holiday_calendars_json(self):
        return json.dumps({})
