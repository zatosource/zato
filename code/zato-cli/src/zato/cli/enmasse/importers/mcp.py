# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.util.channel import ensure_mcp_rest_channel
from zato.common.util.sql import get_security_by_id
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_MCP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
    }

    connection_extra_field_defaults = {
        'url_path': '/mcp',
        'services': '',
        'security': None,
        'security_groups': [],
    }

    connection_secret_keys = []
    connection_required_attrs = ['name']

# ################################################################################################################################

    def _ensure_rest_channel(self, connection_def:'anydict', session:'SASession') -> 'None':

        channel_name = connection_def['name']
        cluster = self.importer.get_cluster(session)

        # Resolve security if specified ..
        security_item = None
        if security_name := connection_def.get('security'):
            if security_name in self.importer.sec_defs:
                sec_def = self.importer.sec_defs[security_name]
                security_item = get_security_by_id(session, sec_def['id'])
                logger.info('Resolved security "%s" -> id=%s for MCP channel %s', security_name, sec_def['id'], channel_name)
            else:
                logger.warning('Security definition "%s" not found for MCP channel "%s"', security_name, channel_name)

        ensure_mcp_rest_channel(
            session=session,
            channel_name=channel_name,
            url_path=connection_def.get('url_path', '/mcp'),
            cluster_id=cluster.id,
            is_active=connection_def.get('is_active', True),
            security_item=security_item,
            security_groups=connection_def.get('security_groups', []),
        )

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        instance = super().create_definition(connection_def, session)
        self._ensure_rest_channel(connection_def, session)
        return instance

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        instance = super().update_definition(connection_def, session)
        self._ensure_rest_channel(connection_def, session)
        return instance

# ################################################################################################################################
# ################################################################################################################################
