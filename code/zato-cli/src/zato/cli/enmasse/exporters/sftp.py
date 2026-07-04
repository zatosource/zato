# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, SFTP
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    sftp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to extract from opaque attributes, in the order they are exported
OPTIONAL_FIELDS = [
    'port', 'identity_file', 'ssh_config_file', 'log_level', 'sftp_command', 'ping_command', 'buffer_size',
    'bandwidth_limit', 'force_ip_type', 'should_flush', 'should_preserve_meta', 'is_compression_enabled',
    'ssh_options', 'default_directory'
]

# Values that are not exported because they match the defaults
_field_defaults = {
    'port': SFTP.DEFAULT.PORT,
    'identity_file': '',
    'ssh_config_file': '',
    'log_level': 0,
    'sftp_command': SFTP.DEFAULT.COMMAND_SFTP,
    'ping_command': SFTP.DEFAULT.COMMAND_PING,
    'buffer_size': SFTP.DEFAULT.BUFFER_SIZE,
    'bandwidth_limit': SFTP.DEFAULT.BANDWIDTH_LIMIT,
    'force_ip_type': '',
    'should_flush': False,
    'should_preserve_meta': True,
    'is_compression_enabled': False,
    'ssh_options': '',
    'default_directory': '',
}

# ################################################################################################################################
# ################################################################################################################################

class SFTPExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'sftp_def_list':
        """ Exports SFTP connection definitions.
        """
        logger.info('Exporting SFTP connection definitions')

        # Get SFTP connections from database using the generic connection query
        db_sftp = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP)

        if not db_sftp:
            logger.info('No SFTP connection definitions found in DB')
            return []

        sftp_connections = to_json(db_sftp, return_as_dict=True)
        logger.debug('Processing %d SFTP connection definitions', len(sftp_connections))

        exported_sftp = []

        for row in sftp_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base SFTP connection entry with fields in import order
            item = {
                'name': row['name'],
            }

            if host := row.get('host'):
                item['host'] = host

            if username := row.get('username'):
                item['username'] = username

            # Only add optional fields that do not match the defaults - note that the password
            # is never exported because secrets do not leave the database in plain text.
            for field in OPTIONAL_FIELDS:
                value = row.get(field)
                if value is None:
                    continue
                default = _field_defaults[field]
                if value != default:
                    item[field] = value

            exported_sftp.append(item)

        logger.info('Successfully prepared %d SFTP connection definitions for export', len(exported_sftp))
        return exported_sftp

# ################################################################################################################################
# ################################################################################################################################
