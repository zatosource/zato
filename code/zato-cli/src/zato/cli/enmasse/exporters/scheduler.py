# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import Job
from zato.common.odb.query import job_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SchedulerExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_scheduler_definitions(self, session:'SASession') -> 'list':
        """ Export scheduler job definitions from the database.
        """
        logger.info('Exporting scheduler jobs from cluster_id=%s', self.exporter.cluster_id)
        
        # Get scheduler jobs from the database
        jobs = job_list(session, self.exporter.cluster_id)
        
        job_defs = []
        
        for job in jobs:
            logger.info('Processing scheduler job: %s', job.name)
            
            # Create a dictionary representation of the scheduler job
            job_def = {
                'name': job.name,
                'service': job.service_name,
                'is_active': job.is_active,
                'job_type': job.job_type
            }
            
            # Add start date if present
            if job.start_date:
                job_def['start_date'] = job.start_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Add time intervals based on job type
            if job.job_type == 'interval_based':
                if job.weeks > 0:
                    job_def['weeks'] = job.weeks
                if job.days > 0:
                    job_def['days'] = job.days
                if job.hours > 0:
                    job_def['hours'] = job.hours
                if job.minutes > 0:
                    job_def['minutes'] = job.minutes
                if job.seconds > 0:
                    job_def['seconds'] = job.seconds
                if job.repeats > 0:
                    job_def['repeats'] = job.repeats
            elif job.job_type == 'cron_style':
                job_def['cron_definition'] = job.cron_definition
            
            # Store in exporter's job definitions
            self.exporter.job_defs[job.name] = {
                'id': job.id,
                'name': job.name
            }
            
            # Add to results
            job_defs.append(job_def)
            
        logger.info('Exported %d scheduler jobs', len(job_defs))
        return job_defs

# ################################################################################################################################
# ################################################################################################################################
