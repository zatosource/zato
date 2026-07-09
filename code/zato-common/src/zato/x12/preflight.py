# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Retailer pre-flight checks - the layer that prevents the failures suppliers get fined for.
# Every failed submission resets the retailer's testing queue, so these checks run before
# the first wire send: the 856 HL tree shape, SSCC-18 and GTIN check digits, unit-of-measure
# echo-back against the purchase order, invoice balancing, duplicate invoice numbers
# and the ISA15 test-vs-production guard.

from __future__ import annotations

# Zato
from zato.x12.base import X12Message, _element_value
from zato.x12.syntax import RawSegment
from zato.x12.validation import validate_snip_3

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401
    from zato.x12.control import ControlNumberStore
    from zato.x12.envelope import X12Interchange
    ControlNumberStore = ControlNumberStore
    X12Interchange = X12Interchange

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
any_             = 'Any'
strlist          = list[str]
raw_segment_list = list[RawSegment]
store_none       = 'ControlNumberStore | None'
message_none     = 'X12Message | None'

# ################################################################################################################################
# ################################################################################################################################

# The value kinds recorded for per-partner uniqueness.
Kind_SSCC           = 'sscc'
Kind_Invoice_Number = 'invoice-number'

# An SSCC-18 is always exactly eighteen digits, GS1 check digit included.
SSCC_Length = 18

# The GTIN lengths in circulation - GTIN-8, UPC-A/GTIN-12, EAN/GTIN-13 and GTIN-14.
GTIN_Lengths = (8, 12, 13, 14)

# The MAN qualifier marking an SSCC-18 and the product id qualifier marking a GTIN/UPC.
SSCC_Qualifier = 'GM'
GTIN_Qualifier = 'UP'

# The HL level codes of an 856 - shipment, order, pack (tare) and item.
Level_Shipment = 'S'
Level_Order    = 'O'
Level_Pack     = 'P'
Level_Item     = 'I'

# Which child levels each HL level may carry - standard pack is S-O-P-I,
# pick-and-pack is S-O-I and packs may nest inside packs.
allowed_hl_children = {
    Level_Shipment: (Level_Order,),
    Level_Order:    (Level_Pack, Level_Item),
    Level_Pack:     (Level_Pack, Level_Item),
}

# The product id qualifier element pairs of a PO1 or IT1 - (qualifier position, id position).
product_id_positions = ((6, 7), (8, 9), (10, 11))

# ################################################################################################################################
# ################################################################################################################################

def gs1_check_digit(digits:'str') -> 'int':
    """ Computes the GS1 Mod-10 check digit of the given digits - the rightmost digit
    is weighted 3, then the weights alternate 1 and 3 moving left.
    """
    total = 0

    for index, character in enumerate(reversed(digits)):
        digit = int(character)

        if index % 2 == 0:
            total += digit * 3
        else:
            total += digit

    out = (10 - total % 10) % 10
    return out

# ################################################################################################################################

def is_valid_sscc(value:'str') -> 'bool':
    """ Whether the value is a well-formed SSCC-18 - eighteen digits whose last one
    is the correct GS1 check digit.
    """
    if not value.isdigit():
        return False

    if len(value) != SSCC_Length:
        return False

    expected = gs1_check_digit(value[:-1])

    out = int(value[-1]) == expected
    return out

# ################################################################################################################################

def is_valid_gtin(value:'str') -> 'bool':
    """ Whether the value is a well-formed GTIN - one of the GS1 lengths
    with a correct Mod-10 check digit, covering UPC-A and EAN codes.
    """
    if not value.isdigit():
        return False

    if len(value) not in GTIN_Lengths:
        return False

    expected = gs1_check_digit(value[:-1])

    out = int(value[-1]) == expected
    return out

# ################################################################################################################################
# ################################################################################################################################

def _check_hl_tree(out:'strlist', raw_segments:'raw_segment_list') -> 'None':
    """ Validates the HL01/HL02 parentage of an 856 - the ids must be unique, the parents
    must exist, there must be exactly one shipment-level root and every parent-child level
    pair must be one the guides allow, whether standard-pack or pick-and-pack.
    """
    hl_ids:'strlist' = []
    parent_by_id:'dict[str, str]' = {}
    level_by_id:'dict[str, str]' = {}

    for raw_segment in raw_segments:
        if raw_segment.tag != 'HL':
            continue

        hl_id = _element_value(raw_segment, 1)
        parent_id = _element_value(raw_segment, 2)
        level_code = _element_value(raw_segment, 3)

        if hl_id in hl_ids:
            out.append(f'Duplicate HL01 id `{hl_id}`')
            continue

        hl_ids.append(hl_id)
        parent_by_id[hl_id] = parent_id
        level_by_id[hl_id] = level_code

    if not hl_ids:
        out.append('No HL segments found')
        return

    # There must be exactly one root and it must be the shipment level ..
    root_ids:'strlist' = []

    for hl_id in hl_ids:
        if not parent_by_id[hl_id]:
            root_ids.append(hl_id)

    root_count = len(root_ids)

    if root_count != 1:
        out.append(f'Expected exactly 1 top-level HL, found {root_count}')

    for root_id in root_ids:
        root_level = level_by_id[root_id]
        if root_level != Level_Shipment:
            out.append(f'Top-level HL `{root_id}` has level `{root_level}` instead of `{Level_Shipment}`')

    # .. every parent pointer must resolve ..
    for hl_id in hl_ids:
        parent_id = parent_by_id[hl_id]
        if parent_id:
            if parent_id not in level_by_id:
                out.append(f'HL `{hl_id}` points at parent `{parent_id}` which does not exist')

    # .. and every parent-child level pair must be an allowed shape.
    for hl_id in hl_ids:
        parent_id = parent_by_id[hl_id]

        if parent_id in level_by_id:
            parent_level = level_by_id[parent_id]
            child_level = level_by_id[hl_id]

            allowed = allowed_hl_children.get(parent_level, ())

            if child_level not in allowed:
                out.append(f'HL `{hl_id}` level `{child_level}` cannot be a child of level `{parent_level}`')

# ################################################################################################################################

def _check_line_gtins(out:'strlist', raw_segments:'raw_segment_list', tag:'str') -> 'None':
    """ Validates the Mod-10 check digit of every UP-qualified product id
    on the line segments with the given tag (PO1 or IT1).
    """
    for raw_segment in raw_segments:
        if raw_segment.tag != tag:
            continue

        for qualifier_position, id_position in product_id_positions:
            qualifier = _element_value(raw_segment, qualifier_position)

            if qualifier == GTIN_Qualifier:
                product_id = _element_value(raw_segment, id_position)

                if not is_valid_gtin(product_id):
                    out.append(f'{tag} product id `{product_id}` is not a valid GTIN/UPC')

# ################################################################################################################################
# ################################################################################################################################

def preflight_ship_notice(
    message:'X12Message',
    store:'store_none' = None,
    sender:'str' = '',
    receiver:'str' = '',
    ) -> 'strlist':
    """ Pre-flight checks of an 856 ship notice - the HL tree must be coherent,
    every SSCC-18 on a MAN segment must have a correct check digit and be unique,
    both within the notice and, given a store, across everything ever sent
    to the partner, and every UP-qualified LIN id must be a valid GTIN.
    """

    # Our response to produce
    out:'strlist' = []

    raw_segments = message._raw_segments

    # The tree shape is the highest failure rate in retailer testing
    _check_hl_tree(out, raw_segments)

    # SSCC-18 check digits and uniqueness on the MAN segments
    seen_sscc:'strlist' = []

    for raw_segment in raw_segments:
        if raw_segment.tag != 'MAN':
            continue

        qualifier = _element_value(raw_segment, 1)
        if qualifier != SSCC_Qualifier:
            continue

        sscc = _element_value(raw_segment, 2)

        if not is_valid_sscc(sscc):
            out.append(f'MAN SSCC `{sscc}` is not a valid SSCC-18')
            continue

        if sscc in seen_sscc:
            out.append(f'Duplicate SSCC `{sscc}` within the ship notice')
            continue

        seen_sscc.append(sscc)

        # Per-partner uniqueness across everything ever sent
        if store is not None:
            is_duplicate = store.observe_value(sender, receiver, Kind_SSCC, sscc)
            if is_duplicate:
                out.append(f'SSCC `{sscc}` was already used with this partner')

    # GTIN check digits on the LIN item identifications
    for raw_segment in raw_segments:
        if raw_segment.tag == 'LIN':
            for position in (2, 4):
                qualifier = _element_value(raw_segment, position)
                if qualifier == GTIN_Qualifier:
                    product_id = _element_value(raw_segment, position + 1)
                    if not is_valid_gtin(product_id):
                        out.append(f'LIN product id `{product_id}` is not a valid GTIN/UPC')

    return out

# ################################################################################################################################

def _uom_by_product_id(raw_segments:'raw_segment_list', tag:'str') -> 'dict[str, str]':
    """ Maps each UP-qualified product id of the given line tag to its unit of measure.
    """

    # Our response to produce
    out:'dict[str, str]' = {}

    for raw_segment in raw_segments:
        if raw_segment.tag != tag:
            continue

        unit = _element_value(raw_segment, 3)

        for qualifier_position, id_position in product_id_positions:
            qualifier = _element_value(raw_segment, qualifier_position)

            if qualifier == GTIN_Qualifier:
                product_id = _element_value(raw_segment, id_position)
                out[product_id] = unit

    return out

# ################################################################################################################################

def preflight_invoice(
    message:'X12Message',
    order:'message_none' = None,
    store:'store_none' = None,
    sender:'str' = '',
    receiver:'str' = '',
    ) -> 'strlist':
    """ Pre-flight checks of an 810 invoice - GTIN check digits on the lines, TDS01
    balancing against the line amounts, the unit of measure echoed back against
    the purchase order and, given a store, duplicate invoice number detection on BIG02.
    """

    # Our response to produce
    out:'strlist' = []

    raw_segments = message._raw_segments

    # GTIN check digits on the IT1 lines
    _check_line_gtins(out, raw_segments, 'IT1')

    # TDS01 and CTT balancing is the SNIP type 3 arithmetic
    balance_issues = validate_snip_3(message)
    out.extend(balance_issues)

    # The unit of measure must echo what the purchase order used
    if order is not None:
        order_units = _uom_by_product_id(order._raw_segments, 'PO1')
        invoice_units = _uom_by_product_id(raw_segments, 'IT1')

        for product_id, invoice_unit in invoice_units.items():
            if product_id in order_units:
                order_unit = order_units[product_id]
                if invoice_unit != order_unit:
                    out.append(
                        f'Line `{product_id}` uses unit `{invoice_unit}` but the purchase order used `{order_unit}`')

    # An invoice number must never repeat with the same partner
    if store is not None:
        for raw_segment in raw_segments:
            if raw_segment.tag == 'BIG':
                invoice_number = _element_value(raw_segment, 2)
                is_duplicate = store.observe_value(sender, receiver, Kind_Invoice_Number, invoice_number)
                if is_duplicate:
                    out.append(f'Invoice number `{invoice_number}` was already used with this partner')

    return out

# ################################################################################################################################

def preflight_purchase_order(message:'X12Message') -> 'strlist':
    """ Pre-flight checks of an 850 purchase order - GTIN check digits on the lines
    and the CTT totals balancing against the actual line data.
    """

    # Our response to produce
    out:'strlist' = []

    raw_segments = message._raw_segments

    _check_line_gtins(out, raw_segments, 'PO1')

    balance_issues = validate_snip_3(message)
    out.extend(balance_issues)

    return out

# ################################################################################################################################

def check_usage_indicator(interchange:'X12Interchange', expected:'str') -> 'strlist':
    """ The ISA15 test-vs-production guard - a test interchange must never post
    to a production endpoint and the other way around.
    """

    # Our response to produce
    out:'strlist' = []

    usage_indicator = interchange.isa.usage_indicator

    if usage_indicator != expected:
        out.append(f'ISA15 is `{usage_indicator}` but this endpoint expects `{expected}`')

    return out

# ################################################################################################################################
# ################################################################################################################################
