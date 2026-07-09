# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SNIP conformance suite - types 1 through 4 asserted by name.
# Type 1 is EDI syntax integrity, type 2 is implementation guide syntax,
# type 3 is balancing and type 4 is the inter-segment situational rules.

# stdlib
import unittest

# Zato
from zato.x12.envelope import parse_x12
from zato.x12.validation import validate_snip_1, validate_snip_2, validate_snip_3, validate_snip_4

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators.
_isa = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
       '*260709*1200*U*00401*000000905*0*P*>~'

# A version 00501 healthcare envelope with the colon component separator the guides use.
_isa_hipaa = 'ISA*00*          *00*          *ZZ*SUBMITTERID    *ZZ*PAYERID        ' + \
             '*260709*1200*^*00501*000000101*1*P*:~'


def _in_group(functional_id:'str', version:'str', body:'str', isa:'str'=_isa) -> 'str':
    """ Wraps a transaction set body in a full interchange whose IEA echoes the ISA13.
    """
    control_number = isa.split('*')[13]

    out = isa + \
        f'GS*{functional_id}*SENDERGS*RECEIVERGS*20260709*1200*905*X*{version}~' + \
        body + \
        'GE*1*905~' + \
        f'IEA*1*{control_number}~'
    return out


# A clean 810 - the lines sum to the TDS total and the CTT count matches.
_invoice_balanced = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'IT1*2*5*CA*30.00*TE*UP*036000291452~' + \
    'TDS*24750~' + \
    'CTT*2~' + \
    'SE*7*0001~'

# The same 810 with a TDS total that does not match the lines.
_invoice_unbalanced = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'IT1*2*5*CA*30.00*TE*UP*036000291452~' + \
    'TDS*99999~' + \
    'CTT*2~' + \
    'SE*7*0001~'

# An 850 whose CTT hash total matches the sum of the line quantities.
_order_balanced = 'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    'PO1*1*10*EA*9.75~' + \
    'PO1*2*5*CA*30.00~' + \
    'CTT*2*15~' + \
    'SE*6*0001~'

# The same 850 with a wrong line count in CTT01.
_order_bad_count = 'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    'PO1*1*10*EA*9.75~' + \
    'PO1*2*5*CA*30.00~' + \
    'CTT*3*15~' + \
    'SE*6*0001~'

# An 856 whose CTT01 matches its HL count.
_ship_notice_balanced = 'ST*856*0001~' + \
    'BSN*00*SHIP-88112*20260710*0830~' + \
    'HL*1**S~' + \
    'HL*2*1*O~' + \
    'HL*3*2*I~' + \
    'CTT*3~' + \
    'SE*7*0001~'

# An 835 that balances - BPR02 is the sum of CLP04 minus the PLB adjustment.
_remittance_balanced = 'ST*835*0001~' + \
    'BPR*I*75*C*ACH~' + \
    'TRN*1*12345~' + \
    'CLP*PATIENT-001*1*150*100~' + \
    'PLB*1234567893*20261231*WO:PATIENT-002*25~' + \
    'SE*6*0001~'

# The same 835 with a BPR02 that does not reconcile.
_remittance_unbalanced = 'ST*835*0001~' + \
    'BPR*I*100*C*ACH~' + \
    'TRN*1*12345~' + \
    'CLP*PATIENT-001*1*150*100~' + \
    'PLB*1234567893*20261231*WO:PATIENT-002*25~' + \
    'SE*6*0001~'

# A clean 837P claim.
_claim_clean = 'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'CLM*PATIENT-001*150~' + \
    'HI*ABK:J039~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1~' + \
    'SE*7*0001~'

# An 837P whose claim carries no diagnosis and no service line.
_claim_bare = 'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'CLM*PATIENT-001*150~' + \
    'SE*4*0001~'

# An 835 with a denied claim that still pays out.
_remittance_denied_paid = 'ST*835*0001~' + \
    'BPR*I*50*C*ACH~' + \
    'TRN*1*12345~' + \
    'CLP*PATIENT-001*4*150*50~' + \
    'SE*5*0001~'

# A 270 with the subscriber loop and the insured subscriber name.
_inquiry_clean = 'ST*270*0001*005010X279A1~' + \
    'BHT*0022*13*INQ-1001*20260709*1200~' + \
    'HL*1**20*1~' + \
    'NM1*PR*2*Acme Health Plan*****PI*66783~' + \
    'HL*2*1*21*1~' + \
    'NM1*1P*2*Sunrise Family Practice*****XX*1234567893~' + \
    'HL*3*2*22*0~' + \
    'NM1*IL*1*Doe*John****MI*MEMBER123~' + \
    'EQ*30~' + \
    'SE*10*0001~'

# A 270 whose subscriber loop has no NM1 with the IL entity code.
_inquiry_no_subscriber = 'ST*270*0001*005010X279A1~' + \
    'BHT*0022*13*INQ-1001*20260709*1200~' + \
    'HL*1**20*1~' + \
    'NM1*PR*2*Acme Health Plan*****PI*66783~' + \
    'HL*3*1*22*0~' + \
    'EQ*30~' + \
    'SE*7*0001~'

# ################################################################################################################################
# ################################################################################################################################

class TestSnipType1(unittest.TestCase):
    """ SNIP type 1 - EDI syntax integrity: control numbers, counts and separators.
    """

    maxDiff = None

    def test_snip_1_clean(self) -> None:
        errors = validate_snip_1(_in_group('IN', '004010', _invoice_balanced))
        self.assertEqual(errors, [])

    def test_snip_1_control_number_mismatch(self) -> None:
        raw = _in_group('IN', '004010', _invoice_balanced)
        raw = raw.replace('IEA*1*000000905~', 'IEA*1*000000999~')

        errors = validate_snip_1(raw)
        self.assertEqual(len(errors), 1)
        self.assertIn('does not match IEA02', errors[0])

    def test_snip_1_wrong_segment_count(self) -> None:
        raw = _in_group('IN', '004010', _invoice_balanced)
        raw = raw.replace('SE*7*0001~', 'SE*9*0001~')

        errors = validate_snip_1(raw)
        self.assertEqual(len(errors), 1)
        self.assertIn('does not match the segment count', errors[0])

# ################################################################################################################################
# ################################################################################################################################

class TestSnipType2(unittest.TestCase):
    """ SNIP type 2 - implementation guide syntax: usage, code sets and lengths per the TR3.
    """

    maxDiff = None

    def test_snip_2_clean(self) -> None:
        message = parse_x12(_in_group('IN', '004010', _invoice_balanced)).transaction_set
        issues = validate_snip_2(message)
        self.assertEqual(issues, [])

    def test_snip_2_finds_issues(self) -> None:
        body = _invoice_balanced.replace('SE*7*0001~', 'ZZZ*1~SE*8*0001~')
        message = parse_x12(_in_group('IN', '004010', body)).transaction_set

        issues = validate_snip_2(message)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].segment_tag, 'ZZZ')

# ################################################################################################################################
# ################################################################################################################################

class TestSnipType3(unittest.TestCase):
    """ SNIP type 3 - balancing: TDS01 against the line amounts, CTT counts
    and hash totals, and 835 amounts reconciling to BPR02.
    """

    maxDiff = None

    def test_snip_3_invoice_balanced(self) -> None:
        message = parse_x12(_in_group('IN', '004010', _invoice_balanced)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

    def test_snip_3_invoice_unbalanced(self) -> None:
        message = parse_x12(_in_group('IN', '004010', _invoice_unbalanced)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('TDS01', issues[0])

    def test_snip_3_order_balanced(self) -> None:
        message = parse_x12(_in_group('PO', '004010', _order_balanced)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

    def test_snip_3_order_bad_count(self) -> None:
        message = parse_x12(_in_group('PO', '004010', _order_bad_count)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('CTT01', issues[0])

    def test_snip_3_order_bad_hash_total(self) -> None:
        body = _order_balanced.replace('CTT*2*15~', 'CTT*2*99~')
        message = parse_x12(_in_group('PO', '004010', body)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('CTT02', issues[0])

    def test_snip_3_ship_notice_hl_count(self) -> None:
        message = parse_x12(_in_group('SH', '004010', _ship_notice_balanced)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

        body = _ship_notice_balanced.replace('CTT*3~', 'CTT*5~')
        message = parse_x12(_in_group('SH', '004010', body)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('CTT01', issues[0])

    def test_snip_3_remittance_balanced(self) -> None:
        message = parse_x12(_in_group('HP', '005010X221A1', _remittance_balanced, isa=_isa_hipaa)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

    def test_snip_3_remittance_unbalanced(self) -> None:
        message = parse_x12(_in_group('HP', '005010X221A1', _remittance_unbalanced, isa=_isa_hipaa)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('BPR02', issues[0])

# ################################################################################################################################
# ################################################################################################################################

class TestSnipType4(unittest.TestCase):
    """ SNIP type 4 - inter-segment situational rules from the implementation guides.
    """

    maxDiff = None

    def test_snip_4_claim_clean(self) -> None:
        message = parse_x12(_in_group('HC', '005010X222A1', _claim_clean, isa=_isa_hipaa)).transaction_set
        self.assertEqual(validate_snip_4(message), [])

    def test_snip_4_claim_without_diagnosis_or_lines(self) -> None:
        message = parse_x12(_in_group('HC', '005010X222A1', _claim_bare, isa=_isa_hipaa)).transaction_set

        issues = validate_snip_4(message)
        self.assertEqual(len(issues), 2)
        self.assertIn('no HI diagnosis codes', issues[0])
        self.assertIn('no LX service lines', issues[1])

    def test_snip_4_denied_claim_pays_nothing(self) -> None:
        message = parse_x12(_in_group('HP', '005010X221A1', _remittance_denied_paid, isa=_isa_hipaa)).transaction_set

        issues = validate_snip_4(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('Denied claim', issues[0])

    def test_snip_4_inquiry_clean(self) -> None:
        message = parse_x12(_in_group('HS', '005010X279A1', _inquiry_clean, isa=_isa_hipaa)).transaction_set
        self.assertEqual(validate_snip_4(message), [])

    def test_snip_4_inquiry_without_subscriber_name(self) -> None:
        message = parse_x12(_in_group('HS', '005010X279A1', _inquiry_no_subscriber, isa=_isa_hipaa)).transaction_set

        issues = validate_snip_4(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('no NM1 with entity code IL', issues[0])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
