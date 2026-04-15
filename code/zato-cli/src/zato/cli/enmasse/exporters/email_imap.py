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

class IMAPExporter:

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
        """ Exports IMAP connection definitions.
        """
        logger.info('Exporting IMAP connection definitions')

        excluded_names = set()
        excluded_prefixes = ['zato', 'pub.zato', 'demo']

        exported_imap = []

        for item in items:

            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            imap_conn = {
                'name': item['name'],
            }

            server_type = item.get('server_type') or item.get('type')
            if server_type:
                imap_conn['type'] = server_type

            if server_type == 'microsoft_365':
                if tenant_id := item.get('tenant_id'):
                    imap_conn['tenant_id'] = tenant_id
                if client_id := item.get('client_id'):
                    imap_conn['client_id'] = client_id
            else:
                if host := item.get('host'):
                    imap_conn['host'] = host
                if port := item.get('port'):
                    imap_conn['port'] = port

            if username := item.get('username'):
                imap_conn['username'] = username

            if (get_criteria := item.get('get_criteria')) and get_criteria != '{}':
                imap_conn['get_criteria'] = get_criteria

            if (timeout := item.get('timeout')) and timeout != 30:
                imap_conn['timeout'] = timeout

            exported_imap.append(imap_conn)

        logger.info('Successfully prepared %d IMAP connection definitions for export', len(exported_imap))
        return exported_imap

# ################################################################################################################################
# ################################################################################################################################
