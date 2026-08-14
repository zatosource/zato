# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

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

    # Input validation and client-supplied JSONata response filters
    'validate_input', 'allow_client_filters',

    # Response shaping
    'max_response_size', 'size_cap_mode', 'min_size_threshold', 'characters_per_token',

    # Compaction
    'safeguards_strip_nulls', 'safeguards_collapse_whitespace', 'safeguards_strip_base64',

    # PII removal
    'safeguards_pii_enabled', 'safeguards_pii_lands', 'safeguards_pii_detectors', 'safeguards_pii_exclude',
    'safeguards_pii_validate', 'safeguards_pii_stable_tokens',

    # Content safety
    'safeguards_normalize_unicode', 'safeguards_unicode_mode', 'safeguards_sanitize_markup', 'safeguards_markup_mode',
    'safeguards_url_policy_enabled', 'safeguards_url_allow_list', 'safeguards_url_mode',
]

GATEWAY_OPAQUE_FIELDS = list(GATEWAY_OPTIONAL_FIELDS)

# ################################################################################################################################
# ################################################################################################################################

class GatewayMCPExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'mcp_def_list':
        """ Exports MCP gateway definitions.
        """
        logger.info('Exporting MCP gateway definitions')

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

            # A field is exported whenever the row carries it, falsy values included -
            # otherwise an explicit False against a True default would not survive a round trip.
            for field in GATEWAY_OPTIONAL_FIELDS:
                if field in row:
                    value = row[field]
                    if value is not None:
                        item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d MCP gateway definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
