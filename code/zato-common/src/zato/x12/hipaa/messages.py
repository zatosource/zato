# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The transaction set definitions of the version 005010 US healthcare pattern -
# 837P and 837I claims, 835 remittance and 270/271 eligibility.

from __future__ import annotations

# Zato
from zato.x12.base import EDIGroup, EDIGroupAttr, EDIRepeatableList, EDISegmentAttr, X12Message
from zato.x12.hipaa.segments import AAA, BHT, BPR, CAS, CLM, CLP, DMG, DTM, DTP, EB, EQ, HI, LX, N1, N3, N4, NM1, PER, PLB, \
     REF, SV1, SV2, SVC, TRN
from zato.x12.service import SE, ST

# ################################################################################################################################
# ################################################################################################################################

class ProfessionalServiceLine(EDIGroup):
    """ One 2400 service line loop of an 837P - the LX with its SV1 professional service
    and DTP service dates.
    """
    _leader_tag = 'LX'

    lx      = EDISegmentAttr[LX](LX)
    service = EDISegmentAttr[SV1](SV1)
    dates   = EDISegmentAttr[EDIRepeatableList](DTP, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class ProfessionalClaim(EDIGroup):
    """ One 2300 claim loop of an 837P - the CLM with its HI diagnosis codes
    and the 2400 service line loops.
    """
    _leader_tag = 'CLM'

    clm           = EDISegmentAttr[CLM](CLM)
    diagnoses     = EDISegmentAttr[EDIRepeatableList](HI, optional=True, repeatable=True)
    service_lines = EDIGroupAttr[EDIRepeatableList](ProfessionalServiceLine)

# ################################################################################################################################
# ################################################################################################################################

class Claim837P(X12Message):
    """ 837P professional claim, implementation 005010X222A1 - the claim a physician practice
    or clearinghouse submits. The 2000A/2000B HL loops are reachable through the
    hierarchy property.
    """
    _message_type = '837'
    _message_version = '005010X222A1'

    st       = EDISegmentAttr[ST](ST)
    bht      = EDISegmentAttr[BHT](BHT)
    names    = EDISegmentAttr[EDIRepeatableList](NM1, optional=True, repeatable=True)
    contacts = EDISegmentAttr[EDIRepeatableList](PER, optional=True, repeatable=True)
    claims   = EDIGroupAttr[EDIRepeatableList](ProfessionalClaim)
    se       = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class InstitutionalServiceLine(EDIGroup):
    """ One 2400 service line loop of an 837I - the LX with its SV2 institutional service
    and DTP service dates.
    """
    _leader_tag = 'LX'

    lx      = EDISegmentAttr[LX](LX)
    service = EDISegmentAttr[SV2](SV2)
    dates   = EDISegmentAttr[EDIRepeatableList](DTP, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class InstitutionalClaim(EDIGroup):
    """ One 2300 claim loop of an 837I - the CLM with its HI diagnosis codes
    and the 2400 service line loops.
    """
    _leader_tag = 'CLM'

    clm           = EDISegmentAttr[CLM](CLM)
    diagnoses     = EDISegmentAttr[EDIRepeatableList](HI, optional=True, repeatable=True)
    service_lines = EDIGroupAttr[EDIRepeatableList](InstitutionalServiceLine)

# ################################################################################################################################
# ################################################################################################################################

class Claim837I(X12Message):
    """ 837I institutional claim, implementation 005010X223A2 - the claim a hospital submits.
    The 2000A/2000B HL loops are reachable through the hierarchy property.
    """
    _message_type = '837'
    _message_version = '005010X223A2'

    st       = EDISegmentAttr[ST](ST)
    bht      = EDISegmentAttr[BHT](BHT)
    names    = EDISegmentAttr[EDIRepeatableList](NM1, optional=True, repeatable=True)
    contacts = EDISegmentAttr[EDIRepeatableList](PER, optional=True, repeatable=True)
    claims   = EDIGroupAttr[EDIRepeatableList](InstitutionalClaim)
    se       = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class RemittanceParty(EDIGroup):
    """ One N1 party loop of an 835 - the payer (PR) or payee (PE) with its address.
    """
    _leader_tag = 'N1'

    n1       = EDISegmentAttr[N1](N1)
    address  = EDISegmentAttr[EDIRepeatableList](N3, optional=True, repeatable=True)
    location = EDISegmentAttr[N4](N4, optional=True)

# ################################################################################################################################
# ################################################################################################################################

class ServicePayment(EDIGroup):
    """ One SVC service payment of an 835 claim payment, with its dates.
    """
    _leader_tag = 'SVC'

    svc   = EDISegmentAttr[SVC](SVC)
    dates = EDISegmentAttr[EDIRepeatableList](DTM, optional=True, repeatable=True)

# ################################################################################################################################
# ################################################################################################################################

class ClaimPayment(EDIGroup):
    """ One CLP claim-payment loop of an 835 - the payment with its CAS adjustments
    and SVC service lines.
    """
    _leader_tag = 'CLP'

    clp         = EDISegmentAttr[CLP](CLP)
    adjustments = EDISegmentAttr[EDIRepeatableList](CAS, optional=True, repeatable=True)
    services    = EDIGroupAttr[EDIRepeatableList](ServicePayment)

# ################################################################################################################################
# ################################################################################################################################

class Remittance835(X12Message):
    """ 835 remittance advice, implementation 005010X221A1 - the payer's payment order
    with per-claim and provider-level adjustments.
    """
    _message_type = '835'
    _message_version = '005010X221A1'

    st          = EDISegmentAttr[ST](ST)
    bpr         = EDISegmentAttr[BPR](BPR)
    trace       = EDISegmentAttr[TRN](TRN)
    parties     = EDIGroupAttr[EDIRepeatableList](RemittanceParty, optional=True)
    payments    = EDIGroupAttr[EDIRepeatableList](ClaimPayment)
    adjustments = EDISegmentAttr[EDIRepeatableList](PLB, optional=True, repeatable=True)
    se          = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class EligibilityInquiry270(X12Message):
    """ 270 eligibility inquiry, implementation 005010X279A1 - who is asking about whose
    coverage. The 2000A/2000B/2000C/2000D HL loops are reachable through the hierarchy property.
    """
    _message_type = '270'
    _message_version = '005010X279A1'

    st        = EDISegmentAttr[ST](ST)
    bht       = EDISegmentAttr[BHT](BHT)
    names     = EDISegmentAttr[EDIRepeatableList](NM1, optional=True, repeatable=True)
    birth     = EDISegmentAttr[DMG](DMG, optional=True)
    dates     = EDISegmentAttr[EDIRepeatableList](DTP, optional=True, repeatable=True)
    inquiries = EDISegmentAttr[EDIRepeatableList](EQ, optional=True, repeatable=True)
    se        = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################

class EligibilityResponse271(X12Message):
    """ 271 eligibility response, implementation 005010X279A1 - the benefit information
    and any AAA rejection reasons. The HL loops are reachable through the hierarchy property.
    """
    _message_type = '271'
    _message_version = '005010X279A1'

    st         = EDISegmentAttr[ST](ST)
    bht        = EDISegmentAttr[BHT](BHT)
    names      = EDISegmentAttr[EDIRepeatableList](NM1, optional=True, repeatable=True)
    references = EDISegmentAttr[EDIRepeatableList](REF, optional=True, repeatable=True)
    benefits   = EDISegmentAttr[EDIRepeatableList](EB, optional=True, repeatable=True)
    rejections = EDISegmentAttr[EDIRepeatableList](AAA, optional=True, repeatable=True)
    se         = EDISegmentAttr[SE](SE)

# ################################################################################################################################
# ################################################################################################################################
