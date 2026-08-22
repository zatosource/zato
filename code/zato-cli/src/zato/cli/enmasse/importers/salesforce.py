# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.common.api import GENERIC, SALESFORCE

# ################################################################################################################################
# ################################################################################################################################

class SalesforceImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': False,
        'is_outgoing': True,
        'pool_size': SALESFORCE.Default.Pool_Size,
        'recv_timeout': SALESFORCE.Default.Recv_Timeout,
    }

    connection_extra_field_defaults = {
        'api_version': SALESFORCE.Default.API_Version,
    }

    connection_secret_keys = ['password']
    connection_required_attrs = ['name', 'address', 'username']

# ################################################################################################################################
# ################################################################################################################################
