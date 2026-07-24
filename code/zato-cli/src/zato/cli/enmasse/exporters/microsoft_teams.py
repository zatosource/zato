# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.cli.enmasse.exporters.microsoft_cloud import MicrosoftCloudExporter

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftTeamsExporter(MicrosoftCloudExporter):

    # Connection-specific constants - everything else runs on the Microsoft 365 implementation.
    connection_type = GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS
    label = 'Microsoft Teams'

# ################################################################################################################################
# ################################################################################################################################
