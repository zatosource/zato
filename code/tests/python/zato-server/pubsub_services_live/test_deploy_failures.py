# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.control import clear_step_delay, set_step_delay
from zato.common.test.order_to_cash.models import Carrier, ServiceName, Step

# Order-to-cash
from order_to_cash.scenario import check_orders, get_trail_items, Module, new_po_number, new_standard_order, Outcome, \
    read_source, Source
from order_to_cash.services_broken import Source as Broken_Source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# How long each step takes while the broken module is deployed, which keeps the orders in flight
_step_delay = 0.3

# How many orders are submitted before and after the broken module
_orders_before = 10
_orders_after = 10

# The versions of the fulfillment
_first_version = 1
_carrier_version = 2

# What the server logs when the worker that received the broken module forwards it to the other ones and they refuse it,
# which is the only record of the refusal that does not name the module
_forwarded_deploy_failure = 'Forwarded invocation of `zato.hot-deploy.create`'

# ################################################################################################################################
# ################################################################################################################################

def test_broken_module_leaves_the_previous_version(suite:'Suite') -> 'None':
    """ A version of the fulfillment with a syntax error is written to the pickup directory while orders flow.
    The previous version continues to serve, every order completes, and a valid version deployed afterwards
    through the same pickup directory takes effect.
    """
    before = [new_po_number('BEFORE-BROKEN') for _ in range(_orders_before)]
    after = [new_po_number('AFTER-BROKEN') for _ in range(_orders_after)]

    # The server and the listener log the refusal of the broken module
    suite.environment.expect_records(Module.Fulfillment, _forwarded_deploy_failure)

    set_step_delay(suite.server_directory, _step_delay)

    try:
        suite.submit_many([new_standard_order(po_number) for po_number in before])

        # The listener reports the outcome of the broken module, whichever it is ..
        _ = suite.environment.deploy_attempt(Module.Fulfillment, Broken_Source)

        # .. and the orders below arrive after it.
        suite.submit_many([new_standard_order(po_number) for po_number in after])

    finally:
        clear_step_delay(suite.server_directory)

    assert suite.is_deployed(ServiceName.Fulfillment)

    expectations = {po_number: Outcome.Invoiced for po_number in before + after}
    trail = check_orders(suite.client, expectations, in_flight=set(before))

    # Every order was shipped by the first version, which the broken module did not replace
    for po_number in before + after:
        items = get_trail_items(trail, po_number, Step.Fulfillment)
        assert [item['version'] for item in items] == [_first_version] * len(items), items

    # A valid version deployed after the failure takes effect
    is_deployed = suite.environment.deploy_attempt(Module.Fulfillment, read_source(Source.Fulfillment_Carrier))
    assert is_deployed

    recovered_po = new_po_number('RECOVERED')
    suite.submit(new_standard_order(recovered_po))

    trail = check_orders(suite.client, {recovered_po: Outcome.Invoiced})
    items = get_trail_items(trail, recovered_po, Step.Fulfillment)

    assert [item['version'] for item in items] == [_carrier_version], items
    assert items[0]['carrier'] == Carrier.Parcel

# ################################################################################################################################
# ################################################################################################################################
