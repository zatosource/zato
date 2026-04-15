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
    group_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GroupExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter
        self.excluded_groups = {'Rule engine API users'}

# ################################################################################################################################

    def export(self, items) -> 'group_def_list':
        """ Exports security group definitions.
        """
        logger.info('Exporting security group definitions')

        if not items:
            logger.info('No security group definitions found')
            return []

        logger.info('Processing %d security group definitions', len(items))

        exported_groups = []

        for group in items:
            group_name = group['name']

            # Skip groups that are to be excluded
            if group_name in self.excluded_groups:
                continue

            group_def = {
                'name': group_name,
                'members': group.get('members', [])
            }

            exported_groups.append(group_def)

        logger.info('Successfully prepared %d security group definitions for export', len(exported_groups))

        return exported_groups

# ################################################################################################################################
# ################################################################################################################################
