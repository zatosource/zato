# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.test.order_to_cash.models import Step, Topic

# Order-to-cash
from order_to_cash.scenario import check_empty_queues, check_orders, count_audit_events, count_messages_by_topic, \
    get_ledger_entries, get_msg_ids, get_steps, new_po_number, new_standard_order, new_unknown_sku_order, Outcome, \
    read_trail, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# How many orders are submitted along with the order that cannot be fulfilled
_other_orders = 3

# ################################################################################################################################
# ################################################################################################################################

def test_unknown_sku_exhausts_the_retries(suite:'Suite') -> 'None':
    """ The fulfillment of an order with a SKU that no warehouse stocks fails on every attempt until the retry policy
    of the publication is exhausted. The delivery is recorded as failed, nothing reaches the invoicing for the order,
    and the other orders complete.
    """
    failed_po = new_po_number('UNKNOWN-SKU')
    other_po_numbers = [new_po_number('SKU-OTHER') for _ in range(_other_orders)]

    orders = [new_unknown_sku_order(failed_po)]
    orders.extend(new_standard_order(other) for other in other_po_numbers)

    suite.submit_many(orders)

    # The other orders complete once the round of the failed delivery ends ..
    _ = check_orders(suite.client, {other: Outcome.Invoiced for other in other_po_numbers})

    # .. the approved order was published once ..
    msg_ids = get_msg_ids(suite.client, Topic.Order_Approved, failed_po)
    assert len(msg_ids) == 1, msg_ids

    msg_id = msg_ids[0]

    # .. and its delivery to the fulfillment is recorded as failed.
    def _is_failed() -> 'bool':
        out = count_audit_events(suite.environment.database_env, msg_id, AuditEvent.Delivery_Failed) == 1
        return out

    wait_until(_is_failed, f'The audit event of the failed delivery of message {msg_id}')

    # The chain stopped at the credit check ..
    trail = read_trail(suite.client)
    assert get_steps(trail)[failed_po] == [Step.Intake, Step.Credit_Approved]
    assert get_ledger_entries(trail, failed_po) == []

    # .. so the order has no ship notice and no invoice ..
    counts = count_messages_by_topic(suite.client)

    assert counts[Topic.Order_Accepted][failed_po] == 1
    assert counts[Topic.Order_Approved][failed_po] == 1
    assert counts[Topic.Order_Shipped][failed_po] == 0
    assert counts[Topic.Invoice_Issued][failed_po] == 0

    # .. and no subscription has anything left to deliver.
    check_empty_queues(suite.client)

# ################################################################################################################################
# ################################################################################################################################
