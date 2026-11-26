# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.models import Buyer_GLN_Contoso, Buyer_GLN_Fabrikam, Buyer_GLN_Northwind, LedgerKind, \
    Step

# Order-to-cash
from order_to_cash.scenario import check_orders, get_ledger_entries, get_trail_items, new_over_limit_order, \
    new_po_number, new_standard_order, Outcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

def test_order_over_the_credit_limit(suite:'Suite') -> 'None':
    """ An order above the credit that its buyer has left goes to the rejected branch and is recorded in the ledger,
    never reaching the fulfillment or the invoicing, while the orders submitted with it complete.
    """
    rejected_po = new_po_number('REJECTED')

    approved = {
        new_po_number('APPROVED'): Buyer_GLN_Northwind,
        new_po_number('APPROVED'): Buyer_GLN_Contoso,
        new_po_number('APPROVED'): Buyer_GLN_Fabrikam,
    }

    orders = [new_over_limit_order(rejected_po)]
    orders.extend(new_standard_order(po_number, buyer_gln) for po_number, buyer_gln in approved.items())

    suite.submit_many(orders)

    expectations = {po_number: Outcome.Invoiced for po_number in approved}
    expectations[rejected_po] = Outcome.Rejected

    trail = check_orders(suite.client, expectations)

    # The rejected order did not reach the fulfillment or the invoicing ..
    assert get_trail_items(trail, rejected_po, Step.Fulfillment) == []
    assert get_trail_items(trail, rejected_po, Step.Invoicing) == []

    # .. and the ledger has its rejection, with no amount owed.
    entries = get_ledger_entries(trail, rejected_po)

    assert entries[0]['kind'] == LedgerKind.Rejection
    assert entries[0]['buyer_gln'] == Buyer_GLN_Fabrikam
    assert entries[0]['amount_minor'] == 0

# ################################################################################################################################
# ################################################################################################################################
