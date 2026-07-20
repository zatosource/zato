# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, LLM
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    llm_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields exported only when they differ from their defaults
OPTIONAL_FIELDS = [
    'pool_size', 'timeout', 'max_tokens', 'max_history_turns', 'chat_expiry',
]

# What each optional field defaults to
_field_defaults = {
    'pool_size': LLM.DEFAULT.POOL_SIZE,
    'timeout': LLM.DEFAULT.TIMEOUT,
    'max_tokens': LLM.DEFAULT.MAX_TOKENS,
    'max_history_turns': LLM.DEFAULT.MAX_HISTORY_TURNS,
    'chat_expiry': LLM.DEFAULT.CHAT_EXPIRY,
}

# ################################################################################################################################
# ################################################################################################################################

class LLMExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'llm_def_list':
        """ Exports LLM connection definitions.
        """
        logger.info('Exporting LLM connection definitions')

        # Get LLM connections from database using the generic connection query
        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_LLM)

        if not db_items:
            logger.info('No LLM connection definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d LLM connection definitions', len(connections))

        exported = []

        for row in connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create the base entry with fields in import order
            item = {
                'name': row['name'],
            }

            if provider := row.get('provider'):
                item['provider'] = provider

            if address := row.get('address'):
                item['address'] = address

            if model := row.get('model'):
                item['model'] = model

            # Add other optional fields only if they have non-default values
            for field in OPTIONAL_FIELDS:
                if value := row.get(field):
                    default = _field_defaults[field]
                    if value != default:
                        item[field] = value

            exported.append(item)

        logger.info('Successfully prepared %d LLM connection definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
