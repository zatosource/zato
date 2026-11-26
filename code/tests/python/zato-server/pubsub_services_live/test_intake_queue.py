# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.control import count_pending_failures, Fault, fail_attempts
from zato.common.test.order_to_cash.models import Step, Topic

# Order-to-cash
from order_to_cash.scenario import check_orders, count_messages_by_topic, get_channel_dlq, get_steps, get_trail_items, \
    new_invalid_order, new_po_number, new_standard_order, Outcome, read_trail, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# How many attempts of the intake fail after they published, fewer than the retries of the channel
_failed_attempts = 2

# ################################################################################################################################
# ################################################################################################################################

def test_retry_after_publication_publishes_once(suite:'Suite') -> 'None':
    """ The intake publishes the accepted order and then fails, twice. The queue of the channel retries it,
    and the message ID derived from the purchase order number leaves one accepted order in the topic.
    """
    po_number = new_po_number('INTAKE-RETRY')

    fail_attempts(suite.server_directory, Fault.Intake_After_Publish, po_number, _failed_attempts)

    suite.submit(new_standard_order(po_number))

    # The intake step repeats for this order, which was in flight during the fault ..
    trail = check_orders(suite.client, {po_number: Outcome.Invoiced}, in_flight={po_number})

    # .. once for each attempt of the queue ..
    items = get_trail_items(trail, po_number, Step.Intake)
    assert len(items) == _failed_attempts + 1, items

    # .. while the topic has the order once, as checked with the rest of the chain.
    assert count_pending_failures(suite.server_directory, Fault.Intake_After_Publish, po_number) == 0

# ################################################################################################################################

def test_order_refused_on_every_attempt_goes_to_the_dlq(suite:'Suite') -> 'None':
    """ An order that the intake refuses on every attempt exhausts the retries of the channel and is kept in its DLQ,
    where the delivery page of the channel lists it. Nothing of it is published.
    """
    po_number = new_po_number('INTAKE-DLQ')

    suite.submit(new_invalid_order(po_number))

    # The query of the delivery page matches the request in lowercase
    query = po_number.lower()

    def _is_in_dlq() -> 'bool':
        page = get_channel_dlq(suite.client, query)
        out = len(page['items']) == 1
        return out

    wait_until(_is_in_dlq, f'The arrival of PO `{po_number}` in the DLQ of the channel')

    # The intake refused the order before it recorded or published anything
    trail = read_trail(suite.client)
    assert po_number not in get_steps(trail)

    counts = count_messages_by_topic(suite.client)
    assert counts[Topic.Order_Accepted][po_number] == 0

# ################################################################################################################################
# ################################################################################################################################
