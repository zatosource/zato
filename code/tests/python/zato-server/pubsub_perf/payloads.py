# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The business documents that the publishers of the perf suite publish - purchase orders, invoices and shipment notices.
# The size of the JSON of each message is drawn from a triangular distribution, and the documents are built from
# a fixed seed before a run starts, so every run publishes the same documents and their building takes no time of the run.

# stdlib
import json
from datetime import timedelta

# Faker
from faker import Faker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The size of the JSON of each published message, in bytes - the smallest, the largest and the most frequent one
_min_size  = 500
_max_size  = 10_240
_mode_size = 5_120

# How many distinct documents a run publishes, which each publisher takes in turn from an offset of its own
Pool_Size = 256

# The seed of the documents, the same in every run
_seed = 20261119

# The locale of the names, companies and addresses of the documents
_locale = 'en_US'

# The kinds of documents, which the documents of the pool take in turn
_purchase_order  = 'purchase_order'
_invoice         = 'invoice'
_shipment_notice = 'shipment_notice'

_kinds = (_purchase_order, _invoice, _shipment_notice)

_currency = 'USD'
_country  = 'US'

# The quantity and the unit price in cents of a line, and the weight of a package in grams
_min_quantity         = 1
_max_quantity         = 250
_min_unit_price_cents = 150
_max_unit_price_cents = 250_000
_min_weight_grams     = 200
_max_weight_grams     = 40_000

_cents_per_dollar = 100
_grams_per_kilogram = 1000

# How long after its issue an invoice is due
_payment_terms = timedelta(days=30)

# The bytes that the separator between two items of a JSON list takes, as json.dumps writes it
_list_separator_size = 2

# The bytes kept free for the total of a document, which is computed once its lines are known
_total_reserve = 16

# The upper case letters of the SKUs
_sku_letters = 'ABCDEFGHJKLMNPRSTUVWXYZ'

# ################################################################################################################################
# ################################################################################################################################

def _encoded_size(value:'object') -> 'int':
    """ Returns the size of a value as JSON, as the publishers send it.
    """
    out = len(json.dumps(value))
    return out

# ################################################################################################################################

def _new_party(fake:'Faker') -> 'anydict':
    out:'anydict' = {
        'name': fake.name(),
        'company': fake.company(),
        'email': fake.company_email(),
        'phone': fake.phone_number(),
    }
    return out

# ################################################################################################################################

def _new_address(fake:'Faker') -> 'anydict':
    out:'anydict' = {
        'street': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'postal_code': fake.postcode(),
        'country': _country,
    }
    return out

# ################################################################################################################################

def _new_sku(fake:'Faker') -> 'str':
    out = fake.bothify('SKU-####-??', letters=_sku_letters)
    return out

# ################################################################################################################################

def _new_priced_line(fake:'Faker', line_number:'int') -> 'anydict':
    """ Returns one line of a purchase order or an invoice.
    """
    quantity = fake.random_int(_min_quantity, _max_quantity)
    unit_price_cents = fake.random_int(_min_unit_price_cents, _max_unit_price_cents)
    amount_cents = quantity * unit_price_cents

    out:'anydict' = {
        'line_number': line_number,
        'sku': _new_sku(fake),
        'description': fake.catch_phrase(),
        'quantity': quantity,
        'unit_price': unit_price_cents / _cents_per_dollar,
        'amount': amount_cents / _cents_per_dollar,
    }
    return out

# ################################################################################################################################

def _new_shipped_line(fake:'Faker', line_number:'int') -> 'anydict':
    """ Returns one line of a shipment notice.
    """
    weight_grams = fake.random_int(_min_weight_grams, _max_weight_grams)

    out:'anydict' = {
        'line_number': line_number,
        'sku': _new_sku(fake),
        'description': fake.catch_phrase(),
        'quantity': fake.random_int(_min_quantity, _max_quantity),
        'package_id': fake.bothify('PKG-########'),
        'weight_kg': weight_grams / _grams_per_kilogram,
    }
    return out

# ################################################################################################################################

def _new_header(fake:'Faker', kind:'str') -> 'anydict':
    """ Returns a document of the given kind without its lines, with an empty total and empty notes.
    """
    issued_at = fake.date_time_this_year()
    order_id = fake.bothify('PO-########')

    if kind == _purchase_order:
        out:'anydict' = {
            'type': kind,
            'order_id': order_id,
            'issued_at': issued_at.isoformat(),
            'currency': _currency,
            'buyer': _new_party(fake),
            'ship_to': _new_address(fake),
            'lines': [],
            'total': 0,
            'notes': '',
        }

    elif kind == _invoice:
        due_date = issued_at.date() + _payment_terms
        out = {
            'type': kind,
            'invoice_id': fake.bothify('INV-########'),
            'order_id': order_id,
            'issued_at': issued_at.isoformat(),
            'due_date': due_date.isoformat(),
            'currency': _currency,
            'bill_to': _new_party(fake),
            'lines': [],
            'total': 0,
            'notes': '',
        }

    else:
        out = {
            'type': kind,
            'shipment_id': fake.bothify('SHP-########'),
            'order_id': order_id,
            'shipped_at': issued_at.isoformat(),
            'carrier': fake.company(),
            'tracking_number': fake.bothify('TRK-############'),
            'ship_to': _new_address(fake),
            'lines': [],
            'notes': '',
        }

    return out

# ################################################################################################################################

def _new_document(fake:'Faker', kind:'str', target_size:'int', envelope_size:'int') -> 'anydict':
    """ Returns a document of the given kind whose message has about the given size, with at least one line.
    """
    out = _new_header(fake, kind)
    lines = out['lines']

    # The lines fill the document up to its size, apart from the room of its total ..
    size = envelope_size + _encoded_size(out)
    line_limit = target_size - _total_reserve

    while True:
        line_number = len(lines) + 1

        if kind == _shipment_notice:
            line = _new_shipped_line(fake, line_number)
        else:
            line = _new_priced_line(fake, line_number)

        line_size = _encoded_size(line)

        if lines:
            line_size += _list_separator_size

            if size + line_size > line_limit:
                break

        lines.append(line)
        size += line_size

    # .. the total is that of the lines ..
    if kind != _shipment_notice:
        total_cents = 0
        for line in lines:
            total_cents += round(line['amount'] * _cents_per_dollar)
        out['total'] = total_cents / _cents_per_dollar

    # .. and the notes take the rest, sentence by sentence.
    remaining = target_size - envelope_size - _encoded_size(out)
    notes = ''

    while True:
        sentence = fake.sentence()

        if notes:
            sentence = ' ' + sentence

        if len(notes) + len(sentence) > remaining:
            break

        notes += sentence

    out['notes'] = notes
    return out

# ################################################################################################################################

def build_documents(key_length:'int') -> 'dictlist':
    """ Returns the documents of a run, each to be published as the document of a message with a key of the given length.
    """
    fake = Faker(_locale)
    fake.seed_instance(_seed)

    # The message is the document with its key, as the publishers send it.
    envelope = {'key': 'k' * key_length, 'document': None}
    envelope_size = _encoded_size(envelope) - _encoded_size(None)

    out:'dictlist' = []

    for index in range(Pool_Size):
        kind = _kinds[index % len(_kinds)]

        target_size = fake.random.triangular(_min_size, _max_size, _mode_size)
        target_size = round(target_size)

        document = _new_document(fake, kind, target_size, envelope_size)
        out.append(document)

    return out

# ################################################################################################################################
# ################################################################################################################################
