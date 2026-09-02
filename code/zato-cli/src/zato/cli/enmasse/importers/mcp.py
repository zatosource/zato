# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import CONNECTION, GENERIC, Groups, MCP
from zato.common.odb.model import GenericConn, GenericObject, HTTPSOAP
from zato.common.util.gateway import ensure_mcp_rest_channel
from zato.common.util.safeguards.common import Mode_Clean, Url_Mode_Remove
from zato.common.util.truncate.tokens import Default_Characters_Per_Token, Size_Cap_Mode_Truncate
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, listtuple, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The connections a gateway exposes as tools - one allow list per connection group,
# each defaulting to an empty list.
_connection_list_defaults:'anydict' = {}

for _connection_list_key in MCP.Connection_List_Keys:
    _connection_list_defaults[_connection_list_key] = []

# ################################################################################################################################
# ################################################################################################################################

class GatewayMCPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.GATEWAY_MCP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
    }

    # Every runtime field of an MCP gateway - routing, tools, skills, validation,
    # agent filters, response shaping and the whole safeguards family - so a YAML
    # definition can state any of them and an unstated one gets its documented default.
    connection_extra_field_defaults = {

        # Routing and security
        'url_path': '/mcp',
        'services': [],
        'security_groups': [],
        'is_audit_log_active': False,

        # Skills served as prompts
        'skills': [],

        # Sessions - zero keeps the default idle TTL
        'session_ttl': 0,

        # How long one tools/call invocation may run for, in seconds - zero keeps the default
        'invoke_timeout': 0,

        # Input validation and agent-supplied JSONata response filters
        'validate_input': False,
        'allow_agent_filters': False,

        # Response shaping - zeroes keep the cap and its threshold off
        'max_response_size': 0,
        'size_cap_mode': Size_Cap_Mode_Truncate,
        'min_size_threshold': 0,
        'characters_per_token': Default_Characters_Per_Token,

        # Compaction
        'safeguards_strip_nulls': False,
        'safeguards_collapse_whitespace': False,
        'safeguards_strip_base64': False,

        # PII removal
        'safeguards_pii_enabled': False,
        'safeguards_pii_lands': [],
        'safeguards_pii_detectors': [],
        'safeguards_pii_exclude': [],
        'safeguards_pii_validate': True,
        'safeguards_pii_stable_replacements': False,

        # Secrets removal
        'safeguards_secrets_enabled': False,

        # Content safety
        'safeguards_normalize_unicode': False,
        'safeguards_unicode_mode': Mode_Clean,
        'safeguards_sanitize_markup': False,
        'safeguards_markup_mode': Mode_Clean,
        'safeguards_url_policy_enabled': False,
        'safeguards_url_allow_list': [],
        'safeguards_url_mode': Url_Mode_Remove,

        # The connections the gateway exposes as tools
        **_connection_list_defaults,
    }

    connection_secret_keys = []
    connection_required_attrs = ['name']

# ################################################################################################################################

    def _normalize_services(self, connection_def:'anydict') -> 'None':
        """ Services are a proper YAML list, but a comma-separated string from an older
        configuration is accepted too and becomes the list it always meant to be.
        """
        services = connection_def.get('services')

        if isinstance(services, str):

            out:'strlist' = []

            for name in services.split(','):
                name = name.strip()
                if name:
                    out.append(name)

            connection_def['services'] = out

# ################################################################################################################################

    def _get_group_id_from_db(self, group_name:'str', session:'SASession') -> 'any_':
        """ The ID of one security group that already exists in the database,
        or None if there is no such group.
        """
        query = select([
            GenericObject.id,
        ]).where(and_(
            GenericObject.name == group_name,
            GenericObject.type_ == Groups.Type.Group_Parent,
            GenericObject.subtype == Groups.Type.API_Clients,
            GenericObject.cluster_id == self.importer.cluster_id,
        ))

        row = session.execute(query).fetchone()

        out = row['id'] if row is not None else None
        return out

# ################################################################################################################################

    def _resolve_security_groups(self, connection_def:'anydict', session:'SASession') -> 'list':
        """ Converts security group names from YAML to their database IDs -
        a group absent from the YAML input may still exist in the database,
        e.g. when a gateway travels in a YAML file of its own.
        """
        out:'list' = []

        if group_names := connection_def.get('security_groups'):
            for group_name in group_names:

                if group_name in self.importer.group_defs:
                    group_id = self.importer.group_defs[group_name]['id']
                else:
                    group_id = self._get_group_id_from_db(group_name, session)

                if group_id is None:
                    raise Exception(f'Security group "{group_name}" not found for MCP gateway "{connection_def["name"]}"')

                out.append(group_id)

        return out

# ################################################################################################################################

    def _ensure_rest_channel(self, connection_def:'anydict', session:'SASession') -> 'None':

        channel_name = connection_def['name']
        security_groups = self._resolve_security_groups(connection_def, session)

        ensure_mcp_rest_channel(
            session=session,
            channel_name=channel_name,
            url_path=connection_def.get('url_path', '/mcp'),
            cluster_id=self.importer.cluster_id,
            is_active=connection_def.get('is_active', True),
            security_groups=security_groups,
        )

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        self._normalize_services(connection_def)
        instance = super().create_definition(connection_def, session)
        self._ensure_rest_channel(connection_def, session)
        return instance

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        self._normalize_services(connection_def)
        instance = super().update_definition(connection_def, session)
        self._ensure_rest_channel(connection_def, session)
        return instance

# ################################################################################################################################

    def _delete_gateway(self, gateway_name:'str', session:'SASession') -> 'None':
        """ Deletes one MCP gateway - both its generic connection and the REST channel that
        made it reachable. The config reload that follows an import drops the wrapper
        and the URL routing of the deleted rows.
        """

        connection = session.query(GenericConn).filter(
            GenericConn.name == gateway_name,
            GenericConn.type_ == self.connection_type,
            GenericConn.cluster_id == self.importer.cluster_id,
        ).first()

        if connection is not None:
            session.delete(connection)
            logger.info('Deleted MCP gateway connection: %s', gateway_name)

        channel = session.query(HTTPSOAP).filter(
            HTTPSOAP.name == gateway_name,
            HTTPSOAP.connection == CONNECTION.CHANNEL,
            HTTPSOAP.cluster_id == self.importer.cluster_id,
        ).first()

        if channel is not None:
            session.delete(channel)
            logger.info('Deleted MCP gateway REST channel: %s', gateway_name)

# ################################################################################################################################

    def sync_definitions(self, conn_list:'anylist', session:'SASession') -> 'listtuple':
        """ An mcp_gateway entry marked should_delete is removed instead of created or updated -
        everything else syncs the way any generic connection does.
        """

        remaining:'anylist' = []

        for item in conn_list:

            if item.get('should_delete'):
                self._delete_gateway(item['name'], session)
            else:
                remaining.append(item)

        # The deletions land on their own, so a failure in the create-update pass
        # can never roll a requested deletion back.
        session.commit()

        out = super().sync_definitions(remaining, session)
        return out

# ################################################################################################################################
# ################################################################################################################################
