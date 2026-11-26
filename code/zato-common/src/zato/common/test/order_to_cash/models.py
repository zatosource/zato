# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The messages and the business rules of the order-to-cash integration of the pub/sub service tests. The services
# of the integration run in a test server, which rebuilds the messages of this module on delivery, and the tests
# run in the test process, and both import this module.

# stdlib
from dataclasses import dataclass
from datetime import date, timedelta

# Zato
from zato.common.marshal_.api import Model
from zato.common.typing_ import list_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

stock_list      = list['tuple[str, int]']
allocation_list = list['Allocation']
order_line_list = list['OrderLine']
notice_lines    = list['ShipNoticeLine']
buyer_dict      = dict[str, 'BuyerAccount']
catalog_dict    = dict[str, 'CatalogItem']
stock_dict      = dict[str, stock_list]

# ################################################################################################################################
# ################################################################################################################################

class Topic:
    """ The topics between the services of the integration.
    """
    Order_Accepted = 'order-to-cash.order.accepted'
    Order_Approved = 'order-to-cash.order.approved'
    Order_Rejected = 'order-to-cash.order.rejected'
    Order_Shipped  = 'order-to-cash.order.shipped'
    Invoice_Issued = 'order-to-cash.invoice.issued'

# ################################################################################################################################

class ServiceName:
    """ The services of the integration.
    """
    Order_Intake = 'order-to-cash.order-intake'
    Credit_Check = 'order-to-cash.credit-check'
    Fulfillment  = 'order-to-cash.fulfillment'
    Invoicing    = 'order-to-cash.invoicing'
    Receivables  = 'order-to-cash.receivables'
    Read_Trail   = 'order-to-cash.read-trail'

# ################################################################################################################################

class Step:
    """ The steps that the services record in the trail of an order.
    """
    Intake           = 'intake'
    Credit_Approved  = 'credit-approved'
    Credit_Rejected  = 'credit-rejected'
    Fulfillment      = 'fulfillment'
    Invoicing        = 'invoicing'
    Ledger_Invoice   = 'ledger-invoice'
    Ledger_Rejection = 'ledger-rejection'

# ################################################################################################################################

class Store:
    """ The stores of zato.common.test.received_store that the services write to.
    """
    Trail  = 'order-to-cash-trail'
    Ledger = 'order-to-cash-ledger'

# ################################################################################################################################

class LedgerKind:
    """ The kinds of ledger entries of the receivables service.
    """
    Invoice   = 'invoice'
    Rejection = 'rejection'

# ################################################################################################################################

class Carrier:
    """ The carriers that the second version of the fulfillment service assigns, and the value of a ship notice
    without an assigned carrier.
    """
    Unassigned = ''
    Parcel     = 'DPD-PARCEL'
    Freight    = 'DHL-FREIGHT'

# ################################################################################################################################

class Retry:
    """ The retry policy of every publication of the integration.
    """
    Max_Retries = 3
    Sleep_Time  = 1

# ################################################################################################################################
# ################################################################################################################################

# The length of a GLN with its check digit
_gln_length = 13

# The longest purchase order number that the intake accepts
_po_number_max_length = 35

# The divisor of tax rates, which are expressed in basis points
_basis_points = 10_000

# The total weight of a shipment above which it travels by freight, in grams
_freight_threshold_grams = 100_000

# The prefixes of the identifiers that the services assign to an order
_order_id_prefix   = 'ORD-'
_asn_number_prefix = 'ASN-'
_invoice_prefix    = 'INV-'
_msg_id_prefix     = 'order-to-cash.accepted.'

# ################################################################################################################################
# ################################################################################################################################

class OrderValidationError(Exception):
    """ A purchase order that the intake refuses.
    """

# ################################################################################################################################

class UnknownSKUError(Exception):
    """ A line of an order whose SKU no warehouse stocks, which no retry resolves.
    """

# ################################################################################################################################

class TransientOutageError(Exception):
    """ A backend system of a step that is unavailable for a moment, which a retry resolves.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BuyerAccount:
    """ The contract of a trading partner - its currency, its credit and its payment terms.
    """
    name: str
    currency: str
    credit_limit_minor: int
    open_balance_minor: int
    payment_terms_days: int

# ################################################################################################################################

@dataclass(init=False)
class CatalogItem:
    """ A product that the warehouses stock, with the tax rate in basis points and the shipping weight of one unit.
    """
    tax_rate_bp: int
    weight_grams: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OrderLine(Model):
    line_number: int
    sku: str
    quantity: int
    unit_price_minor: int

# ################################################################################################################################

@dataclass(init=False)
class PurchaseOrder(Model):
    po_number: str
    buyer_gln: str
    currency: str
    order_date: str
    lines: list_[OrderLine]

# ################################################################################################################################

@dataclass(init=False)
class AcceptedOrder(Model):
    order_id: str
    po_number: str
    buyer_gln: str
    currency: str
    order_date: str
    net_total_minor: int
    lines: list_[OrderLine]

# ################################################################################################################################

@dataclass(init=False)
class ApprovedOrder(AcceptedOrder):
    payment_terms_days: int

# ################################################################################################################################

@dataclass(init=False)
class RejectedOrder(Model):
    order_id: str
    po_number: str
    buyer_gln: str
    currency: str
    net_total_minor: int
    available_credit_minor: int
    reason: str

# ################################################################################################################################

@dataclass(init=False)
class Allocation(Model):
    warehouse: str
    quantity: int

# ################################################################################################################################

@dataclass(init=False)
class ShipNoticeLine(Model):
    line_number: int
    sku: str
    ordered_quantity: int
    shipped_quantity: int
    backordered_quantity: int
    unit_price_minor: int
    allocations: list_[Allocation]

# ################################################################################################################################

@dataclass(init=False)
class ShipNotice(Model):
    asn_number: str
    order_id: str
    po_number: str
    buyer_gln: str
    currency: str
    ship_date: str
    payment_terms_days: int
    carrier: str
    lines: list_[ShipNoticeLine]

# ################################################################################################################################

@dataclass(init=False)
class InvoiceLine(Model):
    line_number: int
    sku: str
    quantity: int
    unit_price_minor: int
    net_minor: int
    tax_rate_bp: int
    tax_minor: int

# ################################################################################################################################

@dataclass(init=False)
class Invoice(Model):
    invoice_number: str
    order_id: str
    po_number: str
    buyer_gln: str
    currency: str
    invoice_date: str
    due_date: str
    carrier: str
    net_total_minor: int
    tax_total_minor: int
    gross_total_minor: int
    lines: list_[InvoiceLine]

# ################################################################################################################################
# ################################################################################################################################

def get_check_digit(digits:'str') -> 'int':
    """ Returns the GS1 check digit of the digits of a GLN without its check digit.
    """
    total = 0

    # The weights alternate between 3 and 1, beginning with 3 at the rightmost digit ..
    for idx, digit in enumerate(reversed(digits)):
        weight = 3 if idx % 2 == 0 else 1
        total += int(digit) * weight

    # .. and the check digit brings the weighted sum up to a multiple of ten.
    out = (10 - total % 10) % 10
    return out

# ################################################################################################################################

def with_check_digit(digits:'str') -> 'str':
    """ Returns a GLN that consists of the given digits and their check digit.
    """
    check_digit = get_check_digit(digits)

    out = f'{digits}{check_digit}'
    return out

# ################################################################################################################################

def is_valid_gln(gln:'str') -> 'bool':
    """ Returns whether a GLN has thirteen digits, the last of which is the check digit of the others.
    """
    if len(gln) != _gln_length:
        return False

    if not gln.isdigit():
        return False

    out = get_check_digit(gln[:-1]) == int(gln[-1])
    return out

# ################################################################################################################################

def _new_buyer(name:'str', currency:'str', credit_limit:'int', open_balance:'int', payment_terms_days:'int') -> 'BuyerAccount':
    out = BuyerAccount()
    out.name = name
    out.currency = currency
    out.credit_limit_minor = credit_limit
    out.open_balance_minor = open_balance
    out.payment_terms_days = payment_terms_days

    return out

# ################################################################################################################################

def _new_catalog_item(tax_rate_bp:'int', weight_grams:'int') -> 'CatalogItem':
    out = CatalogItem()
    out.tax_rate_bp = tax_rate_bp
    out.weight_grams = weight_grams

    return out

# ################################################################################################################################
# ################################################################################################################################

# The GLNs of the trading partners
Buyer_GLN_Northwind = with_check_digit('590123412345')
Buyer_GLN_Contoso   = with_check_digit('400638133393')
Buyer_GLN_Fabrikam  = with_check_digit('871234567890')

# The contracts of the trading partners, by GLN
Buyers:'buyer_dict' = {
    Buyer_GLN_Northwind: _new_buyer('Northwind Traders', 'EUR', 50_000_00, 5_000_00, 30),
    Buyer_GLN_Contoso:   _new_buyer('Contoso Retail',    'EUR', 20_000_00, 0,        14),
    Buyer_GLN_Fabrikam:  _new_buyer('Fabrikam Office',   'EUR',  1_500_00, 1_000_00, 60),
}

# The SKUs of the catalog
SKU_Paper   = 'SKU-PAPER-A4'
SKU_Toner   = 'SKU-TONER-BK'
SKU_Stapler = 'SKU-STAPLER'
SKU_Book    = 'SKU-BOOK-GS1'

# The products that the warehouses stock, by SKU - books are taxed at the reduced rate
Catalog:'catalog_dict' = {
    SKU_Paper:   _new_catalog_item(2300, 2500),
    SKU_Toner:   _new_catalog_item(2300, 900),
    SKU_Stapler: _new_catalog_item(2300, 400),
    SKU_Book:    _new_catalog_item(500,  700),
}

# The stock of each SKU, by warehouse, in the order in which the warehouses are allocated from
Warehouse_Gdansk = 'WH-GDANSK'
Warehouse_Poznan = 'WH-POZNAN'

Warehouse_Stock:'stock_dict' = {
    SKU_Paper:   [(Warehouse_Gdansk, 200), (Warehouse_Poznan, 300)],
    SKU_Toner:   [(Warehouse_Gdansk, 50),  (Warehouse_Poznan, 50)],
    SKU_Stapler: [(Warehouse_Gdansk, 100), (Warehouse_Poznan, 0)],
    SKU_Book:    [(Warehouse_Gdansk, 20),  (Warehouse_Poznan, 30)],
}

# ################################################################################################################################
# ################################################################################################################################

def get_order_id(po_number:'str') -> 'str':
    out = f'{_order_id_prefix}{po_number}'
    return out

# ################################################################################################################################

def get_asn_number(po_number:'str') -> 'str':
    out = f'{_asn_number_prefix}{po_number}'
    return out

# ################################################################################################################################

def get_invoice_number(po_number:'str') -> 'str':
    out = f'{_invoice_prefix}{po_number}'
    return out

# ################################################################################################################################

def get_intake_msg_id(po_number:'str') -> 'str':
    """ The message ID of the publication of an accepted order, the same for each attempt of the same purchase order.
    """
    out = f'{_msg_id_prefix}{po_number}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def validate_order(order:'PurchaseOrder') -> 'None':
    """ Raises OrderValidationError if a purchase order does not identify a known buyer in the currency of its contract,
    or if it has no lines, lines with the same number, or lines without a SKU, a quantity or a price.
    """
    po_number = order.po_number

    if not po_number:
        raise OrderValidationError('The purchase order has no number')

    if len(po_number) > _po_number_max_length:
        raise OrderValidationError(f'PO `{po_number}` is longer than {_po_number_max_length} characters')

    if not is_valid_gln(order.buyer_gln):
        raise OrderValidationError(f'PO `{po_number}` has an invalid buyer GLN `{order.buyer_gln}`')

    if order.buyer_gln not in Buyers:
        raise OrderValidationError(f'PO `{po_number}` names an unknown buyer `{order.buyer_gln}`')

    buyer = Buyers[order.buyer_gln]

    if order.currency != buyer.currency:
        raise OrderValidationError(f'PO `{po_number}` is in `{order.currency}` instead of `{buyer.currency}`')

    if not order.lines:
        raise OrderValidationError(f'PO `{po_number}` has no lines')

    line_numbers:'set[int]' = set()

    for line in order.lines:

        if line.line_number in line_numbers:
            raise OrderValidationError(f'PO `{po_number}` repeats line {line.line_number}')

        line_numbers.add(line.line_number)

        if not line.sku:
            raise OrderValidationError(f'PO `{po_number}` line {line.line_number} has no SKU')

        if line.quantity <= 0:
            raise OrderValidationError(f'PO `{po_number}` line {line.line_number} has quantity {line.quantity}')

        if line.unit_price_minor <= 0:
            raise OrderValidationError(f'PO `{po_number}` line {line.line_number} has price {line.unit_price_minor}')

# ################################################################################################################################

def get_net_total(lines:'order_line_list') -> 'int':
    """ Returns the value of the lines of an order before tax, in minor units.
    """
    out = 0

    for line in lines:
        out += line.quantity * line.unit_price_minor

    return out

# ################################################################################################################################

def accept_order(order:'PurchaseOrder') -> 'AcceptedOrder':
    """ Validates a purchase order and returns it as an accepted order with its order ID and its value.
    """
    validate_order(order)

    out = AcceptedOrder()
    out.order_id = get_order_id(order.po_number)
    out.po_number = order.po_number
    out.buyer_gln = order.buyer_gln
    out.currency = order.currency
    out.order_date = order.order_date
    out.net_total_minor = get_net_total(order.lines)
    out.lines = order.lines

    return out

# ################################################################################################################################

def get_available_credit(buyer:'BuyerAccount') -> 'int':
    out = buyer.credit_limit_minor - buyer.open_balance_minor
    return out

# ################################################################################################################################

def decide_credit(order:'AcceptedOrder') -> 'ApprovedOrder | RejectedOrder':
    """ Approves an order whose value fits in the credit that the buyer has left, and rejects any other.
    """
    buyer = Buyers[order.buyer_gln]
    available_credit = get_available_credit(buyer)

    # The order fits in the credit left ..
    if order.net_total_minor <= available_credit:

        approved = ApprovedOrder()
        approved.order_id = order.order_id
        approved.po_number = order.po_number
        approved.buyer_gln = order.buyer_gln
        approved.currency = order.currency
        approved.order_date = order.order_date
        approved.net_total_minor = order.net_total_minor
        approved.lines = order.lines
        approved.payment_terms_days = buyer.payment_terms_days

        return approved

    # .. or it exceeds it.
    else:

        rejected = RejectedOrder()
        rejected.order_id = order.order_id
        rejected.po_number = order.po_number
        rejected.buyer_gln = order.buyer_gln
        rejected.currency = order.currency
        rejected.net_total_minor = order.net_total_minor
        rejected.available_credit_minor = available_credit
        rejected.reason = f'Order value {order.net_total_minor} exceeds the available credit of {available_credit}'

        return rejected

# ################################################################################################################################

def allocate_line(sku:'str', quantity:'int') -> 'tuple[allocation_list, int]':
    """ Allocates the quantity of a SKU from the warehouses in their order and returns the allocations
    with the quantity that no warehouse has, which is backordered.
    """
    if sku not in Catalog:
        raise UnknownSKUError(f'No warehouse stocks SKU `{sku}`')

    allocations:'allocation_list' = []
    remaining = quantity

    for warehouse, stock in Warehouse_Stock[sku]:

        if remaining == 0:
            break

        # A warehouse without stock of the SKU has nothing to allocate
        if stock == 0:
            continue

        allocated = min(stock, remaining)

        allocation = Allocation()
        allocation.warehouse = warehouse
        allocation.quantity = allocated

        allocations.append(allocation)
        remaining -= allocated

    out = (allocations, remaining)
    return out

# ################################################################################################################################

def choose_carrier(lines:'notice_lines') -> 'str':
    """ Returns the carrier of a shipment by its total weight.
    """
    weight = 0

    for line in lines:
        item = Catalog[line.sku]
        weight += line.shipped_quantity * item.weight_grams

    if weight > _freight_threshold_grams:
        out = Carrier.Freight
    else:
        out = Carrier.Parcel

    return out

# ################################################################################################################################

def build_ship_notice(order:'ApprovedOrder') -> 'ShipNotice':
    """ Allocates each line of an approved order and returns the advance ship notice without a carrier.
    The shipment leaves on the date of the order.
    """
    lines:'notice_lines' = []

    for order_line in order.lines:

        allocations, backordered = allocate_line(order_line.sku, order_line.quantity)

        line = ShipNoticeLine()
        line.line_number = order_line.line_number
        line.sku = order_line.sku
        line.ordered_quantity = order_line.quantity
        line.shipped_quantity = order_line.quantity - backordered
        line.backordered_quantity = backordered
        line.unit_price_minor = order_line.unit_price_minor
        line.allocations = allocations

        lines.append(line)

    out = ShipNotice()
    out.asn_number = get_asn_number(order.po_number)
    out.order_id = order.order_id
    out.po_number = order.po_number
    out.buyer_gln = order.buyer_gln
    out.currency = order.currency
    out.ship_date = order.order_date
    out.payment_terms_days = order.payment_terms_days
    out.carrier = Carrier.Unassigned
    out.lines = lines

    return out

# ################################################################################################################################

def get_tax(net_minor:'int', tax_rate_bp:'int') -> 'int':
    """ Returns the tax on a net amount, rounded half up to a minor unit.
    """
    out = (net_minor * tax_rate_bp + _basis_points // 2) // _basis_points
    return out

# ################################################################################################################################

def get_due_date(invoice_date:'str', payment_terms_days:'int') -> 'str':
    """ Returns the date on which an invoice is due under the payment terms of the buyer.
    """
    issued = date.fromisoformat(invoice_date)
    due = issued + timedelta(days=payment_terms_days)

    out = due.isoformat()
    return out

# ################################################################################################################################

def build_invoice(notice:'ShipNotice') -> 'Invoice':
    """ Returns the invoice of a shipment, dated on its ship date, with one line per shipped line of the notice.
    A line that is backordered in full is not invoiced.
    """
    out = Invoice()
    out.invoice_number = get_invoice_number(notice.po_number)
    out.order_id = notice.order_id
    out.po_number = notice.po_number
    out.buyer_gln = notice.buyer_gln
    out.currency = notice.currency
    out.invoice_date = notice.ship_date
    out.due_date = get_due_date(notice.ship_date, notice.payment_terms_days)
    out.carrier = notice.carrier
    out.net_total_minor = 0
    out.tax_total_minor = 0
    out.lines = []

    for notice_line in notice.lines:

        if notice_line.shipped_quantity == 0:
            continue

        item = Catalog[notice_line.sku]

        line = InvoiceLine()
        line.line_number = notice_line.line_number
        line.sku = notice_line.sku
        line.quantity = notice_line.shipped_quantity
        line.unit_price_minor = notice_line.unit_price_minor
        line.net_minor = line.quantity * line.unit_price_minor
        line.tax_rate_bp = item.tax_rate_bp
        line.tax_minor = get_tax(line.net_minor, line.tax_rate_bp)

        out.lines.append(line)
        out.net_total_minor += line.net_minor
        out.tax_total_minor += line.tax_minor

    out.gross_total_minor = out.net_total_minor + out.tax_total_minor

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_invoice_entry(invoice:'Invoice') -> 'anydict':
    """ The ledger entry that posts an invoice to the account of its buyer.
    """
    out = {
        'kind': LedgerKind.Invoice,
        'key': invoice.invoice_number,
        'po_number': invoice.po_number,
        'buyer_gln': invoice.buyer_gln,
        'currency': invoice.currency,
        'amount_minor': invoice.gross_total_minor,
        'due_date': invoice.due_date,
    }

    return out

# ################################################################################################################################

def new_rejection_entry(order:'RejectedOrder') -> 'anydict':
    """ The ledger entry that records an order which the credit check rejected.
    """
    out = {
        'kind': LedgerKind.Rejection,
        'key': order.po_number,
        'po_number': order.po_number,
        'buyer_gln': order.buyer_gln,
        'currency': order.currency,
        'amount_minor': 0,
        'due_date': '',
    }

    return out

# ################################################################################################################################

def is_in_ledger(entries:'dictlist', entry:'anydict') -> 'bool':
    """ Returns whether the ledger already has an entry of the same kind under the same key.
    """
    for item in entries:
        if item['kind'] == entry['kind'] and item['key'] == entry['key']:
            return True

    return False

# ################################################################################################################################
# ################################################################################################################################
