# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.order_to_cash.models import accept_order, Allocation, allocate_line, ApprovedOrder, build_invoice, \
    build_ship_notice, Buyer_GLN_Contoso, Buyer_GLN_Fabrikam, Buyer_GLN_Northwind, Carrier, choose_carrier, decide_credit, \
    get_check_digit, get_due_date, get_tax, is_in_ledger, is_valid_gln, LedgerKind, new_invoice_entry, new_rejection_entry, \
    OrderValidationError, PurchaseOrder, RejectedOrder, ShipNotice, ShipNoticeLine, SKU_Book, SKU_Paper, SKU_Stapler, \
    SKU_Toner, UnknownSKUError, validate_order, Warehouse_Gdansk, Warehouse_Poznan, with_check_digit

# Order-to-cash
from order_to_cash.scenario import Freight_Lines, get_invalid_gln, new_order, new_standard_order, Order_Date, \
    Standard_Lines, Unknown_SKU, Unknown_SKU_Lines

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from order_to_cash.scenario import line_spec_list
    from zato.common.typing_ import anydict, dictlist

    line_spec_list = line_spec_list

# ################################################################################################################################
# ################################################################################################################################

# The GLN of the GS1 specification example, with its check digit
_gs1_example_digits = '590123412345'
_gs1_example_check_digit = 7

# A GLN with a valid check digit that belongs to no buyer
_unregistered_gln = with_check_digit('123456789012')

# The purchase order number of the tests
_po_number = 'PO-UNIT-0001'

# ################################################################################################################################
# ################################################################################################################################

def _new_purchase_order(data:'anydict') -> 'PurchaseOrder':
    out = PurchaseOrder.from_dict(data)
    return out

# ################################################################################################################################

def _new_approved(buyer_gln:'str', lines:'line_spec_list') -> 'ApprovedOrder':
    """ An order of the lines that the credit check approved.
    """
    order = _new_purchase_order(new_order(_po_number, buyer_gln, lines))
    accepted = accept_order(order)

    out = decide_credit(accepted)
    assert isinstance(out, ApprovedOrder), out

    return out

# ################################################################################################################################

def _new_notice_line(sku:'str', ordered:'int', shipped:'int', unit_price_minor:'int') -> 'ShipNoticeLine':
    out = ShipNoticeLine()
    out.line_number = 1
    out.sku = sku
    out.ordered_quantity = ordered
    out.shipped_quantity = shipped
    out.backordered_quantity = ordered - shipped
    out.unit_price_minor = unit_price_minor
    out.allocations = []

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGLN:

    def test_check_digit_of_the_gs1_example(self) -> 'None':
        assert get_check_digit(_gs1_example_digits) == _gs1_example_check_digit

    def test_with_check_digit_appends_it(self) -> 'None':
        assert with_check_digit(_gs1_example_digits) == f'{_gs1_example_digits}{_gs1_example_check_digit}'

    def test_buyer_glns_are_valid(self) -> 'None':
        for gln in (Buyer_GLN_Northwind, Buyer_GLN_Contoso, Buyer_GLN_Fabrikam):
            assert is_valid_gln(gln), gln

    def test_wrong_check_digit_is_invalid(self) -> 'None':
        assert not is_valid_gln(get_invalid_gln(Buyer_GLN_Northwind))

    def test_wrong_length_is_invalid(self) -> 'None':
        assert not is_valid_gln(Buyer_GLN_Northwind[:-1])
        assert not is_valid_gln(Buyer_GLN_Northwind + '0')

    def test_non_digits_are_invalid(self) -> 'None':
        assert not is_valid_gln('59012341234X7')

# ################################################################################################################################
# ################################################################################################################################

class TestValidation:

    def _assert_refused(self, data:'anydict', fragment:'str') -> 'None':
        order = _new_purchase_order(data)

        with pytest.raises(OrderValidationError) as info:
            validate_order(order)

        assert fragment in str(info.value), str(info.value)

# ################################################################################################################################

    def test_standard_order_is_valid(self) -> 'None':
        order = _new_purchase_order(new_standard_order(_po_number))
        validate_order(order)

    def test_order_without_number(self) -> 'None':
        self._assert_refused(new_standard_order(''), 'has no number')

    def test_order_number_too_long(self) -> 'None':
        self._assert_refused(new_standard_order('PO-' + 'X' * 40), 'longer than')

    def test_invalid_gln(self) -> 'None':
        data = new_order(_po_number, get_invalid_gln(Buyer_GLN_Northwind), Standard_Lines)
        self._assert_refused(data, 'invalid buyer GLN')

    def test_unknown_buyer(self) -> 'None':
        data = new_order(_po_number, _unregistered_gln, Standard_Lines)
        self._assert_refused(data, 'unknown buyer')

    def test_currency_other_than_contract(self) -> 'None':
        data = new_standard_order(_po_number)
        data['currency'] = 'USD'
        self._assert_refused(data, 'instead of `EUR`')

    def test_order_without_lines(self) -> 'None':
        data = new_order(_po_number, Buyer_GLN_Northwind, [])
        self._assert_refused(data, 'has no lines')

    def test_repeated_line_number(self) -> 'None':
        data = new_standard_order(_po_number)
        data['lines'][1]['line_number'] = 1
        self._assert_refused(data, 'repeats line 1')

    def test_line_without_sku(self) -> 'None':
        data = new_order(_po_number, Buyer_GLN_Northwind, [('', 1, 1_00)])
        self._assert_refused(data, 'has no SKU')

    def test_line_with_zero_quantity(self) -> 'None':
        data = new_order(_po_number, Buyer_GLN_Northwind, [(SKU_Paper, 0, 4_50)])
        self._assert_refused(data, 'has quantity 0')

    def test_line_with_zero_price(self) -> 'None':
        data = new_order(_po_number, Buyer_GLN_Northwind, [(SKU_Paper, 1, 0)])
        self._assert_refused(data, 'has price 0')

    def test_unknown_sku_passes_the_intake(self) -> 'None':
        """ The intake does not consult the catalog, so an unknown SKU is refused only by the fulfillment.
        """
        order = _new_purchase_order(new_order(_po_number, Buyer_GLN_Northwind, Unknown_SKU_Lines))
        validate_order(order)

# ################################################################################################################################
# ################################################################################################################################

class TestCredit:

    def test_accepted_order_has_its_id_and_value(self) -> 'None':
        accepted = accept_order(_new_purchase_order(new_standard_order(_po_number)))

        assert accepted.order_id == f'ORD-{_po_number}'
        assert accepted.net_total_minor == 329_98

    def test_order_within_credit_is_approved_with_terms(self) -> 'None':
        approved = _new_approved(Buyer_GLN_Northwind, Standard_Lines)
        assert approved.payment_terms_days == 30

    def test_order_equal_to_available_credit_is_approved(self) -> 'None':

        # Fabrikam has a limit of 1,500.00 and an open balance of 1,000.00
        approved = _new_approved(Buyer_GLN_Fabrikam, [(SKU_Stapler, 1, 500_00)])
        assert approved.net_total_minor == 500_00

    def test_order_above_available_credit_is_rejected(self) -> 'None':
        accepted = accept_order(_new_purchase_order(new_order(_po_number, Buyer_GLN_Fabrikam, [(SKU_Stapler, 1, 500_01)])))
        decision = decide_credit(accepted)

        assert isinstance(decision, RejectedOrder), decision
        assert decision.available_credit_minor == 500_00
        assert decision.net_total_minor == 500_01
        assert decision.po_number == _po_number

# ################################################################################################################################
# ################################################################################################################################

class TestAllocation:

    def _quantities(self, allocations:'list[Allocation]') -> 'list[tuple[str, int]]':
        out = [(allocation.warehouse, allocation.quantity) for allocation in allocations]
        return out

    def test_line_within_the_first_warehouse(self) -> 'None':
        allocations, backordered = allocate_line(SKU_Paper, 150)

        assert self._quantities(allocations) == [(Warehouse_Gdansk, 150)]
        assert backordered == 0

    def test_line_split_across_warehouses(self) -> 'None':
        allocations, backordered = allocate_line(SKU_Paper, 250)

        assert self._quantities(allocations) == [(Warehouse_Gdansk, 200), (Warehouse_Poznan, 50)]
        assert backordered == 0

    def test_line_above_all_stock_is_backordered(self) -> 'None':
        allocations, backordered = allocate_line(SKU_Toner, 120)

        assert self._quantities(allocations) == [(Warehouse_Gdansk, 50), (Warehouse_Poznan, 50)]
        assert backordered == 20

    def test_warehouse_without_stock_is_skipped(self) -> 'None':
        allocations, backordered = allocate_line(SKU_Stapler, 120)

        assert self._quantities(allocations) == [(Warehouse_Gdansk, 100)]
        assert backordered == 20

    def test_unknown_sku_is_a_permanent_error(self) -> 'None':
        with pytest.raises(UnknownSKUError):
            _ = allocate_line(Unknown_SKU, 1)

    def test_ship_notice_has_no_carrier_and_ships_on_the_order_date(self) -> 'None':
        notice = build_ship_notice(_new_approved(Buyer_GLN_Northwind, Standard_Lines))

        assert notice.carrier == Carrier.Unassigned
        assert notice.ship_date == Order_Date
        assert notice.asn_number == f'ASN-{_po_number}'
        assert notice.payment_terms_days == 30
        assert [line.shipped_quantity for line in notice.lines] == [10, 2, 3]

    def test_ship_notice_of_unknown_sku(self) -> 'None':
        approved = _new_approved(Buyer_GLN_Northwind, Unknown_SKU_Lines)

        with pytest.raises(UnknownSKUError):
            _ = build_ship_notice(approved)

    def test_carrier_by_weight(self) -> 'None':
        parcel = build_ship_notice(_new_approved(Buyer_GLN_Northwind, Standard_Lines))
        freight = build_ship_notice(_new_approved(Buyer_GLN_Northwind, Freight_Lines))

        assert choose_carrier(parcel.lines) == Carrier.Parcel
        assert choose_carrier(freight.lines) == Carrier.Freight

# ################################################################################################################################
# ################################################################################################################################

class TestInvoice:

    def test_tax_rounds_half_up(self) -> 'None':
        assert get_tax(50, 2300) == 12
        assert get_tax(49, 2300) == 11
        assert get_tax(17998, 2300) == 4140
        assert get_tax(10500, 500) == 525

    def test_due_dates_by_payment_terms(self) -> 'None':
        assert get_due_date(Order_Date, 30) == '2026-12-02'
        assert get_due_date(Order_Date, 14) == '2026-11-16'
        assert get_due_date(Order_Date, 60) == '2027-01-01'

    def test_invoice_of_the_standard_order(self) -> 'None':
        notice = build_ship_notice(_new_approved(Buyer_GLN_Northwind, Standard_Lines))
        invoice = build_invoice(notice)

        assert invoice.invoice_number == f'INV-{_po_number}'
        assert invoice.invoice_date == Order_Date
        assert invoice.due_date == '2026-12-02'

        # Paper 45.00 + 10.35, toner 179.98 + 41.40, books at the reduced rate 105.00 + 5.25
        assert [line.net_minor for line in invoice.lines] == [45_00, 179_98, 105_00]
        assert [line.tax_minor for line in invoice.lines] == [10_35, 41_40, 5_25]

        assert invoice.net_total_minor == 329_98
        assert invoice.tax_total_minor == 57_00
        assert invoice.gross_total_minor == 386_98

    def test_invoice_of_partly_backordered_line(self) -> 'None':
        notice = build_ship_notice(_new_approved(Buyer_GLN_Contoso, [(SKU_Toner, 120, 89_99)]))
        invoice = build_invoice(notice)

        assert invoice.due_date == '2026-11-16'
        assert [line.quantity for line in invoice.lines] == [100]
        assert invoice.net_total_minor == 8999_00

    def test_line_backordered_in_full_is_not_invoiced(self) -> 'None':
        notice = ShipNotice()
        notice.asn_number = f'ASN-{_po_number}'
        notice.order_id = f'ORD-{_po_number}'
        notice.po_number = _po_number
        notice.buyer_gln = Buyer_GLN_Northwind
        notice.currency = 'EUR'
        notice.ship_date = Order_Date
        notice.payment_terms_days = 30
        notice.carrier = Carrier.Unassigned
        notice.lines = [
            _new_notice_line(SKU_Paper, 10, 10, 4_50),
            _new_notice_line(SKU_Book, 5, 0, 35_00),
        ]

        invoice = build_invoice(notice)

        assert [line.sku for line in invoice.lines] == [SKU_Paper]
        assert invoice.gross_total_minor == 55_35

# ################################################################################################################################
# ################################################################################################################################

class TestLedger:

    def test_invoice_is_posted_once(self) -> 'None':
        invoice = build_invoice(build_ship_notice(_new_approved(Buyer_GLN_Northwind, Standard_Lines)))
        entry = new_invoice_entry(invoice)

        entries:'dictlist' = []
        assert not is_in_ledger(entries, entry)

        entries.append(entry)
        assert is_in_ledger(entries, new_invoice_entry(invoice))

    def test_rejection_is_recorded_once(self) -> 'None':
        accepted = accept_order(_new_purchase_order(new_order(_po_number, Buyer_GLN_Fabrikam, [(SKU_Toner, 10, 89_99)])))
        rejected = decide_credit(accepted)
        assert isinstance(rejected, RejectedOrder), rejected

        entry = new_rejection_entry(rejected)
        entries = [entry]

        assert is_in_ledger(entries, new_rejection_entry(rejected))

    def test_entries_of_different_kinds_are_independent(self) -> 'None':
        invoice = build_invoice(build_ship_notice(_new_approved(Buyer_GLN_Northwind, Standard_Lines)))

        invoice_entry = new_invoice_entry(invoice)
        rejection_entry = dict(invoice_entry, kind=LedgerKind.Rejection)

        assert not is_in_ledger([invoice_entry], rejection_entry)

# ################################################################################################################################
# ################################################################################################################################
