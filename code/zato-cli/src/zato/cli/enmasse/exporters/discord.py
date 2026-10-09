# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import Discord, GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    discord_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The values exported for opaque fields a stored connection does not have
_opaque_defaults = {
    'timeout': Discord.Default.Timeout,
    'default_channel_id': '',
}

# ################################################################################################################################
# ################################################################################################################################

class DiscordExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'discord_def_list':
        """ Exports Discord connection definitions.
        """
        logger.info('Exporting Discord connection definitions')

        # Get Discord connections from database using the generic connection query
        db_discord = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHAT_DISCORD)

        if not db_discord:
            logger.info('No Discord connection definitions found in DB')
            return []

        discord_connections = to_json(db_discord, return_as_dict=True)
        logger.debug('Processing %d Discord connection definitions', len(discord_connections))

        exported_discord = []

        for row in discord_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # A connection created through the admin API alone may have no value for a field the importer defaults
            for key, default in _opaque_defaults.items():
                if key not in row:
                    row[key] = default

            item = {
                'name': row['name'],
                'is_active': row['is_active'],
                'address': row['address'],
                'timeout': row['timeout'],
                'default_channel_id': row['default_channel_id'],
            }

            exported_discord.append(item)

        logger.info('Successfully prepared %d Discord connection definitions for export', len(exported_discord))
        return exported_discord

# ################################################################################################################################
# ################################################################################################################################
