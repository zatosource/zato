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
from zato.common.util.sql import parse_instance_opaque_attr

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
        logger.info('Processing %d scheduler job definitions', len(jobs))

        exported_jobs = []

        for row in jobs:
            # Basic job information
            item = {
                'name': row['name'],
                'is_active': row['is_active'],
                'job_type': row['job_type'],
                'service': row['service_name']
            }

            # Include start_date if present
            if 'start_date' in row and row['start_date']:
                item['start_date'] = row['start_date']

            # Include interval-based job attributes if present
            for attr in _interval_based_job_attrs:
                if attr in row and row[attr] is not None:
                    item[attr] = row[attr]

            # Include any extra fields that might be present
            for field in ['extra', 'max_repeats']:
                if field in row and row[field]:
                    item[field] = row[field]

            # Process any opaque attributes
            if 'opaque_attr' in row and row['opaque_attr']:
                opaque = parse_instance_opaque_attr(row)
                item.update(opaque)

            exported_jobs.append(item)

        logger.info('Successfully prepared %d scheduler job definitions for export', len(exported_jobs))

        return exported_jobs

# ################################################################################################################################
# ################################################################################################################################
