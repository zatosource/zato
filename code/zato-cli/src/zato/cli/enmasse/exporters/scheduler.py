# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, list_
    job_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SchedulerExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'job_def_list':
        """ Exports scheduler job definitions.
        """
        logger.info('Exporting scheduler job definitions')

        if not items:
            logger.info('No scheduler job definitions found')
            return []

        exported_jobs = []

        for row in items:
            start_date = row.get('start_date', '')
            if not isinstance(start_date, str):
                start_date = str(start_date)

            item = {
                'name': row['name'],
                'service': row.get('service_name') or row.get('service', ''),
                'job_type': row.get('job_type', ''),
                'start_date': start_date,
                'is_active': row.get('is_active', True),
            }

            for attr in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
                if value := row.get(attr):
                    item[attr] = value

            if repeats := row.get('repeats'):
                item['repeats'] = repeats

            if max_repeats := row.get('max_repeats'):
                item['max_repeats'] = max_repeats

            if extra := row.get('extra'):
                extra = extra.decode('utf8') if isinstance(extra, bytes) else extra
                extra = extra.strip() if isinstance(extra, str) else extra
                if extra:
                    item['extra'] = extra

            exported_jobs.append(item)

        logger.info('Successfully prepared %d scheduler job definitions for export', len(exported_jobs))

        return exported_jobs

# ################################################################################################################################
# ################################################################################################################################
