# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.x12.envelope import parse_x12
from zato.x12.validation import Element_Mandatory_Missing, Element_Too_Long, Element_Too_Short, Segment_Mandatory_Missing, \
     Segment_Unrecognized, X12ValidationError, extract_business_key, validate_snip_2, validate_transaction_set

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators.
_isa = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
       '*260709*1200*U*00401*000000905*0*P*>~'

# A version 00501 healthcare envelope with the colon component separator the guides use.
_isa_hipaa = 'ISA*00*          *00*          *ZZ*SUBMITTERID    *ZZ*PAYERID        ' + \
             '*260709*1200*^*00501*000000101*1*P*:~'


def _in_group(functional_id:'str', version:'str', body:'str', set_count:'int'=1, isa:'str'=_isa) -> 'str':
    """ Wraps a transaction set body in a full interchange whose IEA echoes the ISA13.
    """
    control_number = isa.split('*')[13]

    out = isa + \
        f'GS*{functional_id}*SENDERGS*RECEIVERGS*20260709*1200*905*X*{version}~' + \
        body + \
        f'GE*{set_count}*905~' + \
        f'IEA*1*{control_number}~'
    return out


# A clean 810 - the lines sum to the TDS total and the CTT count matches.
_invoice_clean = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'IT1*2*5*CA*30.00*TE*UP*036000291452~' + \
    'TDS*24750~' + \
    'CTT*2~' + \
    'SE*7*0001~'

# The same 810 with an unrecognized segment inside.
_invoice_unknown_segment = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    'ZZZ*1~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'IT1*2*5*CA*30.00*TE*UP*036000291452~' + \
    'TDS*24750~' + \
    'CTT*2~' + \
    'SE*8*0001~'

# An 810 whose BIG has no invoice number - a mandatory element is missing.
_invoice_missing_element = 'ST*810*0001~' + \
    'BIG*20260715~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'TDS*9750~' + \
    'CTT*1~' + \
    'SE*6*0001~'

# An 810 without any IT1 lines - a mandatory segment is missing.
_invoice_missing_segment = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981~' + \
    'TDS*0~' + \
    'SE*4*0001~'

# An 850 whose BEG purpose code is one character - shorter than its ID 2/2 format allows.
_order_short_element = 'ST*850*0001~' + \
    'BEG*0*SA*PO-4529**20260709~' + \
    'PO1*1*10*EA*9.75~' + \
    'SE*4*0001~'

# An 850 whose BEG03 purchase order number is longer than its 22-character maximum.
_order_long_element = 'ST*850*0001~' + \
    'BEG*00*SA*PO-45290000000000000000000000**20260709~' + \
    'PO1*1*10*EA*9.75~' + \
    'SE*4*0001~'

# A clean 856 with the standard-pack shipment-order-pack-item tree.
_ship_notice_clean = 'ST*856*0001~' + \
    'BSN*00*SHIP-88112*20260710*0830~' + \
    'HL*1**S~' + \
    'TD1*CTN25*8~' + \
    'HL*2*1*O~' + \
    'PRF*PO-4529~' + \
    'HL*3*2*P~' + \
    'MAN*GM*000001234500000003~' + \
    'HL*4*3*I~' + \
    'LIN**UP*036000291452~' + \
    'SN1**10*EA~' + \
    'CTT*4~' + \
    'SE*13*0001~'

# A minimal 837P with one claim.
_claim_clean = 'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'CLM*PATIENT-001*150~' + \
    'HI*ABK:J039~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1~' + \
    'SE*7*0001~'

# A minimal 835 that balances - BPR02 is CLP04 minus the PLB adjustment.
_remittance_clean = 'ST*835*0001~' + \
    'BPR*I*75*C*ACH~' + \
    'TRN*1*12345~' + \
    'CLP*PATIENT-001*1*150*100~' + \
    'PLB*1234567893*20261231*WO:PATIENT-002*25~' + \
    'SE*6*0001~'

# An 837P whose HI diagnosis composite has no code component.
_claim_bad_composite = 'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'CLM*PATIENT-001*150~' + \
    'HI*ABK~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1~' + \
    'SE*7*0001~'

# A price catalog - a set type without a registered class.
_generic_set = 'ST*832*0001~BCT*PC~SE*3*0001~'

# ################################################################################################################################
# ################################################################################################################################

class TestStrictParsing(unittest.TestCase):

    maxDiff = None

    def test_clean_interchange_parses_strictly(self) -> None:
        interchange = parse_x12(_in_group('IN', '004010', _invoice_clean), strict=True)
        self.assertEqual(len(interchange.groups), 1)

    def test_lenient_mode_never_raises_on_content(self) -> None:
        interchange = parse_x12(_in_group('IN', '004010', _invoice_unknown_segment))
        message = interchange.transaction_set

        # The unknown segment stays reachable positionally
        unknown = message.segments('ZZZ')
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0].e_1, '1')

    def test_unknown_segment_is_rejected(self) -> None:
        with self.assertRaises(X12ValidationError) as ctx:
            _ = parse_x12(_in_group('IN', '004010', _invoice_unknown_segment), strict=True)

        results = ctx.exception.results
        self.assertEqual(len(results), 1)

        issues = results[0].issues
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.segment_tag, 'ZZZ')
        self.assertEqual(issue.segment_position, 3)
        self.assertEqual(issue.segment_error_code, Segment_Unrecognized)

    def test_missing_mandatory_element(self) -> None:
        with self.assertRaises(X12ValidationError) as ctx:
            _ = parse_x12(_in_group('IN', '004010', _invoice_missing_element), strict=True)

        issues = ctx.exception.results[0].issues
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.segment_tag, 'BIG')
        self.assertEqual(issue.segment_position, 2)
        self.assertEqual(issue.element_position, 2)
        self.assertEqual(issue.element_error_code, Element_Mandatory_Missing)

    def test_missing_mandatory_segment(self) -> None:
        with self.assertRaises(X12ValidationError) as ctx:
            _ = parse_x12(_in_group('IN', '004010', _invoice_missing_segment), strict=True)

        issues = ctx.exception.results[0].issues
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.segment_tag, 'IT1')
        self.assertEqual(issue.segment_error_code, Segment_Mandatory_Missing)

    def test_element_too_short(self) -> None:
        with self.assertRaises(X12ValidationError) as ctx:
            _ = parse_x12(_in_group('PO', '004010', _order_short_element), strict=True)

        issues = ctx.exception.results[0].issues
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.segment_tag, 'BEG')
        self.assertEqual(issue.element_position, 1)
        self.assertEqual(issue.element_error_code, Element_Too_Short)
        self.assertEqual(issue.value, '0')

    def test_element_too_long(self) -> None:
        with self.assertRaises(X12ValidationError) as ctx:
            _ = parse_x12(_in_group('PO', '004010', _order_long_element), strict=True)

        issues = ctx.exception.results[0].issues
        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.segment_tag, 'BEG')
        self.assertEqual(issue.element_position, 3)
        self.assertEqual(issue.element_error_code, Element_Too_Long)

    def test_composite_component_missing(self) -> None:
        interchange = parse_x12(_in_group('HC', '005010X222A1', _claim_bad_composite, isa=_isa_hipaa))
        issues = validate_snip_2(interchange.transaction_set)

        self.assertEqual(len(issues), 1)

        issue = issues[0]
        self.assertEqual(issue.segment_tag, 'HI')
        self.assertEqual(issue.element_position, 1)
        self.assertEqual(issue.component_position, 2)
        self.assertEqual(issue.element_error_code, Element_Mandatory_Missing)

    def test_all_issues_are_collected(self) -> None:
        # An unknown segment plus a missing element plus a missing IT1 - everything reported at once
        body = 'ST*810*0001~' + \
            'BIG*20260715~' + \
            'ZZZ*1~' + \
            'TDS*0~' + \
            'SE*5*0001~'

        with self.assertRaises(X12ValidationError) as ctx:
            _ = parse_x12(_in_group('IN', '004010', body), strict=True)

        issues = ctx.exception.results[0].issues
        self.assertEqual(len(issues), 3)

    def test_generic_message_is_always_clean(self) -> None:
        interchange = parse_x12(_in_group('SC', '004010', _generic_set), strict=True)

        message = interchange.transaction_set
        issues = validate_transaction_set(message)
        self.assertEqual(issues, [])

    def test_clean_hipaa_interchange_parses_strictly(self) -> None:
        interchange = parse_x12(_in_group('HC', '005010X222A1', _claim_clean, isa=_isa_hipaa), strict=True)
        self.assertEqual(len(interchange.groups), 1)

# ################################################################################################################################
# ################################################################################################################################

class TestBusinessKeys(unittest.TestCase):

    maxDiff = None

    def test_purchase_order_key(self) -> None:
        body = 'ST*850*0001~BEG*00*SA*PO-4529**20260709~PO1*1*10*EA*9.75~SE*4*0001~'
        message = parse_x12(_in_group('PO', '004010', body)).transaction_set

        self.assertEqual(extract_business_key(message), 'PO-4529')

    def test_invoice_key(self) -> None:
        message = parse_x12(_in_group('IN', '004010', _invoice_clean)).transaction_set
        self.assertEqual(extract_business_key(message), 'INV-9981')

    def test_ship_notice_key(self) -> None:
        message = parse_x12(_in_group('SH', '004010', _ship_notice_clean)).transaction_set
        self.assertEqual(extract_business_key(message), 'SHIP-88112')

    def test_claim_key(self) -> None:
        message = parse_x12(_in_group('HC', '005010X222A1', _claim_clean, isa=_isa_hipaa)).transaction_set
        self.assertEqual(extract_business_key(message), 'PATIENT-001')

    def test_remittance_key(self) -> None:
        message = parse_x12(_in_group('HP', '005010X221A1', _remittance_clean, isa=_isa_hipaa)).transaction_set
        self.assertEqual(extract_business_key(message), '12345')

    def test_unknown_set_has_no_key(self) -> None:
        message = parse_x12(_in_group('SC', '004010', _generic_set)).transaction_set
        self.assertEqual(extract_business_key(message), '')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
