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
    }

    connection_extra_field_defaults = {
        'host': '',
        'port': SFTP.DEFAULT.PORT,
        'username': '',
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
# ################################################################################################################################
