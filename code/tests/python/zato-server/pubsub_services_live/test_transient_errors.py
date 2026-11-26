# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.order_to_cash.control import count_pending_failures, Fault, fail_attempts
from zato.common.test.order_to_cash.models import Step

# Order-to-cash
from order_to_cash.scenario import check_orders, get_trail_items, new_po_number, new_standard_order, Outcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# How many attempts of the step fail, fewer than the retries of the publications
_failed_attempts = 2

# How many orders are submitted along with the order whose step fails
_other_orders = 3

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize(('fault', 'step'), [
    (Fault.Invoicing, Step.Invoicing),
    (Fault.Fulfillment, Step.Fulfillment),
])
def test_outage_then_recovery(suite:'Suite', fault:'str', step:'str') -> 'None':
    """ A step fails for a number of attempts while its backend is unavailable, then completes, and the chain
    publishes the result of the step once. The orders submitted with it complete as well.
    """
    po_number = new_po_number('OUTAGE')
    other_po_numbers = [new_po_number('OUTAGE-OTHER') for _ in range(_other_orders)]

    fail_attempts(suite.server_directory, fault, po_number, _failed_attempts)

    orders = [new_standard_order(po_number)]
    orders.extend(new_standard_order(other) for other in other_po_numbers)

    suite.submit_many(orders)

    expectations = {other: Outcome.Invoiced for other in other_po_numbers}
    expectations[po_number] = Outcome.Invoiced

    # One message per topic is among the checks, so the retries published nothing twice ..
    trail = check_orders(suite.client, expectations)

    # .. every failure was consumed by an attempt ..
    assert count_pending_failures(suite.server_directory, fault, po_number) == 0

    # .. and only the attempt that succeeded recorded the step.
    items = get_trail_items(trail, po_number, step)
    assert len(items) == 1, items

# ################################################################################################################################
# ################################################################################################################################
