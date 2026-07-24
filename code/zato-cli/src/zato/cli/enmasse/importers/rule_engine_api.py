# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.util.rule_engine_api import default_rule_engine_api_url_path, ensure_rule_engine_api_channel
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

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

class RuleEngineAPIImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
    }

    connection_extra_field_defaults = {
        'url_path': default_rule_engine_api_url_path,
        'rulesets': [],
        'security_groups': [],
    }

    connection_secret_keys = []
    connection_required_attrs = ['name']

# ################################################################################################################################

    def _resolve_security_groups(self, connection_def:'anydict') -> 'anylist':
        """ Converts security group names from YAML to their database IDs.
        """
        out:'anylist' = []

        if group_names := connection_def.get('security_groups'):
            for group_name in group_names:
                if group_name not in self.importer.group_defs:
                    raise Exception(
                        f'Security group "{group_name}" not found for Rule engine API "{connection_def["name"]}"')
                group_id = self.importer.group_defs[group_name]['id']
                out.append(group_id)

        return out

# ################################################################################################################################

    def _ensure_rest_channel(self, connection_def:'anydict', session:'SASession') -> 'None':

        channel_name = connection_def['name']
        security_groups = self._resolve_security_groups(connection_def)

        ensure_rule_engine_api_channel(
            session=session,
            channel_name=channel_name,
            url_path=connection_def.get('url_path', default_rule_engine_api_url_path),
            cluster_id=self.importer.cluster_id,
            is_active=connection_def.get('is_active', True),
            security_groups=security_groups,
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
