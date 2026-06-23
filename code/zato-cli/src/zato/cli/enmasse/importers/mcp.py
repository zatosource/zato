# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

class ChannelMCPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_MCP

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
    }

    connection_extra_field_defaults = {
        'url_path': '/mcp',
        'services': '',
        'security': None,
    }

    connection_secret_keys = []
    connection_required_attrs = ['name']
