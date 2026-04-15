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
    jira_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class JiraExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'jira_def_list':
        """ Exports JIRA connection definitions.
        """
        logger.info('Exporting JIRA connection definitions')

        if not items:
            logger.info('No JIRA connection definitions found')
            return []

        logger.debug('Processing %d JIRA connection definitions', len(items))

        exported_jira = []

        for row in items:

            item = {
                'name': row['name'],
                'address': row.get('address', ''),
                'username': row.get('username', ''),
                'api_version': row.get('api_version', ''),
            }

            if row.get('is_cloud') is True:
                item['is_cloud'] = True

            if (timeout := row.get('timeout')) and timeout != 600:
                item['timeout'] = timeout

            exported_jira.append(item)

        logger.info('Successfully prepared %d JIRA connection definitions for export', len(exported_jira))
        return exported_jira

# ################################################################################################################################
# ################################################################################################################################
