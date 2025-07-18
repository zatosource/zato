# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import to_json
from zato.common.odb.query import job_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.odb.model import Job
    from zato.common.typing_ import anydict, list_

    job_def_list = list_[anydict]
    db_job_list = list_[Job]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_interval_based_job_attrs = {'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats'}

# ################################################################################################################################
# ################################################################################################################################

class SchedulerExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'job_def_list':
        """ Exports scheduler job definitions.
        """
        logger.info('Exporting scheduler job definitions')

        db_jobs = job_list(session, cluster_id)

        if not db_jobs:
            logger.info('No scheduler job definitions found in DB')
            return []

        jobs = to_json(db_jobs, return_as_dict=True)
        logger.debug('Processing %d scheduler job definitions', len(jobs))

        exported_jobs = []

        for row in jobs:
            # Start with name and service, matching import order
            item = {
                'name': row['name'],
                'service': row['service_name'],
                'job_type': row['job_type'],
                'start_date': row['start_date'],
                'is_active': row['is_active'],
            }

            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
                if value := row.get(attr):
                    item[attr] = value

            if repeats := row.get('repeats'):
                item['repeats'] = repeats

            # Include any extra fields that might be present
            for field in ['extra', 'max_repeats']:
                if field_value := row.get(field):
                    item[field] = field_value

            if extra := row.get('extra'):
                extra = extra.decode('utf8') if isinstance(extra, bytes) else extra
                if extra.strip():
                    item['extra'] = extra.splitlines()

            exported_jobs.append(item)

        logger.info('Successfully prepared %d scheduler job definitions for export', len(exported_jobs))

        return exported_jobs

# ################################################################################################################################
# ################################################################################################################################
