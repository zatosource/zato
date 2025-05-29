# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import SMTP
from zato.common.odb.query import smtp_connection_list

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

class SMTPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_smtp_definitions(self, session:'SASession') -> 'list':
        """ Export SMTP connection definitions from the database.
        """
        logger.info('Exporting SMTP connections from cluster_id=%s', self.exporter.cluster_id)

        # Get SMTP connections from the database
        smtp_connections = smtp_connection_list(session, self.exporter.cluster_id)

        smtp_defs = []

        for conn in smtp_connections:
            logger.info('Processing SMTP connection: %s', conn.name)

            # Create a dictionary representation of the SMTP connection
            smtp_def = {
                'name': conn.name,
                'host': conn.host,
                'port': conn.port,
                'username': conn.username,
                'is_active': conn.is_active
            }

            # Add timeout if not default
            if conn.timeout != 30:
                smtp_def['timeout'] = conn.timeout

            # Add debug level if not default
            if conn.is_debug:
                smtp_def['is_debug'] = True

            # Add mode if not default
            if conn.mode != 'starttls':
                smtp_def['mode'] = conn.mode

            # Add ping address if not default
            if conn.ping_address and conn.ping_address != 'example@example.com':
                smtp_def['ping_address'] = conn.ping_address

            # Store in exporter's SMTP definitions
            self.exporter.smtp_defs[conn.name] = {
                'id': conn.id,
                'name': conn.name
            }

            # Add to results
            smtp_defs.append(smtp_def)

        logger.info('Exported %d SMTP connections', len(smtp_defs))
        return smtp_defs

# ################################################################################################################################
# ################################################################################################################################
