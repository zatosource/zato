# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Every shared scenario of queue delivery, run through outgoing Kafka connections on every pub/sub backend.

# Test support
from queue_delivery.scenarios import SharedScenarios
from _type import kafka_type

# ################################################################################################################################
# ################################################################################################################################

class TestShared(SharedScenarios):
    type_under_test = kafka_type

# ################################################################################################################################
# ################################################################################################################################
