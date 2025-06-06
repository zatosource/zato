# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query import email_smtp_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession

    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SMTPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def _should_skip_item(self, item, excluded_names, excluded_prefixes):

        # Skip items in exclude list
        if item['name'] in excluded_names:
            return True

        # Skip items with excluded prefixes
        for prefix in excluded_prefixes:
            if item['name'].startswith(prefix):
                return True

        return False

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'list_[anydict]':
        """ Exports SMTP connection definitions.
        """
        logger.info('Exporting SMTP connection definitions with exclusions')

        # Names to exclude completely
        excluded_names = set()

        # Prefixes to exclude
        excluded_prefixes = ['zato', 'pub.zato', 'demo']

        exported_smtp = []

        # Get all SMTP connection definitions from the database
        smtp_defs = email_smtp_list(session, cluster_id)

        smtp_items = to_json(smtp_defs, return_as_dict=True)

        for item in smtp_items:
            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            if GENERIC.ATTR_NAME in item:
                opaque = parse_instance_opaque_attr(item)
                item.update(opaque)
                del item[GENERIC.ATTR_NAME]

            smtp_conn = {
                'name': item['name'],
                'host': item['host'],
                'port': item['port'],
            }

            if username := item.get('username'):
                smtp_conn['username'] = username

            if item['mode'] != 'plain':
                smtp_conn['mode'] = item['mode']

            if item['ping_address'].strip():
                smtp_conn['ping_address'] = item['ping_address']

            if item['timeout'] != 60:
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
