# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import logging
from contextlib import closing

logger = logging.getLogger(__name__)

class SchedulerODBAdapter:

    def __init__(self, odb, cluster_id):
        self.odb = odb
        self.cluster_id = cluster_id

    def get_scheduler_jobs(self):
        from zato.common.odb.model import Job, IntervalBasedJob
        from zato.common.util.sql import parse_instance_opaque_attr

        with closing(self.odb.session()) as session:
            jobs = session.query(Job).filter_by(cluster_id=self.cluster_id).all()
            result = {}
            for job in jobs:
                entry = {
                    'name': job.name,
                    'is_active': job.is_active,
                    'job_type': job.job_type,
                    'service': job.service.name if job.service else '',
                    'start_date': job.start_date.isoformat() if job.start_date else '',
                    'extra': job.extra or '',
                }

                opaque = parse_instance_opaque_attr(job)
                entry.update(opaque)

                interval = session.query(IntervalBasedJob).filter_by(job_id=job.id).first()
                if interval:
                    entry['weeks'] = interval.weeks or 0
                    entry['days'] = interval.days or 0
                    entry['hours'] = interval.hours or 0
                    entry['minutes'] = interval.minutes or 0
                    entry['seconds'] = interval.seconds or 0
                    entry['repeats'] = interval.repeats

                result[job.id] = entry

        return result
