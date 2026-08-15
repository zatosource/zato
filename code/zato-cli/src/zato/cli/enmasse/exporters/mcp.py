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
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.common.api import GENERIC, Groups
from zato.common.odb.model import GenericObject, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, anylist, list_

    mcp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Every runtime field an MCP gateway stores - the same list the importer declares defaults for,
# so what one environment exports another can import without losing a single option.
GATEWAY_OPTIONAL_FIELDS = [

    # Routing and security
    'url_path', 'services', 'security_groups', 'is_audit_log_active',

    # Skills served as prompts
    'skills',

    # Sessions
    'session_ttl',

    # Invocation timeout
    'invoke_timeout',

    # Input validation and client-supplied JSONata response filters
    'validate_input', 'allow_client_filters',

    # Response shaping
    'max_response_size', 'size_cap_mode', 'min_size_threshold', 'characters_per_token',

    # Compaction
    'safeguards_strip_nulls', 'safeguards_collapse_whitespace', 'safeguards_strip_base64',

    # PII removal
    'safeguards_pii_enabled', 'safeguards_pii_lands', 'safeguards_pii_detectors', 'safeguards_pii_exclude',
    'safeguards_pii_validate', 'safeguards_pii_stable_replacements',

    # Content safety
    'safeguards_normalize_unicode', 'safeguards_unicode_mode', 'safeguards_sanitize_markup', 'safeguards_markup_mode',
    'safeguards_url_policy_enabled', 'safeguards_url_allow_list', 'safeguards_url_mode',
]

GATEWAY_OPAQUE_FIELDS = list(GATEWAY_OPTIONAL_FIELDS)

# The documented default of each field - a stored value equal to its default is not exported.
_field_defaults = GatewayMCPImporter.connection_extra_field_defaults

# ################################################################################################################################
# ################################################################################################################################

class GatewayMCPExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter
        self.group_id_to_name = {}

# ################################################################################################################################

    def _load_security_groups(self, session:'SASession', cluster_id:'int') -> 'None':
        """ Loads the security groups of the cluster and builds an id-to-name mapping,
        so gateways created through the dashboard, which stores ids, export names too.
        """
        self.group_id_to_name = {}

        # The session belongs to the caller, which goes on to list the gateways with it,
        # so this method must not close it.
        query = select([
            GenericObject.id,
            GenericObject.name,
        ]).where(and_(
            GenericObject.type_ == Groups.Type.Group_Parent,
            GenericObject.subtype == Groups.Type.API_Clients,
            GenericObject.cluster_id == cluster_id,
        ))

        groups = session.execute(query).fetchall()

        for group in groups:
            self.group_id_to_name[group.id] = group.name

        logger.info('Loaded %d security groups', len(self.group_id_to_name))

# ################################################################################################################################

    def _groups_as_names(self, security_groups:'anylist', gateway_name:'str') -> 'anylist':
        """ Returns the given security groups with every id turned into its name -
        entries that already are names pass through as they are.
        """
        out:'anylist' = []

        for group in security_groups:

            if isinstance(group, int):

                if group in self.group_id_to_name:
                    out.append(self.group_id_to_name[group])
                else:
                    logger.warning('Security group ID %s not found for MCP gateway %s', group, gateway_name)

            else:
                out.append(group)

        return out

# ################################################################################################################################

    def export(self, session: 'SASession', cluster_id: 'int') -> 'mcp_def_list':
        """ Exports MCP gateway definitions.
        """
        logger.info('Exporting MCP gateway definitions')

        # Load security groups for the id-to-name conversion
        self._load_security_groups(session, cluster_id)

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.GATEWAY_MCP)

        if not db_items:
            logger.info('No MCP gateway definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d MCP gateway definitions', len(connections))

        exported = []

        for row in connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            item = {
                'name': row['name'],
            }

            # A field is exported whenever the row carries a value other than the field's
            # documented default - an explicit False against a True default survives that way,
            # while fields left at their defaults stay out of the export.
            for field in GATEWAY_OPTIONAL_FIELDS:

                if field not in row:
                    continue

                value = row[field]

                if value is None:
                    continue

                # Group ids become names before the default comparison,
                # so an empty list is omitted either way.
                if field == 'security_groups':
                    value = self._groups_as_names(value, row['name'])

                if value == _field_defaults[field]:
                    continue

                item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d MCP gateway definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
