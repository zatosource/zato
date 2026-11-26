# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.models import Buyer_GLN_Contoso, Buyer_GLN_Northwind, ServiceName, Step

# Order-to-cash
from order_to_cash.scenario import browse_subscription, check_orders, get_steps, get_sub_key, \
    get_subscription_definitions, Module, new_over_limit_order, new_po_number, new_standard_order, Outcome, read_source, \
    read_trail, render_definitions, Source, State_Pending, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# The file of the definitions that activate the subscription of the receivables
_activation_file = 'order-to-cash-receivables.yaml'

# ################################################################################################################################
# ################################################################################################################################

def test_receivables_deployed_later(late_suite:'Suite') -> 'None':
    """ The integration runs without the receivables. Its subscription holds the invoices and the rejections
    as pending, and once the module is written to the pickup directory and the subscription is activated,
    they drain to the ledger.
    """
    client = late_suite.client
    assert not late_suite.is_deployed(ServiceName.Receivables)

    approved = [new_po_number('LATE'), new_po_number('LATE')]
    rejected_po = new_po_number('LATE-REJECTED')

    orders = [
        new_standard_order(approved[0], Buyer_GLN_Northwind),
        new_standard_order(approved[1], Buyer_GLN_Contoso),
        new_over_limit_order(rejected_po),
    ]

    late_suite.submit_many(orders)

    # The chain runs up to the receivables ..
    def _is_up_to_receivables() -> 'bool':
        steps = get_steps(read_trail(client))

        for po_number in approved:
            if Step.Invoicing not in steps.get(po_number, []):
                return False

        out = Step.Credit_Rejected in steps.get(rejected_po, [])
        return out

    wait_until(_is_up_to_receivables, 'The invoicing of the approved orders and the rejection of the other one')

    # .. where its subscription holds one message of each order.
    sub_key = get_sub_key(client, ServiceName.Receivables)

    def _are_all_pending() -> 'bool':
        page = browse_subscription(client, sub_key, State_Pending)
        out = page['total'] == len(orders)
        return out

    wait_until(_are_all_pending, 'The messages of all the orders pending for the receivables')

    # The receivables module is deployed through the pickup directory ..
    late_suite.environment.deploy(Module.Receivables, read_source(Source.Receivables))

    # .. its subscription is activated by enmasse ..
    definitions = render_definitions(late_suite.partner_password, is_receivables_active=True)
    _ = late_suite.environment.import_yaml(_activation_file, get_subscription_definitions(definitions))

    # .. and the pending messages drain to the ledger.
    expectations = {po_number: Outcome.Invoiced for po_number in approved}
    expectations[rejected_po] = Outcome.Rejected

    _ = check_orders(client, expectations)

# ################################################################################################################################
# ################################################################################################################################
