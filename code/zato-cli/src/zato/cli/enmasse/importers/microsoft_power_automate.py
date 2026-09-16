# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC, MicrosoftPowerAutomate
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

class MicrosoftPowerAutomateImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': False,
        'is_outgoing': True,
        'address': MicrosoftPowerAutomate.Default.Address,
        'pool_size': 20,
        'timeout': 250,
    }

    connection_extra_field_defaults = {
        'tenant_id': None,
        'client_id': None,
        'client_secret': None,
        'environment_id': None,
        'token_url': None,
        'recv_timeout': 250
    }

    connection_secret_keys = ['client_secret', 'secret', 'password']
    connection_required_attrs = ['name', 'client_id', 'tenant_id', 'environment_id']

# ################################################################################################################################
# ################################################################################################################################
