# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import LDAP
from zato.common.odb.query import ldap_connection_list

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

class LDAPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_ldap_definitions(self, session:'SASession') -> 'list':
        """ Export LDAP connection definitions from the database.
        """
        logger.info('Exporting LDAP connections from cluster_id=%s', self.exporter.cluster_id)

        # Get LDAP connections from the database
        ldap_connections = ldap_connection_list(session, self.exporter.cluster_id)

        ldap_defs = []

        for conn in ldap_connections:
            logger.info('Processing LDAP connection: %s', conn.name)

            # Create a dictionary representation of the LDAP connection
            ldap_def = {
                'name': conn.name,
                'username': conn.username,
                'auth_type': conn.auth_type,
                'server_list': conn.server_list,
                'is_active': conn.is_active
            }

            # Store in exporter's LDAP definitions
            self.exporter.ldap_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }

            # Add to results
            ldap_defs.append(ldap_def)

        logger.info('Exported %d LDAP connections', len(ldap_defs))
        return ldap_defs

# ################################################################################################################################
# ################################################################################################################################
