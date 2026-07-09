# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The segment definitions of the version 004010 retail order-to-cash pattern -
# the segments shared by the 850, 855, 856 and 810 transaction sets as the mainstream
# retail implementation guides use them, written from public sources.

from __future__ import annotations

# Zato
from zato.x12.base import EDIElement, Usage, X12Segment

# ################################################################################################################################
# ################################################################################################################################

class BEG(X12Segment):
    """ Beginning segment for purchase order.
    """
    _segment_tag = 'BEG'

    purpose_code   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    po_type        = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 2/2')
    po_number      = EDIElement[str](position=3, usage=Usage.REQUIRED, format='AN 1/22')
    release_number = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='AN 1/30')
    date           = EDIElement[str](position=5, usage=Usage.REQUIRED, format='DT 8/8')

# ################################################################################################################################
# ################################################################################################################################

class CUR(X12Segment):
    """ Currency.
    """
    _segment_tag = 'CUR'

    entity_code   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    currency_code = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 3/3')

# ################################################################################################################################
# ################################################################################################################################

class REF(X12Segment):
    """ Reference identification.
    """
    _segment_tag = 'REF'

    qualifier   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    value       = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='AN 1/30')
    description = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/80')

# ################################################################################################################################
# ################################################################################################################################

class PER(X12Segment):
    """ Administrative communications contact.
    """
    _segment_tag = 'PER'

    contact_function = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    name             = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/60')
    comm_qualifier   = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    comm_number      = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 1/80')

# ################################################################################################################################
# ################################################################################################################################

class FOB(X12Segment):
    """ F.O.B. related instructions.
    """
    _segment_tag = 'FOB'

    payment_method = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    location_qualifier = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='ID 1/2')
    location           = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='AN 1/80')

# ################################################################################################################################
# ################################################################################################################################

class ITD(X12Segment):
    """ Terms of sale.
    """
    _segment_tag = 'ITD'

    terms_type         = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='ID 2/2')
    terms_basis        = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 1/2')
    discount_percent   = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='R 1/6')
    discount_due_date  = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='DT 8/8')
    discount_days      = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='N0 1/3')
    net_due_date       = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='DT 8/8')
    net_days           = EDIElement[str](position=7, usage=Usage.CONDITIONAL, format='N0 1/3')

# ################################################################################################################################
# ################################################################################################################################

class DTM(X12Segment):
    """ Date/time reference.
    """
    _segment_tag = 'DTM'

    qualifier = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 3/3')
    date      = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='DT 8/8')
    time      = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='TM 4/8')

# ################################################################################################################################
# ################################################################################################################################

class N9(X12Segment):
    """ Reference identification - the leader of the note loop.
    """
    _segment_tag = 'N9'

    qualifier   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    value       = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='AN 1/30')
    description = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/45')

# ################################################################################################################################
# ################################################################################################################################

class MSG(X12Segment):
    """ Message text.
    """
    _segment_tag = 'MSG'

    text = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/264')

# ################################################################################################################################
# ################################################################################################################################

class N1(X12Segment):
    """ Name - the leader of the party identification loop.
    """
    _segment_tag = 'N1'

    entity_code  = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    name         = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='AN 1/60')
    id_qualifier = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 1/2')
    id_code      = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 2/80')

# ################################################################################################################################
# ################################################################################################################################

class N2(X12Segment):
    """ Additional name information.
    """
    _segment_tag = 'N2'

    name            = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/60')
    additional_name = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/60')

# ################################################################################################################################
# ################################################################################################################################

class N3(X12Segment):
    """ Address information.
    """
    _segment_tag = 'N3'

    address            = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/55')
    additional_address = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/55')

# ################################################################################################################################
# ################################################################################################################################

class N4(X12Segment):
    """ Geographic location.
    """
    _segment_tag = 'N4'

    city        = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='AN 2/30')
    state       = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 2/2')
    postal_code = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='ID 3/15')
    country     = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='ID 2/3')

# ################################################################################################################################
# ################################################################################################################################

class PO1(X12Segment):
    """ Baseline item data - the leader of the purchase order line loop.
    """
    _segment_tag = 'PO1'

    line_number = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='AN 1/20')
    quantity    = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/15')
    unit        = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='ID 2/2')
    unit_price  = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='R 1/17')
    price_basis = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 2/2')

    # Product id qualifier pairs - UP (GTIN-12), VP (vendor part number), IN (buyer item number)
    id_qualifier_1 = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_id_1   = EDIElement[str](position=7, usage=Usage.CONDITIONAL, format='AN 1/48')
    id_qualifier_2 = EDIElement[str](position=8, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_id_2   = EDIElement[str](position=9, usage=Usage.CONDITIONAL, format='AN 1/48')
    id_qualifier_3 = EDIElement[str](position=10, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_id_3   = EDIElement[str](position=11, usage=Usage.CONDITIONAL, format='AN 1/48')

# ################################################################################################################################
# ################################################################################################################################

class PID(X12Segment):
    """ Product/item description.
    """
    _segment_tag = 'PID'

    description_type    = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    characteristic_code = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 2/3')
    agency_code         = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_code        = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 1/12')
    description         = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='AN 1/80')

# ################################################################################################################################
# ################################################################################################################################

class PKG(X12Segment):
    """ Marking, packaging, loading.
    """
    _segment_tag = 'PKG'

    description_type    = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='ID 1/1')
    characteristic_code = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='ID 2/5')
    agency_code         = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    packaging_code      = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 1/7')
    description         = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='AN 1/80')

# ################################################################################################################################
# ################################################################################################################################

class CTT(X12Segment):
    """ Transaction totals.
    """
    _segment_tag = 'CTT'

    line_count = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N0 1/6')
    hash_total = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='R 1/10')

# ################################################################################################################################
# ################################################################################################################################

class BAK(X12Segment):
    """ Beginning segment for purchase order acknowledgment.
    """
    _segment_tag = 'BAK'

    purpose_code = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    ack_type     = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 2/2')
    po_number    = EDIElement[str](position=3, usage=Usage.REQUIRED, format='AN 1/22')
    date         = EDIElement[str](position=4, usage=Usage.REQUIRED, format='DT 8/8')

# ################################################################################################################################
# ################################################################################################################################

class ACK(X12Segment):
    """ Line item acknowledgment.
    """
    _segment_tag = 'ACK'

    line_status = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    quantity    = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/15')
    unit        = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')

# ################################################################################################################################
# ################################################################################################################################

class BSN(X12Segment):
    """ Beginning segment for ship notice.
    """
    _segment_tag = 'BSN'

    purpose_code   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    shipment_id    = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 2/30')
    date           = EDIElement[str](position=3, usage=Usage.REQUIRED, format='DT 8/8')
    time           = EDIElement[str](position=4, usage=Usage.REQUIRED, format='TM 4/8')
    structure_code = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 4/4')

# ################################################################################################################################
# ################################################################################################################################

class HL(X12Segment):
    """ Hierarchical level - the segment whose parent pointers build the 856 tree.
    """
    _segment_tag = 'HL'

    hl_id      = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/12')
    parent_id  = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/12')
    level_code = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 1/2')
    child_code = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='N0 1/1')

# ################################################################################################################################
# ################################################################################################################################

class TD1(X12Segment):
    """ Carrier details - quantity and weight.
    """
    _segment_tag = 'TD1'

    packaging_code   = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='AN 3/5')
    lading_quantity  = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='N0 1/7')
    weight_qualifier = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='ID 1/2')
    weight           = EDIElement[str](position=7, usage=Usage.CONDITIONAL, format='R 1/10')
    weight_unit      = EDIElement[str](position=8, usage=Usage.CONDITIONAL, format='ID 2/2')

# ################################################################################################################################
# ################################################################################################################################

class TD5(X12Segment):
    """ Carrier details - routing sequence and transit time.
    """
    _segment_tag = 'TD5'

    routing_sequence = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='ID 1/2')
    id_qualifier     = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='ID 1/2')
    id_code          = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 2/80')
    transport_method = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='ID 1/2')
    routing          = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='AN 1/35')

# ################################################################################################################################
# ################################################################################################################################

class TD3(X12Segment):
    """ Carrier details - equipment.
    """
    _segment_tag = 'TD3'

    equipment_code    = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='ID 2/2')
    equipment_initial = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/4')
    equipment_number  = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/10')

# ################################################################################################################################
# ################################################################################################################################

class PRF(X12Segment):
    """ Purchase order reference.
    """
    _segment_tag = 'PRF'

    po_number = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/22')
    date      = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='DT 8/8')

# ################################################################################################################################
# ################################################################################################################################

class MAN(X12Segment):
    """ Marks and numbers - carries the SSCC-18 of a pack in an 856.
    """
    _segment_tag = 'MAN'

    qualifier = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/2')
    number    = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 1/48')

# ################################################################################################################################
# ################################################################################################################################

class LIN(X12Segment):
    """ Item identification.
    """
    _segment_tag = 'LIN'

    line_id        = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='AN 1/20')
    id_qualifier_1 = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 2/2')
    product_id_1   = EDIElement[str](position=3, usage=Usage.REQUIRED, format='AN 1/48')
    id_qualifier_2 = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_id_2   = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='AN 1/48')

# ################################################################################################################################
# ################################################################################################################################

class SN1(X12Segment):
    """ Item detail - shipment.
    """
    _segment_tag = 'SN1'

    line_id  = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='AN 1/20')
    quantity = EDIElement[str](position=2, usage=Usage.REQUIRED, format='R 1/10')
    unit     = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 2/2')

# ################################################################################################################################
# ################################################################################################################################

class PO4(X12Segment):
    """ Item physical details.
    """
    _segment_tag = 'PO4'

    pack = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='N0 1/6')
    size = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/9')
    unit = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')

# ################################################################################################################################
# ################################################################################################################################

class BIG(X12Segment):
    """ Beginning segment for invoice.
    """
    _segment_tag = 'BIG'

    invoice_date   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='DT 8/8')
    invoice_number = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 1/22')
    po_date        = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='DT 8/8')
    po_number      = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='AN 1/22')

# ################################################################################################################################
# ################################################################################################################################

class IT1(X12Segment):
    """ Baseline item data - the leader of the invoice line loop.
    """
    _segment_tag = 'IT1'

    line_number = EDIElement[str](position=1, usage=Usage.OPTIONAL, format='AN 1/20')
    quantity    = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/15')
    unit        = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    unit_price  = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='R 1/17')
    price_basis = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 2/2')

    # Product id qualifier pairs, the same shape the PO1 uses
    id_qualifier_1 = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_id_1   = EDIElement[str](position=7, usage=Usage.CONDITIONAL, format='AN 1/48')
    id_qualifier_2 = EDIElement[str](position=8, usage=Usage.CONDITIONAL, format='ID 2/2')
    product_id_2   = EDIElement[str](position=9, usage=Usage.CONDITIONAL, format='AN 1/48')

# ################################################################################################################################
# ################################################################################################################################

class TDS(X12Segment):
    """ Total monetary value summary - the amount is in N2 format, i.e. with two implied decimals.
    """
    _segment_tag = 'TDS'

    total_amount = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N2 1/15')

# ################################################################################################################################
# ################################################################################################################################

class TXI(X12Segment):
    """ Tax information.
    """
    _segment_tag = 'TXI'

    tax_type = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    amount   = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/18')

# ################################################################################################################################
# ################################################################################################################################

class SAC(X12Segment):
    """ Service, promotion, allowance or charge information.
    """
    _segment_tag = 'SAC'

    indicator = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    code      = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='ID 4/4')
    amount    = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='N2 1/15')

# ################################################################################################################################
# ################################################################################################################################

class ISS(X12Segment):
    """ Invoice shipment summary.
    """
    _segment_tag = 'ISS'

    quantity = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='R 1/10')
    unit     = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='ID 2/2')

# ################################################################################################################################
# ################################################################################################################################
