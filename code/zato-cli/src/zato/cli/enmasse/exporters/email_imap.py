# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import to_json
from zato.common.odb.query import email_imap_list
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

class IMAPExporter:

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
        """ Exports IMAP connection definitions.
        """
        logger.info('Exporting IMAP connection definitions with exclusions')

        # Names to exclude completely
        excluded_names = set()

        # Prefixes to exclude
        excluded_prefixes = ['zato', 'pub.zato', 'demo']

        exported_imap = []

        # Get all IMAP connection definitions from the database
        imap_defs = email_imap_list(session, cluster_id)

        if imap_defs:
            imap_items = to_json(imap_defs, return_as_dict=True)
            logger.info('Processing %d IMAP connection definitions', len(imap_items))

            for item in imap_items:
                if self._should_skip_item(item, excluded_names, excluded_prefixes):
                    continue

                # Create base IMAP connection entry
                imap_conn = {
                    'name': item['name'],
                    'host': item['host'],
                    'username': item['username'],
                }

                # Add standard fields if present
                for field in ['port', 'timeout', 'ssl', 'get_criteria', 'is_active']:
                    if field in item:
                        imap_conn[field] = item[field]

                # Handle opaque attributes
                if 'opaque_attr' in item and item['opaque_attr']:
                    opaque = parse_instance_opaque_attr(item)
                    imap_conn.update(opaque)

                exported_imap.append(imap_conn)

        logger.info('Successfully prepared %d IMAP connection definitions for export', len(exported_imap))
        return exported_imap

# ################################################################################################################################
# ################################################################################################################################
