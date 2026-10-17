# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scenarios every transport of channels with the queue on goes through. A transport's suite runs them all with one class:
#
#   class TestShared(ChannelScenarios):
#       type_under_test = rest_channel_type

# Test support
from queue_delivery.channel_scenarios.ack import AckScenarios
from queue_delivery.channel_scenarios.audit import AuditScenarios
from queue_delivery.channel_scenarios.browse import BrowseScenarios
from queue_delivery.channel_scenarios.delivery import DeliveryScenarios
from queue_delivery.channel_scenarios.enmasse import EnmasseScenarios
from queue_delivery.channel_scenarios.responses import ResponseScenarios

# ################################################################################################################################
# ################################################################################################################################

class ChannelScenarios(
    AckScenarios,
    ResponseScenarios,
    DeliveryScenarios,
    BrowseScenarios,
    AuditScenarios,
    EnmasseScenarios,
    ):
    """ Every channel scenario, in the order the blocks were built in.
    """

# ################################################################################################################################
# ################################################################################################################################
