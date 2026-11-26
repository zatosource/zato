# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.order_to_cash.models import Buyer_GLN_Contoso, Buyer_GLN_Fabrikam, Buyer_GLN_Northwind, Carrier, \
    get_invoice_number, LedgerKind, Step

# Order-to-cash
from order_to_cash.scenario import check_orders, get_ledger_entries, get_trail_items, new_po_number, new_standard_order, \
    Outcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite
    from zato.common.typing_ import strstrdict

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

# The gross total of the standard order - 329.98 net and 57.00 of tax
_standard_gross_minor = 386_98

# The due date of an invoice of the standard order, by the payment terms of each buyer
_due_dates = {
    Buyer_GLN_Northwind: '2026-12-02',
    Buyer_GLN_Contoso:   '2026-11-16',
    Buyer_GLN_Fabrikam:  '2027-01-01',
}

# How many orders are submitted at the same time
_concurrent_orders = 50

# ################################################################################################################################
# ################################################################################################################################

def test_single_order(suite:'Suite') -> 'None':
    """ One order passes through all five services and the ledger has its invoice.
    """
    po_number = new_po_number('HAPPY')

    suite.submit(new_standard_order(po_number))
    trail = check_orders(suite.client, {po_number: Outcome.Invoiced})

    # The first version of the fulfillment shipped it without a carrier ..
    fulfillment = get_trail_items(trail, po_number, Step.Fulfillment)

    assert len(fulfillment) == 1, fulfillment
    assert fulfillment[0]['version'] == 1
    assert fulfillment[0]['carrier'] == Carrier.Unassigned

    # .. the invoicing issued the invoice under the number of the order ..
    invoicing = get_trail_items(trail, po_number, Step.Invoicing)

    assert len(invoicing) == 1, invoicing
    assert invoicing[0]['invoice_number'] == get_invoice_number(po_number)
    assert invoicing[0]['gross_total_minor'] == _standard_gross_minor

    # .. and the receivables posted it to the account of the buyer.
    entries = get_ledger_entries(trail, po_number)
    entry = entries[0]

    assert entry['kind'] == LedgerKind.Invoice
    assert entry['key'] == get_invoice_number(po_number)
    assert entry['buyer_gln'] == Buyer_GLN_Northwind
    assert entry['currency'] == 'EUR'
    assert entry['amount_minor'] == _standard_gross_minor
    assert entry['due_date'] == _due_dates[Buyer_GLN_Northwind]

# ################################################################################################################################

def test_concurrent_orders_of_several_partners(suite:'Suite') -> 'None':
    """ Fifty orders of three trading partners, submitted concurrently, all complete with the terms of their buyers.
    """
    buyers = list(_due_dates)

    orders = []
    buyer_by_po:'strstrdict' = {}

    for idx in range(_concurrent_orders):
        buyer_gln = buyers[idx % len(buyers)]
        po_number = new_po_number('CONCURRENT')

        orders.append(new_standard_order(po_number, buyer_gln))
        buyer_by_po[po_number] = buyer_gln

    suite.submit_many(orders)

    expectations = {po_number: Outcome.Invoiced for po_number in buyer_by_po}
    trail = check_orders(suite.client, expectations)

    for po_number, buyer_gln in buyer_by_po.items():
        entry = get_ledger_entries(trail, po_number)[0]

        assert entry['buyer_gln'] == buyer_gln
        assert entry['amount_minor'] == _standard_gross_minor
        assert entry['due_date'] == _due_dates[buyer_gln]

# ################################################################################################################################
# ################################################################################################################################
