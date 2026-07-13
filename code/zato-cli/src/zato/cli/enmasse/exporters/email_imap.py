# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import EMAIL, GENERIC
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

        imap_items = to_json(imap_defs, return_as_dict=True)

        for item in imap_items:

            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            if GENERIC.ATTR_NAME in item:
                opaque = parse_instance_opaque_attr(item)
                item.update(opaque)
                del item[GENERIC.ATTR_NAME]

            # Create base IMAP connection entry with fields in import order
            imap_conn = {
                'name': item['name'],
            }

            server_type = item.get('server_type')
            imap_conn['type'] = server_type # We export the server type as "type"

            if server_type == 'microsoft_365':
                if tenant_id := item.get('tenant_id'):
                    imap_conn['tenant_id'] = tenant_id
                if client_id := item.get('client_id'):
                    imap_conn['client_id'] = client_id
            else:
                # For standard IMAP, include host and port
                if host := item.get('host'):
                    imap_conn['host'] = host
                if port := item.get('port'):
                    imap_conn['port'] = port

            # Username is common for both types
            if username := item.get('username'):
                imap_conn['username'] = username

            # Skip empty get_criteria
            if (get_criteria := item.get('get_criteria')) and get_criteria != '{}':
                imap_conn['get_criteria'] = get_criteria

            # Only include timeout if not the default (30)
            if (timeout := item.get('timeout')) and timeout != 30:
                imap_conn['timeout'] = timeout

            # Include the linked scheduler job configuration, if any - the job ID itself
            # is never exported because IDs are not portable across environments.
            if scheduler_service := item.get('scheduler_service'):
                imap_conn['scheduler_run_every'] = item['scheduler_run_every']
                imap_conn['scheduler_run_unit'] = item['scheduler_run_unit']
                if scheduler_start_date := item.get('scheduler_start_date'):
                    imap_conn['scheduler_start_date'] = scheduler_start_date
                imap_conn['scheduler_service'] = scheduler_service

                # The invoke-with mode is exported only if it differs from the default message one
                if scheduler_invoke_with := item.get('scheduler_invoke_with'):
                    if scheduler_invoke_with != EMAIL.IMAP.Scheduler.InvokeWith.Message:
                        imap_conn['scheduler_invoke_with'] = scheduler_invoke_with

            # The audit log is on by default so only the off state is exported
            if item.get('is_audit_log_active') is False:
                imap_conn['is_audit_log_active'] = False

            exported_imap.append(imap_conn)

        logger.info('Successfully prepared %d IMAP connection definitions for export', len(exported_imap))
        return exported_imap

# ################################################################################################################################
# ################################################################################################################################
