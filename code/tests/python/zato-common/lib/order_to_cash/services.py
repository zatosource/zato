# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The intake, the credit check and the invoicing of the order-to-cash integration, deployed to a test server
# through its pickup directory. Each service passes its result to the next one with self.publish only.

# Zato
from zato.common.test.order_to_cash.control import claim_failure, Fault, record_step, wait_step_delay
from zato.common.test.order_to_cash.models import accept_order, ApprovedOrder, build_invoice, decide_credit, \
    get_intake_msg_id, PurchaseOrder, Retry, ServiceName, Step, Topic, TransientOutageError
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class OrderIntake(Service):
    """ Accepts a purchase order that a trading partner submitted to the queued REST channel.
    """
    name = ServiceName.Order_Intake

    class IO:
        input = PurchaseOrder

    def handle(self) -> 'None':

        wait_step_delay(self)

        # Raises an exception for an order that cannot be accepted, which the queue of the channel retries
        accepted = accept_order(self.request.input)
        po_number = accepted.po_number

        record_step(self, Step.Intake, po_number, order_id=accepted.order_id, net_total_minor=accepted.net_total_minor)

        # Each attempt of the same purchase order publishes under the same message ID ..
        _ = self.publish(
            Topic.Order_Accepted,
            accepted,
            correl_id=po_number,
            msg_id=get_intake_msg_id(po_number),
            max_retries=Retry.Max_Retries,
            retry_sleep_time=Retry.Sleep_Time,
        )

        # .. so an attempt that fails after it published does not publish the order again when the queue retries it.
        if claim_failure(self, Fault.Intake_After_Publish, po_number):
            raise TransientOutageError(f'The intake failed after it published PO `{po_number}`')

# ################################################################################################################################
# ################################################################################################################################

class CreditCheck(Service):
    """ Approves or rejects an accepted order by the credit that its buyer has left.
    """
    name = ServiceName.Credit_Check

    def handle(self) -> 'None':

        wait_step_delay(self)

        order = self.request.input
        po_number = order.po_number

        decision = decide_credit(order)

        if isinstance(decision, ApprovedOrder):
            step = Step.Credit_Approved
            topic_name = Topic.Order_Approved
        else:
            step = Step.Credit_Rejected
            topic_name = Topic.Order_Rejected

        record_step(self, step, po_number, net_total_minor=order.net_total_minor)

        _ = self.publish(
            topic_name,
            decision,
            correl_id=po_number,
            max_retries=Retry.Max_Retries,
            retry_sleep_time=Retry.Sleep_Time,
        )

# ################################################################################################################################
# ################################################################################################################################

class Invoicing(Service):
    """ Issues the invoice of a shipped order.
    """
    name = ServiceName.Invoicing

    def handle(self) -> 'None':

        wait_step_delay(self)

        notice = self.request.input
        po_number = notice.po_number

        # The ERP is unavailable for as many attempts as the control files say
        if claim_failure(self, Fault.Invoicing, po_number):
            raise TransientOutageError(f'The ERP is unavailable for PO `{po_number}`')

        invoice = build_invoice(notice)

        record_step(
            self,
            Step.Invoicing,
            po_number,
            invoice_number=invoice.invoice_number,
            gross_total_minor=invoice.gross_total_minor,
            carrier=invoice.carrier,
        )

        _ = self.publish(
            Topic.Invoice_Issued,
            invoice,
            correl_id=po_number,
            max_retries=Retry.Max_Retries,
            retry_sleep_time=Retry.Sleep_Time,
        )

# ################################################################################################################################
# ################################################################################################################################
