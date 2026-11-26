# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The receivables of the order-to-cash integration, the last service of the chain. It is deployed in a module
# of its own, which lets a test start the integration without it and deploy it later.

# Zato
from zato.common.test.order_to_cash.control import record_step, wait_step_delay
from zato.common.test.order_to_cash.models import Invoice, is_in_ledger, new_invoice_entry, new_rejection_entry, \
    ServiceName, Step, Store
from zato.common.test.received_store import read_items, record
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class Receivables(Service):
    """ Posts an issued invoice to the ledger, or records a rejected order in it. A message that the ledger
    already has an entry for is not posted again.
    """
    name = ServiceName.Receivables

    def handle(self) -> 'None':

        wait_step_delay(self)

        message = self.request.input

        # The subscription delivers invoices and rejected orders, each rebuilt as its own model
        if isinstance(message, Invoice):
            entry = new_invoice_entry(message)
            step = Step.Ledger_Invoice
        else:
            entry = new_rejection_entry(message)
            step = Step.Ledger_Rejection

        entries = read_items(self, Store.Ledger)
        is_new = not is_in_ledger(entries, entry)

        if is_new:
            record(self, Store.Ledger, entry)

        record_step(self, step, message.po_number, is_new=is_new)

# ################################################################################################################################
# ################################################################################################################################
