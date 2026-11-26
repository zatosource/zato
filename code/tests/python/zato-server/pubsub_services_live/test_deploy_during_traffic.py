# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.control import clear_step_delay, set_step_delay
from zato.common.test.order_to_cash.models import Carrier, Step

# Order-to-cash
from order_to_cash.scenario import check_orders, get_trail_items, Module, new_po_number, new_standard_order, Outcome, \
    read_source, Source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# How long each step takes while the new version is deployed, which keeps the orders submitted before it in flight
_step_delay = 0.3

# How many orders are submitted before and after the deployment
_orders_before = 10
_orders_after = 10

# The versions of the fulfillment
_first_version = 1
_carrier_version = 2

# ################################################################################################################################
# ################################################################################################################################

def test_new_fulfillment_while_orders_are_in_flight(suite:'Suite') -> 'None':
    """ The second version of the fulfillment is written to the pickup directory while orders are in flight.
    The orders submitted after the listener reported the deployment ship with a carrier, and no order is lost
    or published twice.
    """
    before = [new_po_number('BEFORE-DEPLOY') for _ in range(_orders_before)]
    after = [new_po_number('AFTER-DEPLOY') for _ in range(_orders_after)]

    set_step_delay(suite.server_directory, _step_delay)

    try:
        suite.submit_many([new_standard_order(po_number) for po_number in before])

        # The listener deploys the new version while the orders above pass through the chain ..
        suite.environment.deploy(Module.Fulfillment, read_source(Source.Fulfillment_Carrier))

        # .. and the orders below are submitted once it has.
        suite.submit_many([new_standard_order(po_number) for po_number in after])

    finally:
        clear_step_delay(suite.server_directory)

    expectations = {po_number: Outcome.Invoiced for po_number in before + after}

    # The orders that were in flight during the deployment may repeat a step that the deployment interrupted
    trail = check_orders(suite.client, expectations, in_flight=set(before))

    # Each order in flight was shipped by one version or the other ..
    for po_number in before:
        items = get_trail_items(trail, po_number, Step.Fulfillment)
        assert items[-1]['version'] in (_first_version, _carrier_version), items

    # .. and each order after the deployment by the new one, with the carrier on its invoice.
    for po_number in after:

        fulfillment = get_trail_items(trail, po_number, Step.Fulfillment)
        invoicing = get_trail_items(trail, po_number, Step.Invoicing)

        assert [item['version'] for item in fulfillment] == [_carrier_version], fulfillment
        assert fulfillment[0]['carrier'] == Carrier.Parcel
        assert invoicing[0]['carrier'] == Carrier.Parcel

# ################################################################################################################################
# ################################################################################################################################
