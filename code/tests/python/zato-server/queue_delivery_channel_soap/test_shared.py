# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every shared scenario of channels with the queue on, run through SOAP channels on every pub/sub backend.

# Test support
from queue_delivery.channel_scenarios import ChannelScenarios
from _type import soap_channel_type

# ################################################################################################################################
# ################################################################################################################################

class TestShared(ChannelScenarios):
    type_under_test = soap_channel_type

# ################################################################################################################################
# ################################################################################################################################
