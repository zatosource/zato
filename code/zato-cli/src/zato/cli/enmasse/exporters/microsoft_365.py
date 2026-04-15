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
    microsoft_365_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365Exporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

    def export(self, items) -> 'microsoft_365_def_list':
        """ Exports Microsoft 365 connection definitions.
        """
        logger.info('Exporting Microsoft 365 connection definitions')

        if not items:
            logger.info('No Microsoft 365 connection definitions found')
            return []

        logger.debug('Processing %d Microsoft 365 connection definitions', len(items))

        exported_microsoft_365 = []

        for row in items:

            item = {
                'name': row['name'],
                'is_active': row.get('is_active', True),
            }

            if client_id := row.get('client_id'):
                item['client_id'] = client_id

            if tenant_id := row.get('tenant_id'):
                item['tenant_id'] = tenant_id

            if scopes := row.get('scopes'):
                if isinstance(scopes, str):
                    lines = scopes.splitlines()
                    clean_scopes = [line.strip() for line in lines if line.strip()]
                    if clean_scopes:
                        if len(clean_scopes) <= 1:
                            item['scopes'] = clean_scopes[0] if clean_scopes else ''
                        else:
                            item['scopes'] = sorted(clean_scopes)
                else:
                    item['scopes'] = scopes

            if (pool_size := row.get('pool_size')) and pool_size != 10:
                item['pool_size'] = pool_size

            if (timeout := row.get('timeout')) and timeout != 600:
                item['timeout'] = timeout

            if recv_timeout := row.get('recv_timeout'):
                item['recv_timeout'] = recv_timeout

            exported_microsoft_365.append(item)

        logger.info('Successfully prepared %d Microsoft 365 connection definitions for export', len(exported_microsoft_365))
        return exported_microsoft_365

# ################################################################################################################################
# ################################################################################################################################
