# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The transaction set definitions of the version 004010 retail order-to-cash pattern -
# 850 purchase order, 855 acknowledgment, 856 ship notice and 810 invoice.

from __future__ import annotations

# Zato
from zato.x12.base import EDIGroup, EDIGroupAttr, EDIRepeatableList, EDISegmentAttr, X12Message
from zato.x12.retail.segments import ACK, BAK, BEG, BIG, BSN, CTT, CUR, DTM, FOB, HL, ISS, IT1, ITD, LIN, MAN, MSG, N1, N2, \
     N3, N4, N9, PER, PID, PKG, PO1, PO4, PRF, REF, SAC, SN1, TD1, TD3, TD5, TDS, TXI
from zato.x12.service import SE, ST

# ################################################################################################################################
# ################################################################################################################################

class Note(EDIGroup):
    """ One N9 note loop - a reference with its free-form message text.
    """
    _leader_tag = 'N9'

    n9       = EDISegmentAttr[N9](N9)
    messages = EDISegmentAttr[EDIRepeatableList](MSG, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class Party(EDIGroup):
    """ One N1 party identification loop - the name with the BY/ST/BT qualifiers
    and its address and location segments.
    """
    _leader_tag = 'N1'

    n1              = EDISegmentAttr[N1](N1)
    additional_name = EDISegmentAttr[N2](N2, optional=True)
    address         = EDISegmentAttr[EDIRepeatableList](N3, optional=True, repeatable=True)
    location        = EDISegmentAttr[N4](N4, optional=True)

# ################################################################################################################################
# ################################################################################################################################

class PurchaseOrderLine(EDIGroup):
    """ One PO1 line loop of an 850 - the baseline item data with its nested
    descriptions, references, dates and packaging.
    """
    _leader_tag = 'PO1'

    po1          = EDISegmentAttr[PO1](PO1)
    descriptions = EDISegmentAttr[EDIRepeatableList](PID, optional=True, repeatable=True)
    references   = EDISegmentAttr[EDIRepeatableList](REF, optional=True, repeatable=True)
    dates        = EDISegmentAttr[EDIRepeatableList](DTM, optional=True, repeatable=True)
    packaging    = EDISegmentAttr[EDIRepeatableList](PKG, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class PurchaseOrder850(X12Message):
    """ 850 purchase order, version 004010 - the retail order the buyer sends the supplier.
    """
    _message_type = '850'
    _message_version = '004010'

    st         = EDISegmentAttr[ST](ST)
    beg        = EDISegmentAttr[BEG](BEG)
    currency   = EDISegmentAttr[CUR](CUR, optional=True)
    references = EDISegmentAttr[EDIRepeatableList](REF, optional=True, repeatable=True)
    contacts   = EDISegmentAttr[EDIRepeatableList](PER, optional=True, repeatable=True)
    fob        = EDISegmentAttr[FOB](FOB, optional=True)
    terms      = EDISegmentAttr[ITD](ITD, optional=True)
    dates      = EDISegmentAttr[EDIRepeatableList](DTM, optional=True, repeatable=True)
    notes      = EDIGroupAttr[EDIRepeatableList](Note, optional=True)
    parties    = EDIGroupAttr[EDIRepeatableList](Party, optional=True)
    lines      = EDIGroupAttr[EDIRepeatableList](PurchaseOrderLine)
    ctt        = EDISegmentAttr[CTT](CTT, optional=True)
    se         = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class AcknowledgedLine(EDIGroup):
    """ One PO1 line loop of an 855 - the baseline item data with its ACK line-status segments.
    """
    _leader_tag = 'PO1'

    po1             = EDISegmentAttr[PO1](PO1)
    acknowledgments = EDISegmentAttr[EDIRepeatableList](ACK, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class PurchaseOrderAcknowledgment855(X12Message):
    """ 855 purchase order acknowledgment, version 004010 - the supplier's line-by-line
    answer to an 850.
    """
    _message_type = '855'
    _message_version = '004010'

    st         = EDISegmentAttr[ST](ST)
    bak        = EDISegmentAttr[BAK](BAK)
    references = EDISegmentAttr[EDIRepeatableList](REF, optional=True, repeatable=True)
    dates      = EDISegmentAttr[EDIRepeatableList](DTM, optional=True, repeatable=True)
    parties    = EDIGroupAttr[EDIRepeatableList](Party, optional=True)
    lines      = EDIGroupAttr[EDIRepeatableList](AcknowledgedLine)
    ctt        = EDISegmentAttr[CTT](CTT, optional=True)
    se         = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class ShipNotice856(X12Message):
    """ 856 ship notice, version 004010 - the advance ship notice whose HL hierarchy
    (shipment, order, pack, item) is reachable through the hierarchy property.
    The HL-carried body segments are declared so strict validation knows them -
    navigation happens through the hierarchy, not through these attributes.
    """
    _message_type = '856'
    _message_version = '004010'

    st         = EDISegmentAttr[ST](ST)
    bsn        = EDISegmentAttr[BSN](BSN)
    dates      = EDISegmentAttr[EDIRepeatableList](DTM, optional=True, repeatable=True)
    levels     = EDISegmentAttr[EDIRepeatableList](HL, optional=True, repeatable=True)
    quantities = EDISegmentAttr[EDIRepeatableList](TD1, optional=True, repeatable=True)
    routings   = EDISegmentAttr[EDIRepeatableList](TD5, optional=True, repeatable=True)
    equipment  = EDISegmentAttr[EDIRepeatableList](TD3, optional=True, repeatable=True)
    orders     = EDISegmentAttr[EDIRepeatableList](PRF, optional=True, repeatable=True)
    marks      = EDISegmentAttr[EDIRepeatableList](MAN, optional=True, repeatable=True)
    items      = EDISegmentAttr[EDIRepeatableList](LIN, optional=True, repeatable=True)
    shipped    = EDISegmentAttr[EDIRepeatableList](SN1, optional=True, repeatable=True)
    packaging  = EDISegmentAttr[EDIRepeatableList](PO4, optional=True, repeatable=True)
    references = EDISegmentAttr[EDIRepeatableList](REF, optional=True, repeatable=True)
    parties    = EDIGroupAttr[EDIRepeatableList](Party, optional=True)
    ctt        = EDISegmentAttr[CTT](CTT, optional=True)
    se         = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class InvoiceLine(EDIGroup):
    """ One IT1 line loop of an 810 - the baseline item data with its descriptions.
    """
    _leader_tag = 'IT1'

    it1          = EDISegmentAttr[IT1](IT1)
    descriptions = EDISegmentAttr[EDIRepeatableList](PID, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class Invoice810(X12Message):
    """ 810 invoice, version 004010 - the supplier's invoice against a purchase order.
    """
    _message_type = '810'
    _message_version = '004010'

    st         = EDISegmentAttr[ST](ST)
    big        = EDISegmentAttr[BIG](BIG)
    references = EDISegmentAttr[EDIRepeatableList](REF, optional=True, repeatable=True)
    parties    = EDIGroupAttr[EDIRepeatableList](Party, optional=True)
    terms      = EDISegmentAttr[ITD](ITD, optional=True)
    dates      = EDISegmentAttr[EDIRepeatableList](DTM, optional=True, repeatable=True)
    lines      = EDIGroupAttr[EDIRepeatableList](InvoiceLine)
    total      = EDISegmentAttr[TDS](TDS, optional=True)
    taxes      = EDISegmentAttr[EDIRepeatableList](TXI, optional=True, repeatable=True)
    charges    = EDISegmentAttr[EDIRepeatableList](SAC, optional=True, repeatable=True)
    shipment   = EDISegmentAttr[ISS](ISS, optional=True)
    ctt        = EDISegmentAttr[CTT](CTT, optional=True)
    se         = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################
