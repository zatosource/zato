# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.importers.microsoft_cloud import MicrosoftCloudImporter

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

class MicrosoftTeamsImporter(MicrosoftCloudImporter):

    # Connection-specific constants - everything else runs on the Microsoft 365 implementation.
    connection_type = GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': False,
        'is_outgoing': True,
        'pool_size': 20,
        'timeout': 250,
        'address': None,
    }

# ################################################################################################################################
# ################################################################################################################################
