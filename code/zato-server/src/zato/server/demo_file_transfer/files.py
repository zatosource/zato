# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The sample files the file transfer demo drops into the directories its schedules poll -
# invoices, orders with their markers, shipments and reports, plus now and then a malformed invoice.

# stdlib
from datetime import datetime, timezone
from json import dumps
from typing import NamedTuple

# Zato
from zato.common.api import FileTransfer
from zato.common.crypto.api import CryptoManager
from zato.server.demo_file_transfer.layout import Shape_Invoices, Shape_Orders, Shape_Reports, Shape_Shipments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strcalldict, strlist

# ################################################################################################################################
# ################################################################################################################################

demo_file_list = list['DemoFile']

# ################################################################################################################################
# ################################################################################################################################

# The first line of every well-formed invoice - the invoices service rejects a file that starts with anything else
Invoice_Header = 'invoice_id,customer,amount,currency'

# What a malformed invoice starts with instead
Malformed_Header = 'malformed'

# How many files of each shape one batch has
_files_per_batch = {
    Shape_Invoices:  2,
    Shape_Orders:    2,
    Shape_Shipments: 2,
    Shape_Reports:   1,
}

# The customers the sample files are for, taking turns
_customers = ['John Smith', 'Maria Johnson', 'Anna Miller', 'Jane Doe']

# The products the sample orders are for, taking turns
_skus = ['SKU-1001', 'SKU-1002', 'SKU-2001', 'SKU-3005']

# How file names say when a file was made
_timestamp_format = '%Y%m%d-%H%M%S'

# How many random bits make two files of the same second differ
_suffix_bits = 32

# What an order's marker file is called after the order itself
_marker_suffix = FileTransfer.Scheduler.Default_Marker_Suffix

# ################################################################################################################################
# ################################################################################################################################

class DemoFile(NamedTuple):
    """ One sample file - its name and its bytes.
    """
    name: 'str'
    data: 'bytes'

# ################################################################################################################################
# ################################################################################################################################

def _new_id() -> 'str':
    """ A unique part of a file's name and of the document inside, e.g. 20261014-150203-9f3a61c2.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime(_timestamp_format)

    suffix = CryptoManager.generate_hex_string(_suffix_bits)

    out = f'{timestamp}-{suffix}'
    return out

# ################################################################################################################################

def _pick(items:'strlist', unique_id:'str') -> 'str':
    """ One of the items, chosen by the random suffix of a unique id.
    """
    suffix = unique_id.rsplit('-', 1)[1]
    position = int(suffix, 16) % len(items)

    out = items[position]
    return out

# ################################################################################################################################

def _build_invoice(is_malformed:'bool') -> 'DemoFile':

    unique_id = _new_id()
    customer = _pick(_customers, unique_id)

    suffix = unique_id.rsplit('-', 1)[1]
    cents = int(suffix, 16) % 100_000
    amount = cents / 100

    if is_malformed:
        name = f'invoice-{unique_id}-malformed.csv'
        lines = [Malformed_Header, f'INV-{unique_id};{customer}']
    else:
        name = f'invoice-{unique_id}.csv'
        lines = [Invoice_Header, f'INV-{unique_id},{customer},{amount:.2f},USD']

    text = '\n'.join(lines) + '\n'
    data = text.encode('utf8')

    out = DemoFile(name, data)
    return out

# ################################################################################################################################

def _build_invoices() -> 'demo_file_list':

    invoice = _build_invoice(False)

    out = [invoice]
    return out

# ################################################################################################################################

def _build_orders() -> 'demo_file_list':
    """ An order and the marker that says it is complete, in the order they are to be written.
    """
    unique_id = _new_id()
    name = f'order-{unique_id}.json'

    order = {
        'order_id': f'ORD-{unique_id}',
        'customer': _pick(_customers, unique_id),
        'lines': [
            {'sku': _pick(_skus, unique_id), 'quantity': 3},
        ],
    }

    text = dumps(order, indent=2)
    data = text.encode('utf8')

    marker_name = name + _marker_suffix
    marker_data = name.encode('utf8')

    order_file = DemoFile(name, data)
    marker_file = DemoFile(marker_name, marker_data)

    out = [order_file, marker_file]
    return out

# ################################################################################################################################

def _build_shipments() -> 'demo_file_list':

    unique_id = _new_id()
    recipient = _pick(_customers, unique_id)

    name = f'shipment-{unique_id}.xml'
    text = f'<shipment id="SHP-{unique_id}"><recipient>{recipient}</recipient><status>dispatched</status></shipment>\n'
    data = text.encode('utf8')

    shipment = DemoFile(name, data)

    out = [shipment]
    return out

# ################################################################################################################################

def _build_reports() -> 'demo_file_list':

    unique_id = _new_id()

    name = f'report-{unique_id}.txt'
    text = f'Daily report {unique_id}\nOrders received: 12\nShipments dispatched: 9\n'
    data = text.encode('utf8')

    report = DemoFile(name, data)

    out = [report]
    return out

# ################################################################################################################################
# ################################################################################################################################

# What builds the files of each shape
_builders:'strcalldict' = {
    Shape_Invoices:  _build_invoices,
    Shape_Orders:    _build_orders,
    Shape_Shipments: _build_shipments,
    Shape_Reports:   _build_reports,
}

# ################################################################################################################################
# ################################################################################################################################

def build_files(shape:'str', with_malformed:'bool') -> 'demo_file_list':
    """ One batch of sample files for a schedule of the given shape, in the order they are to be written.
    With with_malformed, an invoices batch has one malformed invoice on top of the regular ones.
    """
    out:'demo_file_list' = []

    builder = _builders[shape]
    count = _files_per_batch[shape]

    for _ in range(count):
        files = builder()
        out.extend(files)

    if with_malformed:
        if shape == Shape_Invoices:
            malformed = _build_invoice(True)
            out.append(malformed)

    return out

# ################################################################################################################################
# ################################################################################################################################
