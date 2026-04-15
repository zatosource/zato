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

class SMTPExporter:

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
        """ Exports SMTP connection definitions.
        """
        logger.info('Exporting SMTP connection definitions')

        excluded_names = set()
        excluded_prefixes = ['zato', 'pub.zato', 'demo']

        exported_smtp = []

        for item in items:
            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            smtp_conn = {
                'name': item['name'],
                'host': item.get('host', ''),
                'port': item.get('port', 0),
            }

            if username := item.get('username'):
                smtp_conn['username'] = username

            if item.get('mode', 'plain') != 'plain':
                smtp_conn['mode'] = item['mode']

            ping_address = item.get('ping_address', '')
            if isinstance(ping_address, str) and ping_address.strip():
                smtp_conn['ping_address'] = ping_address

            if item.get('timeout', 60) != 60:
                smtp_conn['timeout'] = item['timeout']

            if item.get('is_tls') is True:
                smtp_conn['is_tls'] = True

            if item.get('is_debug') and (debug_level := item.get('debug_level')):
                smtp_conn['debug_level'] = debug_level

            exported_smtp.append(smtp_conn)

        logger.info('Successfully prepared %d SMTP connection definitions for export', len(exported_smtp))
        return exported_smtp

# ################################################################################################################################
# ################################################################################################################################
