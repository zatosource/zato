# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared retry, DLQ and browse scenarios of channels with the queue on, run through SMS channels on every pub/sub backend.
# The acknowledgement, static response, hook and audit scenarios describe HTTP channels - an SMS channel answers a provider's
# callback in the provider's own form and records its events as batches, so those scenarios do not apply to it.

# Test support
from queue_delivery.channel_scenarios.browse import BrowseScenarios
from queue_delivery.channel_scenarios.delivery import DeliveryScenarios
from _type import sms_channel_type

# ################################################################################################################################
# ################################################################################################################################

class TestShared(DeliveryScenarios, BrowseScenarios):
    type_under_test = sms_channel_type

# ################################################################################################################################
# ################################################################################################################################
