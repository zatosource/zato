# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import PubSub
from zato.common.odb.query import pubsub_permission_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    pubsub_permission_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubPermissionExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'pubsub_permission_def_list':
        """ Exports pub/sub permission definitions.
        """
        logger.info('Exporting pub/sub permission definitions')

        # Local variables
        pub_prefix = 'pub='
        sub_prefix = 'sub='
        exported_permissions: 'pubsub_permission_def_list' = []

        # Get pub/sub permissions from database
        query_result = pubsub_permission_list(session, cluster_id, needs_columns=False)

        search_results = query_result[0]
        items = search_results.result

        # Group permissions by security definition
        security_permissions = {}

        for item in items:
            # Each item is a tuple: (PubSubPermission, security_name, subscription_count)
            permission_obj = item[0]
            security_name = item[1]

            if hasattr(permission_obj, '_asdict'):
                permission_obj = permission_obj._asdict()
                permission_obj = permission_obj['PubSubPermission']

            if security_name not in security_permissions:
                security_permissions[security_name] = {'pub': [], 'sub': []}

            permission = security_permissions[security_name]

            # Determine access type and add to appropriate list
            if permission_obj.access_type == PubSub.API_Client.Publisher:
                permission['pub'].append(permission_obj.pattern)

            elif permission_obj.access_type == PubSub.API_Client.Subscriber:
                permission['sub'].append(permission_obj.pattern)

            elif permission_obj.access_type == PubSub.API_Client.Publisher_Subscriber:
                # Split combined patterns on newlines and parse prefixes
                patterns = [p.strip() for p in permission_obj.pattern.splitlines() if p.strip()]
                for individual_pattern in patterns:
                    if individual_pattern.startswith(pub_prefix):
                        clean_pattern = individual_pattern[len(pub_prefix):]
                        permission['pub'].append(clean_pattern)
                    elif individual_pattern.startswith(sub_prefix):
                        clean_pattern = individual_pattern[len(sub_prefix):]
                        permission['sub'].append(clean_pattern)

            else:
                raise ValueError(f'Unknown access_type: {permission_obj.access_type}')

        # Convert grouped permissions to export format
        for security_name, permissions in security_permissions.items():
            exported_permission: 'anydict' = {
                'security': security_name,
            }

            # Add pub permissions if any exist
            if permissions['pub']:
                exported_permission['pub'] = permissions['pub']

            # Add sub permissions if any exist
            if permissions['sub']:
                exported_permission['sub'] = permissions['sub']

            # Only add if there are actual permissions
            if 'pub' in exported_permission or 'sub' in exported_permission:
                exported_permissions.append(exported_permission)

        logger.info('Successfully prepared %d pub/sub permission definitions for export', len(exported_permissions))
        return exported_permissions

# ################################################################################################################################
# ################################################################################################################################
