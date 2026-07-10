# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The formal-document conformance suite. Every expected value below is typed out
# literally from the governing documents - the interchange control standards,
# the acknowledgment code tables and the CMS companion guides - never imported
# from the code under test. Every derived count and total is recomputed
# independently with plain string operations over the wire text, and the SNIP
# type 1 through 4 verdicts are asserted against those recomputations by name.
# Type 1 is EDI syntax integrity, type 2 is implementation guide syntax,
# type 3 is balancing and type 4 is the inter-segment situational rules.

# stdlib
import unittest
from decimal import Decimal

# Zato
from zato.common.typing_ import strlist
from zato.x12 import hipaa, retail
from zato.x12.ack import build_997, build_999
from zato.x12.envelope import parse_x12
from zato.x12.validation import validate_snip_1, validate_snip_2, validate_snip_3, validate_snip_4

# Importing the dictionary modules registers the typed transaction sets with the envelope layer.
hipaa = hipaa
retail = retail

# ################################################################################################################################
# ################################################################################################################################

# The interchange control header is fixed width - its sixteen elements have these
# exact widths, typed out from the interchange control standards.
_isa_element_widths = (2, 10, 2, 10, 2, 15, 2, 15, 6, 4, 1, 5, 9, 1, 1, 1)

# How many elements a well-formed ISA always has.
_isa_element_count = 16

# The whole ISA - tag, separators, elements and terminator - is exactly 106 characters.
_isa_total_length = 106

# The 1-based position of the nine-digit interchange control number, ISA13.
_isa_control_number_position = 13

# Data element 717, transaction set acknowledgment code - the AK501 and IK501 code table.
_set_ack_codes = ('A', 'E', 'M', 'R', 'W', 'X')

# Data element 715, functional group acknowledge code - the AK901 code table.
_group_ack_codes = ('A', 'E', 'M', 'P', 'R', 'W', 'X')

# Data element 718, AK502/IK502 - one or more segments were in error.
_set_error_segments_in_error = '5'

# Data element 720, AK304/IK304 - unrecognized segment ID.
_segment_error_unrecognized = '1'

# The implementation convention reference the HIPAA 999 must declare in its ST03.
_hipaa_999_reference = '005010X231A1'

# TDS01 and other monetary N2 values carry two implied decimal places.
_implied_decimal_places = Decimal(100)

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

# The same 810 with a segment its dictionary does not declare.
_invoice_with_unknown_segment = _invoice_balanced.replace('SE*7*0001~', 'ZZZ*1~SE*8*0001~')

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

# The same 837P with a segment its dictionary does not declare.
_claim_with_unknown_segment = _claim_clean.replace('SE*7*0001~', 'ZZZ*1~SE*8*0001~')

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

def _wire_of(raw:'str') -> 'str':
    """ Parses and re-serializes an interchange, dropping the visual newlines -
    the exact text the engine would put on the wire.
    """
    interchange = parse_x12(raw)
    serialized = interchange.serialize()

    out = serialized.replace('\n', '')
    return out

# ################################################################################################################################

def _split_wire(wire:'str') -> 'strlist':
    """ Splits wire text into segment strings with a plain split on the tilde -
    independent of the syntax layer under test.
    """

    # Our response to produce
    out:'strlist' = []

    flattened = wire.replace('\n', '')
    parts = flattened.split('~')

    for part in parts:
        if part:
            out.append(part)

    return out

# ################################################################################################################################

def _segments_with_tag(segments:'strlist', tag:'str') -> 'strlist':
    """ Returns the segments with the given tag, matched on the text before the first separator.
    """

    # Our response to produce
    out:'strlist' = []

    for segment in segments:
        elements = segment.split('*')
        if elements[0] == tag:
            out.append(segment)

    return out

# ################################################################################################################################

def _elements_of_first(segments:'strlist', tag:'str') -> 'strlist':
    """ Returns the elements of the first segment with the given tag.
    """
    matching = _segments_with_tag(segments, tag)
    first = matching[0]

    out = first.split('*')
    return out

# ################################################################################################################################

def _recompute_invoice_total_cents(body:'str') -> 'int':
    """ Sums the IT1 line amounts of an 810 - quantity times unit price - with plain
    string operations, returning the total in the two-implied-decimals form of TDS01.
    """
    segments = _split_wire(body)
    line_segments = _segments_with_tag(segments, 'IT1')

    total = Decimal(0)

    for segment in line_segments:
        elements = segment.split('*')
        quantity = Decimal(elements[2])
        unit_price = Decimal(elements[4])
        total += quantity * unit_price

    total_cents = total * _implied_decimal_places

    out = int(total_cents)
    return out

# ################################################################################################################################

def _recompute_order_hash_total(body:'str') -> 'Decimal':
    """ Sums the PO102 quantities of an 850 with plain string operations -
    what CTT02 declares as the hash total.
    """

    # Our response to produce
    out = Decimal(0)

    segments = _split_wire(body)
    line_segments = _segments_with_tag(segments, 'PO1')

    for segment in line_segments:
        elements = segment.split('*')
        out += Decimal(elements[2])

    return out

# ################################################################################################################################

def _recompute_remittance_payment(body:'str') -> 'Decimal':
    """ Recomputes the 835 payment order amount with plain string operations -
    the sum of the CLP04 claim payments minus the PLB provider-level adjustments.
    """
    segments = _split_wire(body)

    claim_segments = _segments_with_tag(segments, 'CLP')
    claim_total = Decimal(0)

    for segment in claim_segments:
        elements = segment.split('*')
        claim_total += Decimal(elements[4])

    adjustment_segments = _segments_with_tag(segments, 'PLB')
    adjustment_total = Decimal(0)

    for segment in adjustment_segments:
        elements = segment.split('*')
        adjustment_total += Decimal(elements[4])

    out = claim_total - adjustment_total
    return out

# ################################################################################################################################

def _build_997_wire(body:'str', functional_id:'str', version:'str') -> 'str':
    """ Builds a 997 for the given transaction set body and returns the acknowledgment's wire text.
    """
    interchange = parse_x12(_in_group(functional_id, version, body))
    acknowledgment = build_997(interchange)
    serialized = acknowledgment.serialize()

    out = serialized.replace('\n', '')
    return out

# ################################################################################################################################

def _build_999_wire(body:'str', functional_id:'str', version:'str') -> 'str':
    """ Builds a 999 for the given transaction set body and returns the acknowledgment's wire text.
    """
    interchange = parse_x12(_in_group(functional_id, version, body, isa=_isa_hipaa))
    acknowledgment = build_999(interchange)
    serialized = acknowledgment.serialize()

    out = serialized.replace('\n', '')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestISAFixedWidth(unittest.TestCase):
    """ The interchange control header is fixed width - the sixteen literal element
    widths dictate where every separator sits and make the segment exactly
    106 characters, checked here over the engine's own wire output.
    """

    maxDiff = None

    def test_isa_is_exactly_106_characters(self) -> None:
        wire = _wire_of(_in_group('IN', '004010', _invoice_balanced))

        isa = wire[:_isa_total_length]

        # The tag opens the segment and the terminator closes it at the literal offset.
        self.assertTrue(isa.startswith('ISA*'))
        self.assertEqual(isa[_isa_total_length - 1], '~')

    def test_separators_sit_at_the_offsets_the_widths_dictate(self) -> None:
        wire = _wire_of(_in_group('IN', '004010', _invoice_balanced))

        # Walk the literal widths - an element separator must precede every element ..
        offset = len('ISA')

        for width in _isa_element_widths:
            self.assertEqual(wire[offset], '*')
            offset += 1 + width

        # .. and the terminator follows the sixteenth element, closing the 106 characters.
        self.assertEqual(wire[offset], '~')
        self.assertEqual(offset + 1, _isa_total_length)

    def test_element_values_have_the_literal_widths(self) -> None:
        wire = _wire_of(_in_group('IN', '004010', _invoice_balanced))

        # Split the fixed-width body on the element separator ..
        isa_body = wire[:_isa_total_length - 1]
        elements = isa_body.split('*')
        data_elements = elements[1:]

        # .. sixteen elements must be there ..
        data_element_count = len(data_elements)
        self.assertEqual(data_element_count, _isa_element_count)

        # .. and each one is padded to its literal width.
        for index, value in enumerate(data_elements):
            value_length = len(value)
            self.assertEqual(value_length, _isa_element_widths[index])

# ################################################################################################################################
# ################################################################################################################################

class TestEnvelopeCountsRecompute(unittest.TestCase):
    """ Every derived envelope count and control number echo is recomputed here
    with plain string operations over the wire text and compared with what
    the trailers declare - never through the classes under test.
    """

    maxDiff = None

    def test_se01_counts_every_segment_of_the_set(self) -> None:
        wire = _wire_of(_in_group('IN', '004010', _invoice_balanced))
        segments = _split_wire(wire)

        # Find where the transaction set starts and ends ..
        st_index = 0
        se_index = 0

        for index, segment in enumerate(segments):
            elements = segment.split('*')
            if elements[0] == 'ST':
                st_index = index
            elif elements[0] == 'SE':
                se_index = index

        # .. SE01 counts every segment from ST through SE inclusive ..
        actual_count = se_index - st_index + 1
        se_elements = _elements_of_first(segments, 'SE')
        declared_count = int(se_elements[1])

        self.assertEqual(declared_count, actual_count)

        # .. and SE02 echoes the ST02 set control number.
        st_elements = _elements_of_first(segments, 'ST')
        self.assertEqual(se_elements[2], st_elements[2])

    def test_ge_counts_the_sets_and_echoes_gs06(self) -> None:
        wire = _wire_of(_in_group('IN', '004010', _invoice_balanced))
        segments = _split_wire(wire)

        # GE01 counts the ST segments of its group ..
        set_segments = _segments_with_tag(segments, 'ST')
        set_count = len(set_segments)

        ge_elements = _elements_of_first(segments, 'GE')
        self.assertEqual(int(ge_elements[1]), set_count)

        # .. and GE02 echoes the GS06 group control number.
        gs_elements = _elements_of_first(segments, 'GS')
        self.assertEqual(ge_elements[2], gs_elements[6])

    def test_iea_counts_the_groups_and_echoes_isa13(self) -> None:
        wire = _wire_of(_in_group('IN', '004010', _invoice_balanced))
        segments = _split_wire(wire)

        # IEA01 counts the GS segments of the interchange ..
        group_segments = _segments_with_tag(segments, 'GS')
        group_count = len(group_segments)

        iea_elements = _elements_of_first(segments, 'IEA')
        self.assertEqual(int(iea_elements[1]), group_count)

        # .. and IEA02 echoes ISA13, read from the fixed-width header directly.
        isa_body = wire[:_isa_total_length - 1]
        isa_elements = isa_body.split('*')
        self.assertEqual(iea_elements[2], isa_elements[_isa_control_number_position])

# ################################################################################################################################
# ################################################################################################################################

class Test997Conformance(unittest.TestCase):
    """ The 997 carries codes from the literal acknowledgment code tables and its
    AK9 counts recompute from the acknowledgment's own wire text.
    """

    maxDiff = None

    def test_accepted_codes_come_from_the_literal_tables(self) -> None:
        wire = _build_997_wire(_invoice_balanced, 'IN', '004010')
        segments = _split_wire(wire)

        # A clean set is accepted with the literal per-set code ..
        ak5_elements = _elements_of_first(segments, 'AK5')
        self.assertEqual(ak5_elements[1], 'A')
        self.assertIn(ak5_elements[1], _set_ack_codes)

        # .. and the group code comes from the group-level table.
        ak9_elements = _elements_of_first(segments, 'AK9')
        self.assertEqual(ak9_elements[1], 'A')
        self.assertIn(ak9_elements[1], _group_ack_codes)

    def test_rejected_set_carries_the_literal_error_codes(self) -> None:
        wire = _build_997_wire(_invoice_with_unknown_segment, 'IN', '004010')
        segments = _split_wire(wire)

        # AK304 names the unrecognized segment with its literal code ..
        ak3_elements = _elements_of_first(segments, 'AK3')
        self.assertEqual(ak3_elements[1], 'ZZZ')
        self.assertEqual(ak3_elements[4], _segment_error_unrecognized)

        # .. AK5 rejects the set with the literal segments-in-error code ..
        ak5_elements = _elements_of_first(segments, 'AK5')
        self.assertEqual(ak5_elements[1], 'R')
        self.assertEqual(ak5_elements[2], _set_error_segments_in_error)

        # .. and the group is rejected as a whole.
        ak9_elements = _elements_of_first(segments, 'AK9')
        self.assertEqual(ak9_elements[1], 'R')

    def test_ak9_counts_recompute_from_the_wire(self) -> None:
        for body in (_invoice_balanced, _invoice_with_unknown_segment):

            wire = _build_997_wire(body, 'IN', '004010')
            segments = _split_wire(wire)

            # Count the acknowledged sets and the accepted ones by scanning the wire ..
            set_responses = _segments_with_tag(segments, 'AK2')
            response_count = len(set_responses)

            trailer_segments = _segments_with_tag(segments, 'AK5')
            accepted_count = 0

            for segment in trailer_segments:
                elements = segment.split('*')
                if elements[1] == 'A':
                    accepted_count += 1

            # .. AK902, AK903 and AK904 must declare exactly these counts.
            ak9_elements = _elements_of_first(segments, 'AK9')
            self.assertEqual(int(ak9_elements[2]), response_count)
            self.assertEqual(int(ak9_elements[3]), response_count)
            self.assertEqual(int(ak9_elements[4]), accepted_count)

# ################################################################################################################################
# ################################################################################################################################

class Test999Conformance(unittest.TestCase):
    """ The HIPAA 999 declares its literal implementation convention reference
    and carries IK3/CTX/IK5 details with codes from the literal tables.
    """

    maxDiff = None

    def test_999_declares_the_hipaa_implementation_reference(self) -> None:
        wire = _build_999_wire(_claim_clean, 'HC', '005010X222A1')
        segments = _split_wire(wire)

        # ST03 of a 999 is the implementation convention reference, typed out literally.
        st_elements = _elements_of_first(segments, 'ST')
        self.assertEqual(st_elements[1], '999')
        self.assertEqual(st_elements[3], _hipaa_999_reference)

    def test_accepted_set_carries_the_literal_acceptance_code(self) -> None:
        wire = _build_999_wire(_claim_clean, 'HC', '005010X222A1')
        segments = _split_wire(wire)

        ik5_elements = _elements_of_first(segments, 'IK5')
        self.assertEqual(ik5_elements[1], 'A')
        self.assertIn(ik5_elements[1], _set_ack_codes)

    def test_rejected_set_carries_the_literal_error_codes_and_context(self) -> None:
        wire = _build_999_wire(_claim_with_unknown_segment, 'HC', '005010X222A1')
        segments = _split_wire(wire)

        # IK304 names the unrecognized segment with its literal code ..
        ik3_elements = _elements_of_first(segments, 'IK3')
        self.assertEqual(ik3_elements[1], 'ZZZ')
        self.assertEqual(ik3_elements[4], _segment_error_unrecognized)

        # .. the CTX carries the business-unit reference of the rejected claim,
        # with the colon component separator the HIPAA envelopes use ..
        ctx_elements = _elements_of_first(segments, 'CTX')
        self.assertEqual(ctx_elements[1], 'CLM01:PATIENT-001')

        # .. and IK5 rejects the set with the literal segments-in-error code.
        ik5_elements = _elements_of_first(segments, 'IK5')
        self.assertEqual(ik5_elements[1], 'R')
        self.assertEqual(ik5_elements[2], _set_error_segments_in_error)

    def test_ak9_counts_recompute_from_the_wire(self) -> None:
        for body in (_claim_clean, _claim_with_unknown_segment):

            wire = _build_999_wire(body, 'HC', '005010X222A1')
            segments = _split_wire(wire)

            # Count the acknowledged sets and the accepted ones by scanning the wire ..
            set_responses = _segments_with_tag(segments, 'AK2')
            response_count = len(set_responses)

            trailer_segments = _segments_with_tag(segments, 'IK5')
            accepted_count = 0

            for segment in trailer_segments:
                elements = segment.split('*')
                if elements[1] == 'A':
                    accepted_count += 1

            # .. AK902, AK903 and AK904 must declare exactly these counts.
            ak9_elements = _elements_of_first(segments, 'AK9')
            self.assertEqual(int(ak9_elements[2]), response_count)
            self.assertEqual(int(ak9_elements[3]), response_count)
            self.assertEqual(int(ak9_elements[4]), accepted_count)

# ################################################################################################################################
# ################################################################################################################################

class TestSnipType1(unittest.TestCase):
    """ SNIP type 1 - EDI syntax integrity: control numbers, counts and separators,
    with the clean verdict cross-checked against an independent recomputation.
    """

    maxDiff = None

    def test_snip_1_clean(self) -> None:
        errors = validate_snip_1(_in_group('IN', '004010', _invoice_balanced))
        self.assertEqual(errors, [])

    def test_snip_1_verdict_agrees_with_independent_recomputation(self) -> None:
        raw = _in_group('IN', '004010', _invoice_balanced)
        segments = _split_wire(raw)

        # Recompute the envelope invariants with plain string operations -
        # IEA02 echoes ISA13 ..
        isa_elements = segments[0].split('*')
        iea_elements = _elements_of_first(segments, 'IEA')
        self.assertEqual(iea_elements[2], isa_elements[_isa_control_number_position])

        # .. GE02 echoes GS06 ..
        gs_elements = _elements_of_first(segments, 'GS')
        ge_elements = _elements_of_first(segments, 'GE')
        self.assertEqual(ge_elements[2], gs_elements[6])

        # .. and SE01 counts the set's segments, ST and SE included ..
        set_segment_count = 0

        for segment in segments:
            elements = segment.split('*')
            if elements[0] not in ('ISA', 'GS', 'GE', 'IEA'):
                set_segment_count += 1

        se_elements = _elements_of_first(segments, 'SE')
        self.assertEqual(int(se_elements[1]), set_segment_count)

        # .. so the validator must agree the interchange is sound.
        self.assertEqual(validate_snip_1(raw), [])

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
        message = parse_x12(_in_group('IN', '004010', _invoice_with_unknown_segment)).transaction_set

        issues = validate_snip_2(message)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].segment_tag, 'ZZZ')

# ################################################################################################################################
# ################################################################################################################################

class TestSnipType3(unittest.TestCase):
    """ SNIP type 3 - balancing: TDS01 against the line amounts, CTT counts
    and hash totals, and 835 amounts reconciling to BPR02 - each verdict
    cross-checked against an independent recomputation of the same total.
    """

    maxDiff = None

    def test_snip_3_invoice_balanced(self) -> None:
        # The independent line-total sum matches what TDS01 declares ..
        recomputed_cents = _recompute_invoice_total_cents(_invoice_balanced)
        segments = _split_wire(_invoice_balanced)
        tds_elements = _elements_of_first(segments, 'TDS')
        self.assertEqual(int(tds_elements[1]), recomputed_cents)

        # .. so the validator must agree the invoice balances.
        message = parse_x12(_in_group('IN', '004010', _invoice_balanced)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

    def test_snip_3_invoice_unbalanced(self) -> None:
        # The independent line-total sum disagrees with what TDS01 declares ..
        recomputed_cents = _recompute_invoice_total_cents(_invoice_unbalanced)
        segments = _split_wire(_invoice_unbalanced)
        tds_elements = _elements_of_first(segments, 'TDS')
        self.assertNotEqual(int(tds_elements[1]), recomputed_cents)

        # .. so the validator must flag exactly that disagreement.
        message = parse_x12(_in_group('IN', '004010', _invoice_unbalanced)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('TDS01', issues[0])

    def test_snip_3_order_balanced(self) -> None:
        # The independent quantity hash matches what CTT02 declares ..
        recomputed_hash = _recompute_order_hash_total(_order_balanced)
        segments = _split_wire(_order_balanced)
        ctt_elements = _elements_of_first(segments, 'CTT')
        self.assertEqual(Decimal(ctt_elements[2]), recomputed_hash)

        # .. so the validator must agree the order balances.
        message = parse_x12(_in_group('PO', '004010', _order_balanced)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

    def test_snip_3_order_bad_count(self) -> None:
        # The independent line count disagrees with what CTT01 declares ..
        segments = _split_wire(_order_bad_count)
        line_segments = _segments_with_tag(segments, 'PO1')
        line_count = len(line_segments)

        ctt_elements = _elements_of_first(segments, 'CTT')
        self.assertNotEqual(int(ctt_elements[1]), line_count)

        # .. so the validator must flag exactly that disagreement.
        message = parse_x12(_in_group('PO', '004010', _order_bad_count)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('CTT01', issues[0])

    def test_snip_3_order_bad_hash_total(self) -> None:
        body = _order_balanced.replace('CTT*2*15~', 'CTT*2*99~')

        # The independent quantity hash disagrees with what CTT02 declares ..
        recomputed_hash = _recompute_order_hash_total(body)
        segments = _split_wire(body)
        ctt_elements = _elements_of_first(segments, 'CTT')
        self.assertNotEqual(Decimal(ctt_elements[2]), recomputed_hash)

        # .. so the validator must flag exactly that disagreement.
        message = parse_x12(_in_group('PO', '004010', body)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('CTT02', issues[0])

    def test_snip_3_ship_notice_hl_count(self) -> None:
        # The independent HL count matches what CTT01 declares ..
        segments = _split_wire(_ship_notice_balanced)
        hierarchy_segments = _segments_with_tag(segments, 'HL')
        hierarchy_count = len(hierarchy_segments)

        ctt_elements = _elements_of_first(segments, 'CTT')
        self.assertEqual(int(ctt_elements[1]), hierarchy_count)

        # .. so the validator must agree the ship notice balances ..
        message = parse_x12(_in_group('SH', '004010', _ship_notice_balanced)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

        # .. and a wrong CTT01 is flagged as exactly that disagreement.
        body = _ship_notice_balanced.replace('CTT*3~', 'CTT*5~')
        message = parse_x12(_in_group('SH', '004010', body)).transaction_set

        issues = validate_snip_3(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('CTT01', issues[0])

    def test_snip_3_remittance_balanced(self) -> None:
        # The independent CLP04-minus-PLB computation matches what BPR02 declares ..
        recomputed_payment = _recompute_remittance_payment(_remittance_balanced)
        segments = _split_wire(_remittance_balanced)
        bpr_elements = _elements_of_first(segments, 'BPR')
        self.assertEqual(Decimal(bpr_elements[2]), recomputed_payment)

        # .. so the validator must agree the remittance reconciles.
        message = parse_x12(_in_group('HP', '005010X221A1', _remittance_balanced, isa=_isa_hipaa)).transaction_set
        self.assertEqual(validate_snip_3(message), [])

    def test_snip_3_remittance_unbalanced(self) -> None:
        # The independent CLP04-minus-PLB computation disagrees with what BPR02 declares ..
        recomputed_payment = _recompute_remittance_payment(_remittance_unbalanced)
        segments = _split_wire(_remittance_unbalanced)
        bpr_elements = _elements_of_first(segments, 'BPR')
        self.assertNotEqual(Decimal(bpr_elements[2]), recomputed_payment)

        # .. so the validator must flag exactly that disagreement.
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
