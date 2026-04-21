# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class ConfluenceImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': False,
        'is_outgoing': True,
        'pool_size': 20,
        'timeout': 250,
    }

    connection_extra_field_defaults = {
        'site_url': None,
        'auth_token': None,
        'is_cloud': True,
        'api_version': 'v1',
    }

    connection_secret_keys = ['password', 'secret', 'api_token']
    connection_required_attrs = ['name', 'address', 'username']

# ################################################################################################################################
# ################################################################################################################################
