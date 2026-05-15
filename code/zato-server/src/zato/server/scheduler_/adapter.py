# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import logging
from contextlib import closing

logger = logging.getLogger(__name__)

default_interval_value = 0

class SchedulerODBAdapter:

    def __init__(self, odb, cluster_id):
        self.odb = odb
        self.cluster_id = cluster_id

    def get_scheduler_jobs(self):
        from zato.common.odb.model import Job, IntervalBasedJob
        from zato.common.util.sql import parse_instance_opaque_attr

        with closing(self.odb.session()) as session:
            jobs = session.query(Job).filter_by(cluster_id=self.cluster_id).all()

            logger.info('[DEBUG-DEMO-PUBSUB] ODB has %d scheduler jobs for cluster_id=%s', len(jobs), self.cluster_id)
            for _dbg_job in jobs:
                logger.info(
                    '[DEBUG-DEMO-PUBSUB] ODB job id=%s name=%s service=%s is_active=%s',
                    _dbg_job.id, _dbg_job.name,
                    _dbg_job.service.name if _dbg_job.service else '<no-service>',
                    _dbg_job.is_active,
                )

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
                    entry['weeks'] = interval.weeks if interval.weeks is not None else default_interval_value
                    entry['days'] = interval.days if interval.days is not None else default_interval_value
                    entry['hours'] = interval.hours if interval.hours is not None else default_interval_value
                    entry['minutes'] = interval.minutes if interval.minutes is not None else default_interval_value
                    entry['seconds'] = interval.seconds if interval.seconds is not None else default_interval_value
                    entry['repeats'] = interval.repeats

                result[job.id] = entry

        return result
