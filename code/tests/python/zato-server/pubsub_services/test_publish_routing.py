# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.order_to_cash.control import count_pending_failures, Fault, fail_attempts
from zato.common.test.order_to_cash.models import accept_order, AcceptedOrder, ApprovedOrder, build_invoice, \
    build_ship_notice, Buyer_GLN_Fabrikam, Buyer_GLN_Northwind, Carrier, decide_credit, get_intake_msg_id, Invoice, \
    LedgerKind, OrderValidationError, PurchaseOrder, RejectedOrder, Retry, ShipNotice, Step, Store, Topic, \
    TransientOutageError, UnknownSKUError
from zato.common.test.received_store import read_items

# Order-to-cash
from order_to_cash.scenario import get_publications, new_invalid_order, new_order, new_over_limit_order, \
    new_standard_order, new_unit_service, new_unknown_sku_order, Standard_Lines, Unit_CID
from order_to_cash.services import CreditCheck, Invoicing, OrderIntake
from order_to_cash.services_broken import Source as Broken_Source
from order_to_cash.services_fulfillment import Fulfillment as FulfillmentFirst
from order_to_cash.services_fulfillment_carrier import Fulfillment as FulfillmentCarrier
from order_to_cash.services_receivables import Receivables

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

# The purchase order number of the tests
_po_number = 'PO-ROUTING-0001'

# ################################################################################################################################
# ################################################################################################################################

def _single_publication(service:'any_') -> 'tuple[str, any_, anydict]':
    publications = get_publications(service)
    assert len(publications) == 1, publications

    out = publications[0]
    return out

# ################################################################################################################################

def _assert_metadata(kwargs:'anydict') -> 'None':
    """ Every publication of the integration has the purchase order number as its correlation ID,
    the retry policy of the integration and the CID of the service.
    """
    assert kwargs['correl_id'] == _po_number
    assert kwargs['max_retries'] == Retry.Max_Retries
    assert kwargs['retry_sleep_time'] == Retry.Sleep_Time
    assert kwargs['cid'] == Unit_CID

# ################################################################################################################################

def _trail_steps(service:'any_') -> 'list[str]':
    out = [item['step'] for item in read_items(service, Store.Trail)]
    return out

# ################################################################################################################################

def _purchase_order(data:'anydict') -> 'PurchaseOrder':
    out = PurchaseOrder.from_dict(data)
    return out

# ################################################################################################################################

def _accepted(data:'anydict') -> 'AcceptedOrder':
    out = accept_order(_purchase_order(data))
    return out

# ################################################################################################################################

def _approved(data:'anydict') -> 'ApprovedOrder':
    out = decide_credit(_accepted(data))
    assert isinstance(out, ApprovedOrder), out

    return out

# ################################################################################################################################

def _rejected() -> 'RejectedOrder':
    out = decide_credit(_accepted(new_over_limit_order(_po_number)))
    assert isinstance(out, RejectedOrder), out

    return out

# ################################################################################################################################

def _invoice() -> 'Invoice':
    out = build_invoice(build_ship_notice(_approved(new_standard_order(_po_number))))
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def base_dir(tmp_path:'Path') -> 'str':
    """ The server directory of the services, which holds their stores and the control files.
    """
    out = str(tmp_path)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOrderIntake:

    def test_accepted_order_is_published_under_its_message_id(self, base_dir:'str') -> 'None':
        service = new_unit_service(OrderIntake, base_dir, _purchase_order(new_standard_order(_po_number)))
        service.handle()

        topic_name, data, kwargs = _single_publication(service)

        assert topic_name == Topic.Order_Accepted
        assert isinstance(data, AcceptedOrder), data
        assert data.po_number == _po_number

        assert kwargs['msg_id'] == get_intake_msg_id(_po_number)
        _assert_metadata(kwargs)

        assert _trail_steps(service) == [Step.Intake]

    def test_invalid_order_publishes_nothing(self, base_dir:'str') -> 'None':
        service = new_unit_service(OrderIntake, base_dir, _purchase_order(new_invalid_order(_po_number)))

        with pytest.raises(OrderValidationError):
            service.handle()

        assert get_publications(service) == []
        assert _trail_steps(service) == []

    def test_retry_after_publication_uses_the_same_message_id(self, base_dir:'str') -> 'None':
        fail_attempts(base_dir, Fault.Intake_After_Publish, _po_number, 1)

        order = _purchase_order(new_standard_order(_po_number))

        # The first attempt publishes and then fails ..
        first = new_unit_service(OrderIntake, base_dir, order)

        with pytest.raises(TransientOutageError):
            first.handle()

        # .. and the retry publishes under the same message ID, which the publication of the first attempt has.
        second = new_unit_service(OrderIntake, base_dir, order)
        second.handle()

        _, _, first_kwargs = _single_publication(first)
        _, _, second_kwargs = _single_publication(second)

        assert first_kwargs['msg_id'] == second_kwargs['msg_id'] == get_intake_msg_id(_po_number)
        assert count_pending_failures(base_dir, Fault.Intake_After_Publish, _po_number) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCreditCheck:

    def test_approved_order(self, base_dir:'str') -> 'None':
        service = new_unit_service(CreditCheck, base_dir, _accepted(new_standard_order(_po_number)))
        service.handle()

        topic_name, data, kwargs = _single_publication(service)

        assert topic_name == Topic.Order_Approved
        assert isinstance(data, ApprovedOrder), data
        assert 'msg_id' not in kwargs
        _assert_metadata(kwargs)

        assert _trail_steps(service) == [Step.Credit_Approved]

    def test_rejected_order(self, base_dir:'str') -> 'None':
        service = new_unit_service(CreditCheck, base_dir, _accepted(new_over_limit_order(_po_number)))
        service.handle()

        topic_name, data, kwargs = _single_publication(service)

        assert topic_name == Topic.Order_Rejected
        assert isinstance(data, RejectedOrder), data
        assert data.buyer_gln == Buyer_GLN_Fabrikam
        _assert_metadata(kwargs)

        assert _trail_steps(service) == [Step.Credit_Rejected]

# ################################################################################################################################
# ################################################################################################################################

class TestFulfillment:

    def test_first_version_ships_without_carrier(self, base_dir:'str') -> 'None':
        service = new_unit_service(FulfillmentFirst, base_dir, _approved(new_standard_order(_po_number)))
        service.handle()

        topic_name, data, kwargs = _single_publication(service)

        assert topic_name == Topic.Order_Shipped
        assert isinstance(data, ShipNotice), data
        assert data.carrier == Carrier.Unassigned
        _assert_metadata(kwargs)

        assert _trail_steps(service) == [Step.Fulfillment]

    def test_second_version_assigns_carrier(self, base_dir:'str') -> 'None':
        service = new_unit_service(FulfillmentCarrier, base_dir, _approved(new_standard_order(_po_number)))
        service.handle()

        _, data, _ = _single_publication(service)
        assert data.carrier == Carrier.Parcel

        trail = read_items(service, Store.Trail)
        assert trail[0]['version'] == FulfillmentCarrier.trail_version

    def test_unknown_sku_publishes_nothing(self, base_dir:'str') -> 'None':
        service = new_unit_service(FulfillmentFirst, base_dir, _approved(new_unknown_sku_order(_po_number)))

        with pytest.raises(UnknownSKUError):
            service.handle()

        assert get_publications(service) == []
        assert _trail_steps(service) == []

    def test_transient_outage_then_success(self, base_dir:'str') -> 'None':
        fail_attempts(base_dir, Fault.Fulfillment, _po_number, 2)

        order = _approved(new_standard_order(_po_number))

        # Two attempts fail and publish nothing ..
        for _ in range(2):
            failed = new_unit_service(FulfillmentFirst, base_dir, order)

            with pytest.raises(TransientOutageError):
                failed.handle()

            assert get_publications(failed) == []

        # .. and the third one publishes the ship notice.
        service = new_unit_service(FulfillmentFirst, base_dir, order)
        service.handle()

        topic_name, _, _ = _single_publication(service)
        assert topic_name == Topic.Order_Shipped

        assert _trail_steps(service) == [Step.Fulfillment]

# ################################################################################################################################
# ################################################################################################################################

class TestInvoicing:

    def test_invoice_is_issued(self, base_dir:'str') -> 'None':
        notice = build_ship_notice(_approved(new_standard_order(_po_number)))

        service = new_unit_service(Invoicing, base_dir, notice)
        service.handle()

        topic_name, data, kwargs = _single_publication(service)

        assert topic_name == Topic.Invoice_Issued
        assert isinstance(data, Invoice), data
        assert data.invoice_number == f'INV-{_po_number}'
        _assert_metadata(kwargs)

        assert _trail_steps(service) == [Step.Invoicing]

    def test_transient_outage_publishes_nothing(self, base_dir:'str') -> 'None':
        fail_attempts(base_dir, Fault.Invoicing, _po_number, 1)

        notice = build_ship_notice(_approved(new_standard_order(_po_number)))
        service = new_unit_service(Invoicing, base_dir, notice)

        with pytest.raises(TransientOutageError):
            service.handle()

        assert get_publications(service) == []
        assert count_pending_failures(base_dir, Fault.Invoicing, _po_number) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestReceivables:

    def test_invoice_is_posted_once(self, base_dir:'str') -> 'None':
        invoice = _invoice()

        # The same invoice is delivered twice ..
        services = [new_unit_service(Receivables, base_dir, invoice) for _ in range(2)]

        for service in services:
            service.handle()
            assert get_publications(service) == []

        # .. and the ledger has one entry of it.
        ledger = read_items(services[0], Store.Ledger)

        assert len(ledger) == 1, ledger
        assert ledger[0]['kind'] == LedgerKind.Invoice
        assert ledger[0]['amount_minor'] == invoice.gross_total_minor

        trail = read_items(services[0], Store.Trail)
        assert [item['is_new'] for item in trail] == [True, False]

    def test_rejection_is_recorded(self, base_dir:'str') -> 'None':
        service = new_unit_service(Receivables, base_dir, _rejected())
        service.handle()

        ledger = read_items(service, Store.Ledger)

        assert len(ledger) == 1, ledger
        assert ledger[0]['kind'] == LedgerKind.Rejection
        assert _trail_steps(service) == [Step.Ledger_Rejection]

    def test_invoices_of_different_orders_are_both_posted(self, base_dir:'str') -> 'None':
        first = _invoice()

        other_order = new_order('PO-ROUTING-0002', Buyer_GLN_Northwind, Standard_Lines)
        second = build_invoice(build_ship_notice(_approved(other_order)))

        services = [new_unit_service(Receivables, base_dir, invoice) for invoice in (first, second)]

        for service in services:
            service.handle()

        ledger = read_items(services[0], Store.Ledger)
        assert [entry['key'] for entry in ledger] == [first.invoice_number, second.invoice_number]

# ################################################################################################################################
# ################################################################################################################################

class TestBrokenModule:

    def test_source_has_a_syntax_error(self) -> 'None':
        with pytest.raises(SyntaxError):
            _ = compile(Broken_Source, 'order_to_cash_fulfillment.py', 'exec')

# ################################################################################################################################
# ################################################################################################################################
