# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.x12.render import extract_x12, render_document

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators.
_isa_retail = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
              '*260709*1200*U*00401*000000905*0*P*>~'

# A version 00501 healthcare envelope with the colon component separator the guides use.
_isa_hipaa = 'ISA*00*          *00*          *ZZ*SUBMITTERID    *ZZ*PAYERID        ' + \
             '*260709*1200*^*00501*000000101*1*P*:~'

_purchase_order_850 = _isa_retail + \
    'GS*PO*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    'CUR*BY*USD~' + \
    'REF*DP*038~' + \
    'DTM*002*20260801~' + \
    'N9*L1*Marking Instructions~' + \
    'MSG*Ship all cartons on one pallet~' + \
    'N1*BY*Acme Retail Corp*92*0042~' + \
    'N3*100 Main Street~' + \
    'N4*Columbus*OH*43215*US~' + \
    'PO1*1*10*EA*9.75*TE*UP*012345678905*VP*ACME-100~' + \
    'PID*F****Blue ceramic mug 350 ml~' + \
    'PO1*2*5*CA*30.00*TE*UP*012345678912*VP*ACME-200~' + \
    'PID*F****Green ceramic bowl~' + \
    'CTT*2~' + \
    'SE*16*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

_ship_notice_856 = _isa_retail + \
    'GS*SH*SENDERGS*RECEIVERGS*20260710*0830*905*X*004010~' + \
    'ST*856*0001~' + \
    'BSN*00*SHIP-88112*20260710*0830~' + \
    'HL*1**S~' + \
    'TD1*CTN25*8~' + \
    'REF*BM*BOL-556677~' + \
    'N1*ST*Acme DC East*92*0871~' + \
    'HL*2*1*O~' + \
    'PRF*PO-4529***20260709~' + \
    'HL*3*2*P~' + \
    'MAN*GM*00000123450000000018~' + \
    'HL*4*3*I~' + \
    'LIN**UP*012345678905~' + \
    'SN1**10*EA~' + \
    'CTT*4~' + \
    'SE*15*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

_claim_837p = _isa_hipaa + \
    'GS*HC*SUBMITTERGS*PAYERGS*20260709*1200*101*X*005010X222A1~' + \
    'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'NM1*41*2*Sunrise Medical Billing*****46*123456789~' + \
    'HL*1**20*1~' + \
    'NM1*85*2*Sunrise Family Practice*****XX*1234567893~' + \
    'N3*200 Care Lane~' + \
    'N4*Denver*CO*80202~' + \
    'HL*2*1*22*0~' + \
    'SBR*P*18*GRP-7789******CI~' + \
    'NM1*IL*1*Doe*John****MI*MEMBER123~' + \
    'CLM*PATIENT-001*150***11:B:1*Y*A*Y*Y~' + \
    'HI*ABK:J039~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1***1~' + \
    'DTP*472*D8*20260701~' + \
    'SE*16*0001~' + \
    'GE*1*101~' + \
    'IEA*1*000000101~'

# A transaction set no dictionary declares - an 864 text message.
_text_message_864 = _isa_retail + \
    'GS*TX*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    'ST*864*0001~' + \
    'MIT*REF-1*Carrier strike notice~' + \
    'MSG*All shipments are delayed by two days~' + \
    'SE*4*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

# ################################################################################################################################
# ################################################################################################################################

def _line_indexes(rendered:'str', line:'str') -> 'list[int]':
    """ Returns the indexes of every occurrence of the given exact line.
    """
    out:'list[int]' = []

    for index, rendered_line in enumerate(rendered.splitlines()):
        if rendered_line == line:
            out.append(index)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExtractX12(unittest.TestCase):

    maxDiff = None

    def test_extract_plain(self) -> 'None':

        # A payload that is exactly one interchange comes back as-is.
        out = extract_x12(_purchase_order_850)
        self.assertEqual(out, _purchase_order_850)

# ################################################################################################################################

    def test_extract_embedded(self) -> 'None':

        # The interchange is lifted out of the surrounding MIME content.
        text = 'Content-Type: application/edi-x12\r\nContent-Disposition: attachment\r\n\r\n' + \
            _purchase_order_850 + '\r\n--as2-boundary--\r\n'

        out = extract_x12(text)
        self.assertEqual(out, _purchase_order_850)

# ################################################################################################################################

    def test_extract_none_without_interchange(self) -> 'None':
        out = extract_x12('{"mic": "T3JkZXJzTUlDVmFsdWU=, sha-256"}')
        self.assertEqual(out, '')

# ################################################################################################################################

    def test_extract_none_with_malformed_isa(self) -> 'None':

        # The tag alone is not an interchange - the fixed-width layout must hold.
        out = extract_x12('ISA is the tag every interchange starts with')
        self.assertEqual(out, '')

# ################################################################################################################################

    def test_extract_none_without_trailer(self) -> 'None':

        # An interchange cut off before its IEA has no complete document to extract.
        truncated = _purchase_order_850.split('IEA')[0]

        out = extract_x12(truncated)
        self.assertEqual(out, '')

# ################################################################################################################################
# ################################################################################################################################

class TestRenderTypedSet(unittest.TestCase):

    maxDiff = None

    def test_envelope_element_names(self) -> 'None':
        rendered = render_document(_purchase_order_850)

        self.assertIn('ISA - Interchange control header', rendered)
        self.assertIn('    sender_id: SENDERID', rendered)
        self.assertIn('    receiver_id: RECEIVERID', rendered)
        self.assertIn('    control_number: 000000905', rendered)

        self.assertIn('GS - Functional group header', rendered)
        self.assertIn('    functional_id_code: PO', rendered)
        self.assertIn('    version: 004010', rendered)

        self.assertIn('IEA - Interchange control trailer', rendered)
        self.assertIn('    group_count: 1', rendered)

# ################################################################################################################################

    def test_segment_element_names(self) -> 'None':
        rendered = render_document(_purchase_order_850)

        # Message-level segments sit at the leftmost level, with their dictionary names ..
        self.assertIn('\nBEG - Beginning segment for purchase order\n', rendered)
        self.assertIn('    purpose_code: 00', rendered)
        self.assertIn('    po_number: PO-4529', rendered)

        self.assertIn('\nCUR - Currency\n', rendered)
        self.assertIn('    currency_code: USD', rendered)

        # .. and the transaction set header is named too.
        self.assertIn('\nST - Transaction set header\n', rendered)
        self.assertIn('    identifier_code: 850', rendered)

# ################################################################################################################################

    def test_empty_elements_are_skipped(self) -> 'None':
        rendered = render_document(_purchase_order_850)

        # BEG04 is empty on the wire, so its release_number never shows.
        self.assertNotIn('release_number', rendered)

        # The padded ISA authorization information is whitespace only.
        self.assertNotIn('auth_information', rendered)

# ################################################################################################################################

    def test_loops_are_indented(self) -> 'None':
        rendered = render_document(_purchase_order_850)

        # The loop segments sit one level deeper than the message-level segments ..
        self.assertIn('\n    N9 - Reference identification - the leader of the note loop\n', rendered)
        self.assertIn('\n    MSG - Message text\n', rendered)
        self.assertIn('\n    N1 - Name - the leader of the party identification loop\n', rendered)
        self.assertIn('\n    N3 - Address information\n', rendered)

        # .. both PO1 lines start their own loop instances at the same depth ..
        po1_lines = _line_indexes(rendered, '    PO1 - Baseline item data - the leader of the purchase order line loop')
        self.assertEqual(len(po1_lines), 2)

        pid_lines = _line_indexes(rendered, '    PID - Product/item description')
        self.assertEqual(len(pid_lines), 2)

        # .. their elements one level deeper still ..
        self.assertIn('\n        quantity: 10\n', rendered)
        self.assertIn('\n        description: Blue ceramic mug 350 ml\n', rendered)

        # .. and the summary area returns to the leftmost level.
        self.assertIn('\nCTT - Transaction totals\n', rendered)
        self.assertIn('\nSE - Transaction set trailer\n', rendered)

# ################################################################################################################################
# ################################################################################################################################

class TestRenderHierarchy(unittest.TestCase):

    maxDiff = None

    def test_hl_loops_are_indented_by_tree_depth(self) -> 'None':
        rendered = render_document(_ship_notice_856)

        # The header area sits at the leftmost level ..
        self.assertIn('\nBSN - Beginning segment for ship notice\n', rendered)

        # .. the shipment level opens the tree ..
        self.assertIn('\n    HL - Hierarchical level - the segment whose parent pointers build the 856 tree\n', rendered)
        self.assertIn('\n        level_code: S\n', rendered)
        self.assertIn('\n    TD1 - Carrier details - quantity and weight\n', rendered)

        # .. the order level sits below the shipment ..
        self.assertIn('\n            level_code: O\n', rendered)
        self.assertIn('\n        PRF - Purchase order reference\n', rendered)

        # .. the pack below the order ..
        self.assertIn('\n                level_code: P\n', rendered)
        self.assertIn('\n            MAN - Marks and numbers - carries the SSCC-18 of a pack in an 856\n', rendered)

        # .. and the item below the pack.
        self.assertIn('\n                    level_code: I\n', rendered)
        self.assertIn('\n                LIN - Item identification\n', rendered)
        self.assertIn('\n                SN1 - Item detail - shipment\n', rendered)

        # The summary area returns to the leftmost level.
        self.assertIn('\nCTT - Transaction totals\n', rendered)

# ################################################################################################################################

    def test_group_loops_nest_inside_hl_loops(self) -> 'None':
        rendered = render_document(_ship_notice_856)

        # The party loop of the shipment level sits one level below its HL segments.
        self.assertIn('\n        N1 - Name - the leader of the party identification loop\n', rendered)
        self.assertIn('\n            name: Acme DC East\n', rendered)

# ################################################################################################################################
# ################################################################################################################################

class TestRenderComposite(unittest.TestCase):

    maxDiff = None

    def test_composite_components_have_their_own_names(self) -> 'None':
        rendered = render_document(_claim_837p)

        # The HI diagnosis code is a composite - each component shows with its own name.
        self.assertIn('code_1:', rendered)
        self.assertIn('qualifier: ABK', rendered)
        self.assertIn('code: J039', rendered)

        # So is the CLM facility code, e.g. 11:B:1 for an office place of service.
        self.assertIn('facility:', rendered)
        self.assertIn('place_of_service: 11', rendered)
        self.assertIn('frequency: 1', rendered)

# ################################################################################################################################

    def test_claim_loops_nest_inside_the_subscriber_level(self) -> 'None':
        rendered = render_document(_claim_837p)

        # The subscriber HL loop sits below the billing provider one ..
        self.assertIn('\n        SBR - Subscriber information\n', rendered)

        # .. the claim loop opens inside the subscriber level ..
        self.assertIn('\n            CLM - Claim information - the leader of the 2300 claim loop\n', rendered)

        # .. and the service line loop nests inside the claim.
        self.assertIn('\n                LX - Transaction set line number - the leader of the 2400 service line loop\n', rendered)

# ################################################################################################################################
# ################################################################################################################################

class TestRenderGenericSet(unittest.TestCase):

    maxDiff = None

    def test_generic_set_keeps_positional_names(self) -> 'None':
        rendered = render_document(_text_message_864)

        # A set without a dictionary shows its elements positionally ..
        self.assertIn('\nMIT\n', rendered)
        self.assertIn('    e_1: REF-1', rendered)
        self.assertIn('    e_2: Carrier strike notice', rendered)

        self.assertIn('\nMSG\n', rendered)
        self.assertIn('    e_1: All shipments are delayed by two days', rendered)

        # .. while the envelope classes still name the set header and trailer.
        self.assertIn('\nST - Transaction set header\n', rendered)
        self.assertIn('    identifier_code: 864', rendered)
        self.assertIn('\nSE - Transaction set trailer\n', rendered)

# ################################################################################################################################
# ################################################################################################################################

class TestRenderDocumentBoundary(unittest.TestCase):

    maxDiff = None

    def test_no_document_renders_nothing(self) -> 'None':
        self.assertEqual(render_document(''), '')
        self.assertEqual(render_document('{"disposition": "processed"}'), '')

# ################################################################################################################################

    def test_unparseable_document_renders_nothing(self) -> 'None':

        # The envelope numbers must agree - a wrong segment count means no parsed view.
        broken = _purchase_order_850.replace('SE*16*0001~', 'SE*99*0001~')

        out = render_document(broken)
        self.assertEqual(out, '')

# ################################################################################################################################

    def test_document_embedded_in_mime_renders(self) -> 'None':
        text = 'Content-Type: application/edi-x12\r\n\r\n' + _purchase_order_850 + '\r\n--as2-boundary--\r\n'

        rendered = render_document(text)

        self.assertIn('    po_number: PO-4529', rendered)
        self.assertIn('    sender_id: SENDERID', rendered)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
