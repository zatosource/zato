# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import Discord, GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_default = Discord.Default

# ################################################################################################################################
# ################################################################################################################################

class DiscordImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.CHAT_DISCORD

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHAT_DISCORD,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': False,
        'is_outgoing': True,
        'pool_size': 20,
        'timeout': _default.Timeout,
        'address': _default.Address,
    }

    connection_extra_field_defaults = {
        'recv_timeout': 250,
        'timeout': _default.Timeout,
        'default_channel_id': '',
    }

    connection_secret_keys = ['token', 'secret', 'password']
    connection_required_attrs = ['name']

# ################################################################################################################################
# ################################################################################################################################
