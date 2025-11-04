# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.json_internal import loads
from zato.common.odb.model import to_json
from zato.common.odb.query import basic_auth_list, apikey_security_list, ntlm_list, oauth_list
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

class SecurityExporter:

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

    def _process_standard_security(self, items, sec_type, excluded_names, excluded_prefixes):
        result = []

        for item in items:
            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            # Create base security entry
            security_entry = {
                'name': item['name'],
                'type': sec_type,
                'username': item['username']
            }

            # Add is_active if present
            if 'is_active' in item:
                security_entry['is_active'] = item['is_active']

            # Handle opaque attributes
            if 'opaque_attr' in item and item['opaque_attr']:
                opaque = parse_instance_opaque_attr(item)
                security_entry.update(opaque)

            result.append(security_entry)

        return result

    def _process_bearer_tokens(self, items, excluded_names, excluded_prefixes):
        result = []

        # Known required fields for bearer tokens that must be included
        required_fields = ['auth_endpoint']

        # Fields that might be in opaque data
        possible_fields = [
            'auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', 'data_format', 'extra_fields'
        ]

        for item in items:
            if self._should_skip_item(item, excluded_names, excluded_prefixes):
                continue

            # Log fields for debugging
            logger.info('Fields for bearer_token %s: %s', item['name'], sorted(item.keys()))

            # Create base token entry
            oauth = {
                'name': item['name'],
                'type': 'bearer_token',
                'username': item['username']
            }

            # Add is_active if present
            if 'is_active' in item:
                oauth['is_active'] = item['is_active']

            # Get opaque data from various sources and merge them
            opaque_data = {}
            missing_fields = []

            # Try to access as opaque1 attribute (SQLAlchemy objects)
            if hasattr(item, 'opaque1') and item.opaque1:
                try:
                    data = loads(item.opaque1)
                    if data:
                        opaque_data.update(data)
                except Exception as e:
                    logger.warning('Error parsing opaque1 attribute for %s: %s', item['name'], e)

            # Try to access as opaque1 dict key (JSON objects)
            if not opaque_data and 'opaque1' in item and item['opaque1']:
                try:
                    data = loads(item['opaque1'])
                    if data:
                        opaque_data.update(data)
                except Exception as e:
                    logger.warning('Error parsing opaque1 key for %s: %s', item['name'], e)

            # Check for direct attributes in the item that match our needed fields
            # This handles the case where fields are directly on the model
            for field in possible_fields:
                if field in item and item[field]:
                    opaque_data[field] = item[field]

            # Update OAuth definition with the collected opaque data
            if opaque_data:
                # Rename auth_server_url back to auth_endpoint for export
                if 'auth_server_url' in opaque_data:
                    opaque_data['auth_endpoint'] = opaque_data.pop('auth_server_url')
                oauth.update(opaque_data)

            # Check for missing required fields
            for field in required_fields:
                if field not in oauth:
                    missing_fields.append(field)

            if missing_fields:
                logger.warning('Bearer token %s is missing required fields: %s', item['name'], missing_fields)

            result.append(oauth)

        return result

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'list_[anydict]':
        """ Exports security definitions.
        """
        logger.info('Exporting security definitions with exclusions')

        # Names to exclude completely
        excluded_names = {'Rule engine default user', 'admin.invoke', 'ide_publisher'}

        # Prefixes to exclude
        excluded_prefixes = ['zato', 'pub.zato', 'demo']

        exported_security = []

        # Get all security definitions from the database
        basic_auth_defs = basic_auth_list(session, cluster_id)
        apikey_defs = apikey_security_list(session, cluster_id)
        ntlm_defs = ntlm_list(session, cluster_id)
        oauth_defs = oauth_list(session, cluster_id)

        # Process basic auth definitions
        if basic_auth_defs:
            basic_auth_items = to_json(basic_auth_defs, return_as_dict=True)
            logger.info('Processing %d basic auth definitions', len(basic_auth_items))

            # Process and get basic auth items
            basic_auth_security = self._process_standard_security(basic_auth_items, 'basic_auth', excluded_names, excluded_prefixes)
            exported_security.extend(basic_auth_security)

        # Process API key definitions
        if apikey_defs:
            apikey_items = to_json(apikey_defs, return_as_dict=True)
            logger.info('Processing %d API key definitions', len(apikey_items))

            # Process and get API key items
            apikey_security = self._process_standard_security(apikey_items, 'apikey', excluded_names, excluded_prefixes)
            exported_security.extend(apikey_security)

        # Process NTLM definitions
        if ntlm_defs:
            ntlm_items = to_json(ntlm_defs, return_as_dict=True)
            logger.info('Processing %d NTLM definitions', len(ntlm_items))

            # Process and get NTLM items
            ntlm_security = self._process_standard_security(ntlm_items, 'ntlm', excluded_names, excluded_prefixes)
            exported_security.extend(ntlm_security)

        # Process OAuth bearer token definitions
        if oauth_defs:
            oauth_items = to_json(oauth_defs, return_as_dict=True)
            logger.info('Processing %d bearer token definitions', len(oauth_items))

            # Process and get bearer token items
            bearer_tokens = self._process_bearer_tokens(oauth_items, excluded_names, excluded_prefixes)
            exported_security.extend(bearer_tokens)

        logger.info('Successfully prepared %d security definitions for export', len(exported_security))
        return exported_security

# ################################################################################################################################
# ################################################################################################################################
