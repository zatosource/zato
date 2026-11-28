# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from ack_values import run_ack_values_scenario
from attempt_values import run_attempt_values_scenario
from cleanup import run_cleanup_scenario
from concurrency import run_concurrency_scenario
from count_consistency import run_count_consistency_scenario
from dlq_rule import run_dlq_rule_scenario
from encryption import run_encryption_scenario
from fenced_values import run_fenced_values_scenario
from lease_budget import run_lease_budget_scenario
from lifecycle import run_lifecycle_scenario
from message_dedup import run_message_dedup_scenario
from outgoing import run_outgoing_scenario
from publish_events import run_publish_events_scenario
from publish_values import run_publish_values_scenario
from pull_events import run_pull_events_scenario
from pull_values import run_pull_values_scenario
from push_delivery import run_push_delivery_scenario
from queue_order import run_queue_order_scenario
from queues import run_queues_scenario
from retry_settings import run_retry_settings_scenario
from stats import run_stats_scenario
from trace_values import run_trace_values_scenario
from wakeup import run_wakeup_scenario
from write_transaction import run_write_transaction_scenario

# ################################################################################################################################
# ################################################################################################################################

def run_common_scenarios() -> 'None':
    """ Runs the scenarios that every database type passes in the same way.
    """
    run_lifecycle_scenario()
    run_queues_scenario()
    run_stats_scenario()
    run_wakeup_scenario()
    run_encryption_scenario()
    run_cleanup_scenario()
    run_push_delivery_scenario()
    run_retry_settings_scenario()
    run_outgoing_scenario()
    run_queue_order_scenario()
    run_dlq_rule_scenario()
    run_concurrency_scenario()
    run_count_consistency_scenario()
    run_pull_values_scenario()
    run_lease_budget_scenario()
    run_pull_events_scenario()
    run_publish_values_scenario()
    run_message_dedup_scenario()
    run_ack_values_scenario()
    run_trace_values_scenario()
    run_fenced_values_scenario()
    run_attempt_values_scenario()
    run_publish_events_scenario()
    run_write_transaction_scenario()

# ################################################################################################################################
# ################################################################################################################################
