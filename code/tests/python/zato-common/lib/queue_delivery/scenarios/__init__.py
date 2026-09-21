# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scenarios every type of outgoing connection goes through. A type's suite runs them all with one class:
#
#   class TestShared(SharedScenarios):
#       type_under_test = rest_type

# Test support
from queue_delivery.scenarios.amqp_transport import AMQPTransportScenarios
from queue_delivery.scenarios.browse import BrowseScenarios
from queue_delivery.scenarios.dlq import DLQScenarios
from queue_delivery.scenarios.dlq_rule import DLQRuleScenarios
from queue_delivery.scenarios.harness import HarnessScenarios
from queue_delivery.scenarios.lifecycle import LifecycleScenarios
from queue_delivery.scenarios.ordering import OrderingScenarios
from queue_delivery.scenarios.retry_policy import RetryPolicyScenarios
from queue_delivery.scenarios.send_result import SendResultScenarios

# ################################################################################################################################
# ################################################################################################################################

class SharedScenarios(
    HarnessScenarios,
    SendResultScenarios,
    OrderingScenarios,
    RetryPolicyScenarios,
    DLQScenarios,
    DLQRuleScenarios,
    LifecycleScenarios,
    BrowseScenarios,
    AMQPTransportScenarios,
    ):
    """ Every shared scenario, in the order the blocks were built in.
    """

# ################################################################################################################################
# ################################################################################################################################
