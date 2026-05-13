# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

class OutgoingGraphQLImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
    }

    connection_extra_field_defaults = {
        'default_query_timeout': 60,
        'extra': None,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'address']
