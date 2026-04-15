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

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SecurityExporter:

    def __init__(self, exporter) -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def _should_skip_item(self, item, excluded_names, excluded_prefixes):

        if item['name'] in excluded_names:
            return True

        for prefix in excluded_prefixes:
            if item['name'].startswith(prefix):
                return True

        return False

# ################################################################################################################################

    def export(self, items) -> 'list_[anydict]':
        """ Exports security definitions.
        """
        logger.info('Exporting security definitions')

        excluded_names = {'Rule engine default user', 'admin.invoke', 'ide_publisher', 'metrics'}
        excluded_prefixes = ['zato', 'pub.zato', 'demo']

        exported_security = []

        for item in items:

            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            sec_type = item.get('type') or item.get('sec_type', '')

            security_entry = {
                'name': item['name'],
                'type': sec_type,
            }

            # Add username only if not apikey type
            if sec_type != 'apikey':
                if 'username' in item:
                    security_entry['username'] = item['username']

            if 'is_active' in item:
                security_entry['is_active'] = item['is_active']

            # Bearer token specific fields
            if sec_type == 'bearer_token':
                for field in ['auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', 'data_format', 'extra_fields']:
                    if field in item and item[field]:
                        security_entry[field] = item[field]

            exported_security.append(security_entry)

        logger.info('Successfully prepared %d security definitions for export', len(exported_security))
        return exported_security

# ################################################################################################################################
# ################################################################################################################################
