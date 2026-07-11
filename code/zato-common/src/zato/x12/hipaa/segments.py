# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The segment definitions of the version 005010 US healthcare pattern - the segments
# shared by the 837 claims, 835 remittance and 270/271 eligibility transaction sets,
# covering the elements the CMS companion guides actually use.

from __future__ import annotations

# Zato
from zato.x12.base import EDIComponent, EDIComposite, EDIElement, Usage, X12Segment

# ################################################################################################################################
# ################################################################################################################################

class MedicalProcedure(EDIComposite):
    """ C003 - a composite medical procedure identifier, e.g. HC:99213 with optional modifiers.
    """
    qualifier  = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    code       = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='AN 1/48')
    modifier_1 = EDIComponent[str](position=3, usage=Usage.OPTIONAL, format='AN 2/2')
    modifier_2 = EDIComponent[str](position=4, usage=Usage.OPTIONAL, format='AN 2/2')

# ################################################################################################################################
# ################################################################################################################################

class HealthCareCode(EDIComposite):
    """ C022 - health care code information, e.g. ABK:J039 for an ICD-10-CM principal diagnosis.
    """
    qualifier = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='ID 1/3')
    code      = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='AN 1/30')

# ################################################################################################################################
# ################################################################################################################################

class FacilityCode(EDIComposite):
    """ C023 - the health care service location, e.g. 11:B:1 for an office place of service.
    """
    place_of_service = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='AN 1/2')
    qualifier        = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='ID 1/2')
    frequency        = EDIComponent[str](position=3, usage=Usage.OPTIONAL, format='AN 1/1')

# ################################################################################################################################
# ################################################################################################################################

class ProviderAdjustmentID(EDIComposite):
    """ C042 - the adjustment identifier of a PLB, a reason code with its reference.
    """
    reason_code = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    reference   = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='AN 1/50')

# ################################################################################################################################
# ################################################################################################################################

class BHT(X12Segment):
    """ Beginning of hierarchical transaction.
    """
    _segment_tag = 'BHT'

    structure_code   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 4/4')
    purpose_code     = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 2/2')
    reference        = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/50')
    date             = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='DT 8/8')
    time             = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='TM 4/8')
    transaction_type = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='ID 2/2')

# ################################################################################################################################
# ################################################################################################################################

class NM1(X12Segment):
    """ Individual or organizational name.
    """
    _segment_tag = 'NM1'

    entity_code  = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    entity_type  = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 1/1')
    last_name    = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/60')
    first_name   = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='AN 1/35')
    middle_name  = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='AN 1/25')
    name_prefix  = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='AN 1/10')
    name_suffix  = EDIElement[str](position=7, usage=Usage.OPTIONAL, format='AN 1/10')
    id_qualifier = EDIElement[str](position=8, usage=Usage.CONDITIONAL, format='ID 1/2')
    id_code      = EDIElement[str](position=9, usage=Usage.CONDITIONAL, format='AN 2/80')

# ################################################################################################################################
# ################################################################################################################################

class PER(X12Segment):
    """ Administrative communications contact.
    """
    _segment_tag = 'PER'

    contact_function        = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    name                    = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/60')
    communication_qualifier = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    communication_number    = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 1/256')

# ################################################################################################################################
# ################################################################################################################################

class N1(X12Segment):
    """ Name - the leader of the payer and payee identification loops of an 835.
    """
    _segment_tag = 'N1'

    entity_code  = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    name         = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='AN 1/60')
    id_qualifier = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 1/2')
    id_code      = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 2/80')

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

class REF(X12Segment):
    """ Reference identification.
    """
    _segment_tag = 'REF'

    qualifier   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/3')
    value       = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='AN 1/50')
    description = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/80')

# ################################################################################################################################
# ################################################################################################################################

class HL(X12Segment):
    """ Hierarchical level - the segment whose parent pointers build the 2000 loop trees.
    """
    _segment_tag = 'HL'

    hl_id      = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/12')
    parent_id  = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='AN 1/12')
    level_code = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 1/2')
    child_code = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='N0 1/1')

# ################################################################################################################################
# ################################################################################################################################

class SBR(X12Segment):
    """ Subscriber information.
    """
    _segment_tag = 'SBR'

    payer_responsibility = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    relationship         = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='ID 2/2')
    group_number         = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 1/50')
    group_name           = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='AN 1/60')
    claim_filing_code    = EDIElement[str](position=9, usage=Usage.CONDITIONAL, format='ID 1/2')

# ################################################################################################################################
# ################################################################################################################################

class DMG(X12Segment):
    """ Demographic information.
    """
    _segment_tag = 'DMG'

    format_qualifier = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='ID 2/3')
    date_of_birth    = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='AN 1/35')
    gender           = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='ID 1/1')

# ################################################################################################################################
# ################################################################################################################################

class CLM(X12Segment):
    """ Claim information - the leader of the 2300 claim loop.
    """
    _segment_tag = 'CLM'

    claim_id           = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/38')
    amount             = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/18')
    facility           = EDIElement[FacilityCode](position=5, usage=Usage.CONDITIONAL, composite='FacilityCode')
    provider_signature = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='ID 1/1')
    assignment_code    = EDIElement[str](position=7, usage=Usage.CONDITIONAL, format='ID 1/1')
    benefits_assigned  = EDIElement[str](position=8, usage=Usage.CONDITIONAL, format='ID 1/1')
    release_code       = EDIElement[str](position=9, usage=Usage.CONDITIONAL, format='ID 1/1')

# ################################################################################################################################
# ################################################################################################################################

class HI(X12Segment):
    """ Health care diagnosis codes.
    """
    _segment_tag = 'HI'

    code_1 = EDIElement[HealthCareCode](position=1, usage=Usage.REQUIRED, composite='HealthCareCode')
    code_2 = EDIElement[HealthCareCode](position=2, usage=Usage.OPTIONAL, composite='HealthCareCode')
    code_3 = EDIElement[HealthCareCode](position=3, usage=Usage.OPTIONAL, composite='HealthCareCode')
    code_4 = EDIElement[HealthCareCode](position=4, usage=Usage.OPTIONAL, composite='HealthCareCode')

# ################################################################################################################################
# ################################################################################################################################

class LX(X12Segment):
    """ Transaction set line number - the leader of the 2400 service line loop.
    """
    _segment_tag = 'LX'

    number = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N0 1/6')

# ################################################################################################################################
# ################################################################################################################################

class SV1(X12Segment):
    """ Professional service - the 837P service line.
    """
    _segment_tag = 'SV1'

    procedure         = EDIElement[MedicalProcedure](position=1, usage=Usage.REQUIRED, composite='MedicalProcedure')
    charge_amount     = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='R 1/18')
    unit              = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    quantity          = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='R 1/15')
    diagnosis_pointer = EDIElement[str](position=7, usage=Usage.CONDITIONAL, format='AN 1/20')

# ################################################################################################################################
# ################################################################################################################################

class SV2(X12Segment):
    """ Institutional service - the 837I service line.
    """
    _segment_tag = 'SV2'

    revenue_code  = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='AN 1/48')
    procedure     = EDIElement[MedicalProcedure](position=2, usage=Usage.CONDITIONAL, composite='MedicalProcedure')
    charge_amount = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='R 1/18')
    unit          = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='ID 2/2')
    quantity      = EDIElement[str](position=5, usage=Usage.CONDITIONAL, format='R 1/15')

# ################################################################################################################################
# ################################################################################################################################

class DTP(X12Segment):
    """ Date or time period.
    """
    _segment_tag = 'DTP'

    qualifier        = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 3/3')
    format_qualifier = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 2/3')
    date             = EDIElement[str](position=3, usage=Usage.REQUIRED, format='AN 1/35')

# ################################################################################################################################
# ################################################################################################################################

class DTM(X12Segment):
    """ Date/time reference - the 835 uses it for production and service dates.
    """
    _segment_tag = 'DTM'

    qualifier = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 3/3')
    date      = EDIElement[str](position=2, usage=Usage.CONDITIONAL, format='DT 8/8')

# ################################################################################################################################
# ################################################################################################################################

class BPR(X12Segment):
    """ Beginning segment for payment order/remittance advice.
    """
    _segment_tag = 'BPR'

    transaction_code = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/2')
    amount           = EDIElement[str](position=2, usage=Usage.REQUIRED, format='R 1/18')
    credit_debit     = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 1/1')
    payment_method   = EDIElement[str](position=4, usage=Usage.REQUIRED, format='ID 3/3')
    payment_format   = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='ID 1/10')
    date             = EDIElement[str](position=16, usage=Usage.CONDITIONAL, format='DT 8/8')

# ################################################################################################################################
# ################################################################################################################################

class TRN(X12Segment):
    """ Reassociation trace number.
    """
    _segment_tag = 'TRN'

    trace_type   = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/2')
    reference    = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 1/50')
    origin_id    = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='AN 10/10')

# ################################################################################################################################
# ################################################################################################################################

class CLP(X12Segment):
    """ Claim payment information - the leader of the 835 claim-payment loop.
    """
    _segment_tag = 'CLP'

    claim_id               = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/38')
    status_code            = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 1/2')
    charge_amount          = EDIElement[str](position=3, usage=Usage.REQUIRED, format='R 1/18')
    payment_amount         = EDIElement[str](position=4, usage=Usage.REQUIRED, format='R 1/18')
    patient_responsibility = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='R 1/18')
    claim_filing_code      = EDIElement[str](position=6, usage=Usage.CONDITIONAL, format='ID 1/2')
    payer_control_number   = EDIElement[str](position=7, usage=Usage.OPTIONAL, format='AN 1/50')
    facility_code          = EDIElement[str](position=8, usage=Usage.OPTIONAL, format='AN 1/2')

# ################################################################################################################################
# ################################################################################################################################

class CAS(X12Segment):
    """ Claims adjustment.
    """
    _segment_tag = 'CAS'

    group_code  = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/2')
    reason_code = EDIElement[str](position=2, usage=Usage.REQUIRED, format='ID 1/5')
    amount      = EDIElement[str](position=3, usage=Usage.REQUIRED, format='R 1/18')
    quantity    = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='R 1/15')

# ################################################################################################################################
# ################################################################################################################################

class SVC(X12Segment):
    """ Service payment information - one service line of an 835 claim payment.
    """
    _segment_tag = 'SVC'

    procedure      = EDIElement[MedicalProcedure](position=1, usage=Usage.REQUIRED, composite='MedicalProcedure')
    charge_amount  = EDIElement[str](position=2, usage=Usage.REQUIRED, format='R 1/18')
    payment_amount = EDIElement[str](position=3, usage=Usage.REQUIRED, format='R 1/18')

# ################################################################################################################################
# ################################################################################################################################

class PLB(X12Segment):
    """ Provider level adjustment.
    """
    _segment_tag = 'PLB'

    provider_id        = EDIElement[str](position=1, usage=Usage.REQUIRED, format='AN 1/50')
    fiscal_period_date = EDIElement[str](position=2, usage=Usage.REQUIRED, format='DT 8/8')
    adjustment_id      = EDIElement[ProviderAdjustmentID](position=3, usage=Usage.REQUIRED, composite='ProviderAdjustmentID')
    amount             = EDIElement[str](position=4, usage=Usage.REQUIRED, format='R 1/18')

# ################################################################################################################################
# ################################################################################################################################

class EQ(X12Segment):
    """ Eligibility or benefit inquiry.
    """
    _segment_tag = 'EQ'

    service_type = EDIElement[str](position=1, usage=Usage.CONDITIONAL, format='ID 1/2')

# ################################################################################################################################
# ################################################################################################################################

class EB(X12Segment):
    """ Eligibility or benefit information.
    """
    _segment_tag = 'EB'

    eligibility_code      = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/2')
    coverage_level        = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 3/3')
    service_type          = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='ID 1/2')
    insurance_type        = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='ID 1/3')
    plan_description      = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='AN 1/50')
    time_period_qualifier = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='ID 1/2')
    amount                = EDIElement[str](position=7, usage=Usage.OPTIONAL, format='R 1/18')

# ################################################################################################################################
# ################################################################################################################################

class AAA(X12Segment):
    """ Request validation - the rejection reasons of a 271.
    """
    _segment_tag = 'AAA'

    valid_request    = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 1/1')
    agency_code      = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='ID 1/2')
    reject_reason    = EDIElement[str](position=3, usage=Usage.CONDITIONAL, format='ID 2/2')
    follow_up_action = EDIElement[str](position=4, usage=Usage.CONDITIONAL, format='ID 1/1')

# ################################################################################################################################
# ################################################################################################################################
