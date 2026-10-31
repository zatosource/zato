# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from hashlib import sha256

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The approximate size of each kind of document, in bytes.
Receipt_Size        = 1_000
Lab_Result_Size     = 10_000
Purchase_Order_Size = 100_000
X12_Batch_Size      = 1_000_000

# How many documents of each kind one cycle of the mix holds - receipts make up 40 percent of the traffic,
# lab results 30 percent, purchase orders 20 percent and X12 batches 10 percent.
_receipt_count        = 4
_lab_result_count     = 3
_purchase_order_count = 2
_x12_batch_count      = 1

# The laboratory tests each lab result reports - LOINC code, name, unit, reference range and a base value.
_lab_tests = [
    ('2345-7', 'Glucose', 'mg/dL', '70-99', 92),
    ('2160-0', 'Creatinine', 'mg/dL', '0.6-1.2', 1),
    ('3094-0', 'Urea nitrogen', 'mg/dL', '7-20', 14),
    ('2951-2', 'Sodium', 'mmol/L', '136-145', 140),
    ('2823-3', 'Potassium', 'mmol/L', '3.5-5.1', 4),
    ('2075-0', 'Chloride', 'mmol/L', '98-107', 102),
    ('2028-9', 'Carbon dioxide', 'mmol/L', '23-29', 26),
    ('17861-6', 'Calcium', 'mg/dL', '8.6-10.3', 9),
    ('2885-2', 'Protein', 'g/dL', '6.0-8.3', 7),
    ('1751-7', 'Albumin', 'g/dL', '3.5-5.2', 4),
]

# The products the purchase orders and X12 batches order - name, unit price in cents.
_products = [
    ('Industrial bearing 6204-2RS', 412),
    ('Hydraulic hose 1/2 in, 10 m', 3890),
    ('Stainless hex bolt M10x40', 37),
    ('Nitrile gloves, box of 100', 1150),
    ('Safety goggles, anti-fog', 860),
    ('Cable tie 300 mm, pack of 100', 520),
    ('Pallet wrap film 500 mm', 2475),
    ('Thermal label roll 100x150', 1890),
]

# ################################################################################################################################
# ################################################################################################################################

def _new_receipt(index:'int') -> 'str':
    """ A partner's delivery receipt for a group of documents, in JSON.
    """
    documents:'anylist' = []

    receipt:'anydict' = {
        'type': 'delivery_receipt',
        'receipt_id': f'RCPT-2026-{index:08d}',
        'partner_id': f'PARTNER-{index % 50:04d}',
        'received_at': '2026-10-31T10:15:00.000+00:00',
        'status': 'accepted',
        'documents': documents,
    }

    out = json.dumps(receipt)
    document_index = 0

    # Documents are added to the receipt until it reaches its size ..
    while len(out) < Receipt_Size:

        reference = f'DOC-{index:08d}-{document_index:04d}'
        reference_bytes = reference.encode('utf8')
        checksum = sha256(reference_bytes).hexdigest()

        documents.append({
            'reference': reference,
            'status': 'accepted',
            'checksum': f'sha256:{checksum}',
        })

        # .. each time serializing it anew to tell its size.
        out = json.dumps(receipt)
        document_index += 1

    return out

# ################################################################################################################################

def _new_lab_result(index:'int') -> 'str':
    """ An HL7 v2.5.1 ORU^R01 message with the observations of a laboratory order.
    """
    segments:'strlist' = [
        f'MSH|^~\\&|LAB|ACME_HOSPITAL|EHR|ACME_HOSPITAL|20261031101500||ORU^R01|LAB{index:010d}|P|2.5.1',
        f'PID|1||PAT{index:08d}^^^ACME^MR||DOE^JANE^A||19800101|F|||1 MAIN ST^^SPRINGFIELD^IL^62701',
        'PV1|1|O|LAB^^^ACME||||1234^SMITH^JOHN^^^DR',
        f'ORC|RE|ORD{index:08d}|FIL{index:08d}||CM',
        f'OBR|1|ORD{index:08d}|FIL{index:08d}|24323-8^Comprehensive metabolic panel^LN|||20261031090000',
    ]

    total_size = 0

    for segment in segments:
        total_size += len(segment) + 1

    observation_index = 0

    # Observations are added until the message reaches its size ..
    while total_size < Lab_Result_Size:

        test_count = len(_lab_tests)
        test_index = observation_index % test_count
        code, name, unit, reference_range, base_value = _lab_tests[test_index]

        # .. each one a result of one test with a value that varies a little from one observation to the next ..
        value = base_value + observation_index % 3
        set_id = observation_index + 1

        segment = f'OBX|{set_id}|NM|{code}^{name}^LN||{value}|{unit}|{reference_range}|N|||F|||20261031093000'
        segments.append(segment)

        total_size += len(segment) + 1
        observation_index += 1

    # .. and the segments are separated with carriage returns, as HL7 v2 requires.
    out = '\r'.join(segments)
    return out

# ################################################################################################################################

def _new_purchase_order(index:'int') -> 'str':
    """ A purchase order in XML, with as many order lines as its size allows.
    """
    header_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<PurchaseOrder xmlns="urn:acme:purchase-order:1.0" number="PO-2026-{index:08d}" date="2026-10-31">',
        '  <Buyer><PartyId scheme="GLN">5790000000012</PartyId><Name>Acme Retail Ltd</Name></Buyer>',
        '  <Seller><PartyId scheme="GLN">5790000000029</PartyId><Name>Acme Industrial Supply</Name></Seller>',
        '  <Lines>',
        '',
    ]
    header = '\n'.join(header_lines)
    header = header.format(index=index)

    footer = '  </Lines>\n</PurchaseOrder>\n'

    line_elements = [
        '    <Line number="{number}">',
        '<Sku>SKU-{sku:06d}</Sku>',
        '<Description>{description}</Description>',
        '<Quantity unit="EA">{quantity}</Quantity>',
        '<UnitPrice currency="EUR">{price}</UnitPrice>',
        '</Line>\n',
    ]
    line_template = ''.join(line_elements)

    parts:'strlist' = [header]
    total_size = len(header) + len(footer)
    line_index = 0

    # Order lines are added until the order reaches its size.
    while total_size < Purchase_Order_Size:

        product_count = len(_products)
        product_index = line_index % product_count
        description, price_cents = _products[product_index]

        price = price_cents / 100
        price = f'{price:.2f}'

        line = line_template.format(
            number=line_index + 1,
            sku=product_index + 1,
            description=description,
            quantity=line_index % 40 + 1,
            price=price,
        )

        parts.append(line)

        total_size += len(line)
        line_index += 1

    parts.append(footer)

    out = ''.join(parts)
    return out

# ################################################################################################################################

def _new_x12_purchase_order(control_number:'int', order_number:'int', line_count:'int') -> 'strlist':
    """ The segments of one X12 850 purchase order transaction set.
    """
    out:'strlist' = [
        f'ST*850*{control_number:04d}',
        f'BEG*00*SA*PO{order_number:010d}**20261031',
        f'N1*ST*ACME STORE {order_number % 500:04d}*92*{order_number % 500:06d}',
    ]

    for line_index in range(line_count):

        product_count = len(_products)
        product_index = line_index % product_count
        description, price_cents = _products[product_index]

        price = price_cents / 100
        line_number = line_index + 1
        quantity = line_index % 40 + 1

        out.append(f'PO1*{line_number}*{quantity}*EA*{price:.2f}**VP*SKU{product_index + 1:06d}')
        out.append(f'PID*F****{description}')

    out.append(f'CTT*{line_count}')

    # The trailer counts the segments of the transaction set, itself included.
    segment_count = len(out) + 1
    out.append(f'SE*{segment_count}*{control_number:04d}')

    return out

# ################################################################################################################################

def _new_x12_batch(index:'int') -> 'str':
    """ An X12 interchange with a batch of 850 purchase orders, as many as its size allows.
    """

    # The interchange header has fixed-width fields, padded with spaces.
    sender = 'ACMEBUYER'.ljust(15)
    receiver = 'ACMESUPPLIER'.ljust(15)
    empty_field = ' ' * 10

    segments:'strlist' = [
        f'ISA*00*{empty_field}*00*{empty_field}*ZZ*{sender}*ZZ*{receiver}*261031*1015*U*00401*{index:09d}*0*P*>',
        f'GS*PO*ACMEBUYER*ACMESUPPLIER*20261031*1015*{index}*X*004010',
    ]

    total_size = 0

    for segment in segments:
        total_size += len(segment) + 1

    transaction_count = 0

    # Purchase orders are added until the batch reaches its size ..
    while total_size < X12_Batch_Size:

        control_number = transaction_count + 1
        order_number = index * 10_000 + control_number

        transaction = _new_x12_purchase_order(control_number, order_number, 50)
        segments.extend(transaction)

        for segment in transaction:
            total_size += len(segment) + 1

        transaction_count += 1

    # .. and the trailers close the group and the interchange.
    segments.append(f'GE*{transaction_count}*{index}')
    segments.append(f'IEA*1*{index:09d}')

    out = '~'.join(segments)
    out += '~'

    return out

# ################################################################################################################################

def get_document_mix() -> 'strlist':
    """ One cycle of the document mix - delivery receipts, lab results, purchase orders and X12 batches,
    in the proportions of the traffic, interleaved so that every part of the cycle carries documents of each size.
    """
    receipts:'strlist' = []
    lab_results:'strlist' = []
    purchase_orders:'strlist' = []
    x12_batches:'strlist' = []

    for index in range(_receipt_count):
        receipts.append(_new_receipt(index))

    for index in range(_lab_result_count):
        lab_results.append(_new_lab_result(index))

    for index in range(_purchase_order_count):
        purchase_orders.append(_new_purchase_order(index))

    for index in range(_x12_batch_count):
        x12_batches.append(_new_x12_batch(index))

    out:'strlist' = []
    kinds = [receipts, lab_results, purchase_orders, x12_batches]
    document_count = _receipt_count + _lab_result_count + _purchase_order_count + _x12_batch_count

    # Each round takes the next document of every kind that still has one left.
    while len(out) < document_count:
        for kind in kinds:
            if kind:
                document = kind.pop(0)
                out.append(document)

    return out

# ################################################################################################################################
# ################################################################################################################################
