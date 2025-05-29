# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import HTTPBasicAuth, APIKeySecurity, NTLM, OAuth
from zato.common.odb.query import basic_auth_list, apikey_security_list, ntlm_list, oauth_list
from zato.common.util.api import get_security_def_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SecurityExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter
        self.sec_defs = {}

# ################################################################################################################################

    def process_basic_auth(self, session:'SASession') -> 'list':
        """ Process and export HTTP Basic Auth definitions.
        """
        basic_auth_list_result = basic_auth_list(session, self.exporter.cluster_id)
        basic_auth_defs = []

        for item in basic_auth_list_result:
            name = item.name
            logger.info('Processing basic_auth: %s', name)

            # Create a dictionary representation of the basic auth definition
            basic_auth_def = {
                'name': name,
                'type': 'basic_auth',
                'username': item.username,
                'is_active': item.is_active
            }

            # Add to results
            basic_auth_defs.append(basic_auth_def)

            # Store in exporter's security definitions
            self.exporter.sec_defs[name] = {
                'id': item.id,
                'name': name,
                'type': 'basic_auth'
            }

        return basic_auth_defs

# ################################################################################################################################

    def process_apikey(self, session:'SASession') -> 'list':
        """ Process and export API Key definitions.
        """
        apikey_list_result = apikey_security_list(session, self.exporter.cluster_id)
        apikey_defs = []

        for item in apikey_list_result:
            name = item.name
            logger.info('Processing apikey: %s', name)

            # Create a dictionary representation of the API key definition
            apikey_def = {
                'name': name,
                'type': 'apikey',
                'username': item.username,
                'is_active': item.is_active
            }

            # Add to results
            apikey_defs.append(apikey_def)

            # Store in exporter's security definitions
            self.exporter.sec_defs[name] = {
                'id': item.id,
                'name': name,
                'type': 'apikey'
            }

        return apikey_defs

# ################################################################################################################################

    def process_ntlm(self, session:'SASession') -> 'list':
        """ Process and export NTLM Auth definitions.
        """
        ntlm_list_result = ntlm_list(session, self.exporter.cluster_id)
        ntlm_defs = []

        for item in ntlm_list_result:
            name = item.name
            logger.info('Processing ntlm: %s', name)

            # Create a dictionary representation of the NTLM auth definition
            ntlm_def = {
                'name': name,
                'type': 'ntlm',
                'username': item.username,
                'is_active': item.is_active
            }

            # Add to results
            ntlm_defs.append(ntlm_def)

            # Store in exporter's security definitions
            self.exporter.sec_defs[name] = {
                'id': item.id,
                'name': name,
                'type': 'ntlm'
            }

        return ntlm_defs

# ################################################################################################################################

    def process_oauth(self, session:'SASession') -> 'list':
        """ Process and export OAuth/Bearer Token definitions.
        """
        oauth_list_result = oauth_list(session, self.exporter.cluster_id)
        oauth_defs = []

        for item in oauth_list_result:
            name = item.name
            logger.info('Processing oauth/bearer_token: %s', name)

            # Create a dictionary representation of the OAuth definition
            oauth_def = {
                'name': name,
                'type': 'bearer_token',
                'username': item.username,
                'is_active': item.is_active,
                'auth_endpoint': item.auth_endpoint,
                'client_id_field': item.client_id_field,
                'client_secret_field': item.client_secret_field,
                'grant_type': item.grant_type,
                'data_format': item.data_format
            }

            # Add extra fields if they exist
            if item.extra_fields:
                oauth_def['extra_fields'] = [item.extra_fields]

            # Add to results
            oauth_defs.append(oauth_def)

            # Store in exporter's security definitions
            self.exporter.sec_defs[name] = {
                'id': item.id,
                'name': name,
                'type': 'bearer_token'
            }

        return oauth_defs

# ################################################################################################################################

    def export_security_definitions(self, session:'SASession') -> 'list':
        """ Export all security definitions from the database.
        """
        logger.info('Exporting security definitions from cluster_id=%s', self.exporter.cluster_id)

        # Clear existing security definitions
        self.sec_defs = {}

        # Process different security types
        basic_auth_defs = self.process_basic_auth(session)
        apikey_defs = self.process_apikey(session)
        ntlm_defs = self.process_ntlm(session)
        oauth_defs = self.process_oauth(session)

        # Combine all security definitions
        all_defs = basic_auth_defs + apikey_defs + ntlm_defs + oauth_defs

        logger.info('Exported %d security definitions: basic_auth=%d, apikey=%d, ntlm=%d, oauth=%d',
                    len(all_defs), len(basic_auth_defs), len(apikey_defs), len(ntlm_defs), len(oauth_defs))

        return all_defs

# ################################################################################################################################
# ################################################################################################################################
