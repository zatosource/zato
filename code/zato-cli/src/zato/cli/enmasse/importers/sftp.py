# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.common.api import GENERIC, SFTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class SFTPImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SFTP,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': 1,

        # These two are columns on the ODB model rather than opaque attributes
        'port': SFTP.DEFAULT.PORT,
        'username': '',
    }

    connection_extra_field_defaults = {
        'host': '',
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

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'host']

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Let the base class update the opaque attributes first ..
        connection = super().update_definition(connection_def, session)

        # .. and then update the two fields that are columns on the ODB model
        # .. rather than opaque attributes, but only if they are actually given on input.
        if 'port' in connection_def:
            connection.port = connection_def['port']

        if 'username' in connection_def:
            connection.username = connection_def['username']

        return connection

# ################################################################################################################################
# ################################################################################################################################
