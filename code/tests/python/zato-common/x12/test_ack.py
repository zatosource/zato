# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.x12.ack import Ack_Accepted, Ack_Partial, Ack_Rejected, X12AckError, build_997, build_999, build_ta1, parse_997, \
     parse_999, parse_ta1
from zato.x12.envelope import parse_x12
from zato.x12.validation import Element_Mandatory_Missing, Segment_Unrecognized

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators.
_isa = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
       '*260709*1200*U*00401*000000905*0*P*>~'

# A version 00501 healthcare envelope with the colon component separator the guides use.
_isa_hipaa = 'ISA*00*          *00*          *ZZ*SUBMITTERID    *ZZ*PAYERID        ' + \
             '*260709*1200*^*00501*000000101*1*P*:~'

# A clean 810.
_invoice_clean = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'TDS*9750~' + \
    'CTT*1~' + \
    'SE*6*0001~'

# An 810 with an unknown segment and a BIG without its mandatory invoice number.
_invoice_bad = 'ST*810*0002~' + \
    'BIG*20260715~' + \
    'ZZZ*1~' + \
    'IT1*1*10*EA*9.75*TE*UP*036000291452~' + \
    'TDS*9750~' + \
    'CTT*1~' + \
    'SE*7*0002~'

# One clean invoice in one group.
_interchange_clean = _isa + \
    'GS*IN*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    _invoice_clean + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

# A clean invoice next to a bad one.
_interchange_mixed = _isa + \
    'GS*IN*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    _invoice_clean + \
    _invoice_bad + \
    'GE*2*905~' + \
    'IEA*1*000000905~'

# A clean 837P claim.
_claim_clean = 'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'CLM*PATIENT-001*150~' + \
    'HI*ABK:J039~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1~' + \
    'SE*7*0001~'

# The same claim with an unknown segment inside.
_claim_bad = 'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'CLM*PATIENT-001*150~' + \
    'ZZZ*1~' + \
    'HI*ABK:J039~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1~' + \
    'SE*8*0001~'


def _in_hipaa_group(body:'str') -> 'str':
    """ Wraps an 837 body in a full healthcare interchange.
    """
    out = _isa_hipaa + \
        'GS*HC*SUBMITTERGS*PAYERGS*20260709*1200*101*X*005010X222A1~' + \
        body + \
        'GE*1*101~' + \
        'IEA*1*000000101~'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTA1(unittest.TestCase):

    maxDiff = None

    def test_build_and_parse(self) -> None:
        interchange = parse_x12(_interchange_clean)

        ack = build_ta1(interchange)
        serialized = ack.serialize()

        # A TA1 travels without any GS/GE wrapping
        self.assertNotIn('GS*', serialized)

        reparsed = parse_x12(serialized)

        # The envelope is addressed back at the sender
        self.assertEqual(reparsed.isa.sender_id, 'RECEIVERID     ')
        self.assertEqual(reparsed.isa.receiver_id, 'SENDERID       ')

        result = parse_ta1(reparsed)

        self.assertEqual(result.control_number, '000000905')
        self.assertEqual(result.date, '260709')
        self.assertEqual(result.time, '1200')
        self.assertEqual(result.ack_code, Ack_Accepted)
        self.assertEqual(result.note_code, '000')
        self.assertTrue(result.is_accepted)

    def test_rejection_code(self) -> None:
        interchange = parse_x12(_interchange_clean)

        ack = build_ta1(interchange, ack_code=Ack_Rejected, note_code='001')
        result = parse_ta1(parse_x12(ack.serialize()))

        self.assertEqual(result.ack_code, Ack_Rejected)
        self.assertEqual(result.note_code, '001')
        self.assertFalse(result.is_accepted)

    def test_no_ta1_found(self) -> None:
        interchange = parse_x12(_interchange_clean)

        with self.assertRaises(X12AckError) as ctx:
            _ = parse_ta1(interchange)

        self.assertIn('No TA1 found', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class Test997(unittest.TestCase):

    maxDiff = None

    def test_accepted(self) -> None:
        interchange = parse_x12(_interchange_clean)

        ack = build_997(interchange)
        serialized = ack.serialize()

        reparsed = parse_x12(serialized)

        # The acknowledgment travels in an FA group echoing the acknowledged version
        group = reparsed.groups[0]
        self.assertEqual(group.gs.functional_id_code, 'FA')
        self.assertEqual(group.gs.version, '004010')

        result = parse_997(reparsed)

        self.assertEqual(result.functional_id_code, 'IN')
        self.assertEqual(result.group_control_number, '905')
        self.assertEqual(result.ack_code, Ack_Accepted)
        self.assertEqual(result.included_count, 1)
        self.assertEqual(result.received_count, 1)
        self.assertEqual(result.accepted_count, 1)
        self.assertTrue(result.is_accepted)

        set_result = result.set_results[0]
        self.assertEqual(set_result.identifier_code, '810')
        self.assertEqual(set_result.control_number, '0001')
        self.assertEqual(set_result.ack_code, Ack_Accepted)
        self.assertEqual(set_result.segment_notes, [])

    def test_rejected_set_never_produces_a_clean_997(self) -> None:
        interchange = parse_x12(_interchange_mixed)

        ack = build_997(interchange)
        result = parse_997(parse_x12(ack.serialize()))

        # One of the two sets was bad, so the group outcome is partial
        self.assertEqual(result.ack_code, Ack_Partial)
        self.assertEqual(result.included_count, 2)
        self.assertEqual(result.received_count, 2)
        self.assertEqual(result.accepted_count, 1)
        self.assertFalse(result.is_accepted)

        clean_result = result.set_results[0]
        self.assertEqual(clean_result.control_number, '0001')
        self.assertEqual(clean_result.ack_code, Ack_Accepted)

        bad_result = result.set_results[1]
        self.assertEqual(bad_result.control_number, '0002')
        self.assertEqual(bad_result.ack_code, Ack_Rejected)
        self.assertEqual(bad_result.error_codes, ['5'])

        # The AK3/AK4 detail names the exact problems
        self.assertEqual(len(bad_result.segment_notes), 2)

        big_note = bad_result.segment_notes[0]
        self.assertEqual(big_note.segment_id, 'BIG')
        self.assertEqual(big_note.position, 2)

        element_note = big_note.element_notes[0]
        self.assertEqual(element_note.element_position, 2)
        self.assertEqual(element_note.error_code, Element_Mandatory_Missing)

        unknown_note = bad_result.segment_notes[1]
        self.assertEqual(unknown_note.segment_id, 'ZZZ')
        self.assertEqual(unknown_note.position, 3)
        self.assertEqual(unknown_note.error_code, Segment_Unrecognized)

    def test_all_sets_rejected(self) -> None:
        raw = _isa + \
            'GS*IN*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
            _invoice_bad + \
            'GE*1*905~' + \
            'IEA*1*000000905~'

        interchange = parse_x12(raw)

        ack = build_997(interchange)
        result = parse_997(parse_x12(ack.serialize()))

        self.assertEqual(result.ack_code, Ack_Rejected)
        self.assertEqual(result.accepted_count, 0)

    def test_no_997_found(self) -> None:
        interchange = parse_x12(_interchange_clean)

        with self.assertRaises(X12AckError) as ctx:
            _ = parse_997(interchange)

        self.assertIn('Expected exactly 1 `997`', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class Test999(unittest.TestCase):

    maxDiff = None

    def test_accepted(self) -> None:
        interchange = parse_x12(_in_hipaa_group(_claim_clean))

        ack = build_999(interchange)
        serialized = ack.serialize()

        # The 999 declares its own implementation convention reference
        self.assertIn('ST*999*0001*005010X231A1', serialized)

        reparsed = parse_x12(serialized)
        result = parse_999(reparsed)

        self.assertEqual(result.functional_id_code, 'HC')
        self.assertEqual(result.ack_code, Ack_Accepted)
        self.assertTrue(result.set_results[0].is_accepted)

    def test_rejected_with_context(self) -> None:
        interchange = parse_x12(_in_hipaa_group(_claim_bad))

        ack = build_999(interchange)
        serialized = ack.serialize()

        # The CTX carries the business-unit reference of the rejected claim
        self.assertIn('CTX*CLM01:PATIENT-001', serialized)

        result = parse_999(parse_x12(serialized))

        self.assertEqual(result.ack_code, Ack_Rejected)
        self.assertEqual(result.accepted_count, 0)

        set_result = result.set_results[0]
        self.assertEqual(set_result.identifier_code, '837')
        self.assertEqual(set_result.ack_code, Ack_Rejected)

        note = set_result.segment_notes[0]
        self.assertEqual(note.segment_id, 'ZZZ')
        self.assertEqual(note.position, 4)
        self.assertEqual(note.error_code, Segment_Unrecognized)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
