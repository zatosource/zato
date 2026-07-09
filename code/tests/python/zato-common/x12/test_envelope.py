# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.typing_ import cast_
from zato.x12.base import X12GenericMessage
from zato.x12.envelope import X12EnvelopeError, X12Interchange, parse_x12
from zato.x12.retail import Invoice810, PurchaseOrder850, ShipNotice856

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators.
_isa = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
       '*260709*1200*U*00401*000000905*0*P*>~'

# Two minimal invoices - four segments each, ST and SE included.
_invoice_one = 'ST*810*0001~BIG*20260715*INV-9981*20260709*PO-4529~TDS*24750~SE*4*0001~'
_invoice_two = 'ST*810*0002~BIG*20260716*INV-9982*20260709*PO-4530~TDS*10000~SE*4*0002~'

# A minimal purchase order - three segments, ST and SE included.
_order = 'ST*850*0001~BEG*00*SA*PO-4529**20260709~SE*3*0001~'

# One group with one invoice.
_interchange_single = _isa + \
    'GS*IN*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    _invoice_one + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

# One group with two invoices.
_interchange_multi_set = _isa + \
    'GS*IN*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    _invoice_one + \
    _invoice_two + \
    'GE*2*905~' + \
    'IEA*1*000000905~'

# Two groups - an invoice group next to a purchase order group.
_interchange_multi_group = _isa + \
    'GS*IN*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    _invoice_one + \
    'GE*1*905~' + \
    'GS*PO*SENDERGS*RECEIVERGS*20260709*1200*906*X*004010~' + \
    _order + \
    'GE*1*906~' + \
    'IEA*2*000000905~'

# An interchange-level TA1 acknowledgment between ISA and IEA, with no groups at all.
_interchange_ta1 = _isa + \
    'TA1*000000800*260708*0900*A*000~' + \
    'IEA*0*000000905~'

# A price catalog - a set type without a registered class.
_interchange_generic = _isa + \
    'GS*SC*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    'ST*832*0001~BCT*PC~SE*3*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

# Interchanges past this size must parse and round-trip - there is no size ceiling.
_min_large_size = 16 * 1024 * 1024

# ################################################################################################################################
# ################################################################################################################################

class TestParseX12(unittest.TestCase):

    maxDiff = None

    def test_parse_single_set(self) -> None:
        interchange = parse_x12(_interchange_single)

        self.assertEqual(interchange.isa.sender_id, 'SENDERID       ')
        self.assertEqual(interchange.isa.control_number, '000000905')
        self.assertEqual(interchange.iea.control_number, '000000905')

        self.assertEqual(len(interchange.groups), 1)

        group = interchange.groups[0]
        self.assertEqual(group.gs.functional_id_code, 'IN')
        self.assertEqual(group.gs.version, '004010')
        self.assertEqual(group.ge.transaction_set_count, '1')

        message = cast_('Invoice810', interchange.transaction_set)
        self.assertIsInstance(message, Invoice810)
        self.assertEqual(message.big.invoice_number, 'INV-9981')

    def test_parse_multi_set(self) -> None:
        interchange = parse_x12(_interchange_multi_set)

        group = interchange.groups[0]
        self.assertEqual(len(group.transaction_sets), 2)

        first_invoice = cast_('Invoice810', group.transaction_sets[0])
        second_invoice = cast_('Invoice810', group.transaction_sets[1])

        self.assertEqual(first_invoice.big.invoice_number, 'INV-9981')
        self.assertEqual(second_invoice.big.invoice_number, 'INV-9982')

        # With two sets present, the single-set property must refuse to pick one.
        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = interchange.transaction_set

        self.assertIn('Expected exactly 1 transaction set, found 2', str(ctx.exception))

    def test_parse_multi_group(self) -> None:
        interchange = parse_x12(_interchange_multi_group)

        self.assertEqual(len(interchange.groups), 2)
        self.assertEqual(interchange.groups[0].gs.functional_id_code, 'IN')
        self.assertEqual(interchange.groups[1].gs.functional_id_code, 'PO')

        self.assertIsInstance(interchange.groups[0].transaction_sets[0], Invoice810)
        self.assertIsInstance(interchange.groups[1].transaction_sets[0], PurchaseOrder850)

    def test_parse_ta1(self) -> None:
        interchange = parse_x12(_interchange_ta1)

        self.assertEqual(len(interchange.ta1_list), 1)
        self.assertEqual(interchange.ta1_list[0].control_number, '000000800')
        self.assertEqual(interchange.ta1_list[0].ack_code, 'A')

    def test_parse_unregistered_set_is_generic(self) -> None:
        interchange = parse_x12(_interchange_generic)

        message = interchange.transaction_set
        self.assertIs(type(message), X12GenericMessage)
        self.assertEqual(message.segments('BCT')[0].e_1, 'PC')

    def test_roundtrip_is_byte_exact(self) -> None:
        interchange = parse_x12(_interchange_multi_group)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _interchange_multi_group)

        # A second parse-serialize cycle is byte-stable.
        self.assertEqual(parse_x12(serialized).serialize(), serialized)

    def test_to_dict(self) -> None:
        interchange = parse_x12(_interchange_single)
        dict_data = interchange.to_dict()

        self.assertEqual(dict_data['isa']['control_number'], '000000905')
        self.assertEqual(len(dict_data['groups']), 1)
        self.assertEqual(dict_data['groups'][0]['gs']['functional_id_code'], 'IN')
        self.assertEqual(dict_data['iea']['group_count'], '1')

# ################################################################################################################################
# ################################################################################################################################

class TestEnvelopeValidation(unittest.TestCase):

    maxDiff = None

    def test_isa_iea_control_number_mismatch(self) -> None:
        raw = _interchange_single.replace('IEA*1*000000905~', 'IEA*1*000000906~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('does not match IEA02', str(ctx.exception))

    def test_iea_group_count_mismatch(self) -> None:
        raw = _interchange_single.replace('IEA*1*000000905~', 'IEA*2*000000905~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('does not match the group count', str(ctx.exception))

    def test_gs_ge_control_number_mismatch(self) -> None:
        raw = _interchange_single.replace('GE*1*905~', 'GE*1*906~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('does not match GE02', str(ctx.exception))

    def test_ge_set_count_mismatch(self) -> None:
        raw = _interchange_single.replace('GE*1*905~', 'GE*2*905~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('does not match the transaction set count', str(ctx.exception))

    def test_st_se_control_number_mismatch(self) -> None:
        raw = _interchange_single.replace('SE*4*0001~', 'SE*4*0002~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('does not match SE02', str(ctx.exception))

    def test_se_segment_count_mismatch(self) -> None:
        raw = _interchange_single.replace('SE*4*0001~', 'SE*5*0001~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('does not match the segment count', str(ctx.exception))

    def test_duplicate_set_control_number(self) -> None:
        raw = _interchange_multi_set.replace('ST*810*0002~', 'ST*810*0001~')
        raw = raw.replace('SE*4*0002~', 'SE*4*0001~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('Duplicate transaction set control number', str(ctx.exception))

    def test_duplicate_group_control_number(self) -> None:
        raw = _interchange_multi_group.replace('GS*PO*SENDERGS*RECEIVERGS*20260709*1200*906*X*004010~',
            'GS*PO*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~')
        raw = raw.replace('GE*1*906~', 'GE*1*905~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('Duplicate group control number', str(ctx.exception))

    def test_missing_iea(self) -> None:
        raw = _interchange_single.replace('IEA*1*000000905~', '')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('not closed with IEA', str(ctx.exception))

    def test_missing_ge(self) -> None:
        raw = _interchange_single.replace('GE*1*905~', '')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('not closed with GE', str(ctx.exception))

    def test_missing_se(self) -> None:
        raw = _interchange_single.replace('SE*4*0001~', '')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('not closed with SE', str(ctx.exception))

    def test_segment_outside_transaction_set(self) -> None:
        raw = _interchange_single.replace('IEA*1*000000905~', 'REF*ZZ*STRAY~IEA*1*000000905~')

        with self.assertRaises(X12EnvelopeError) as ctx:
            _ = parse_x12(raw)

        self.assertIn('found outside of a transaction set', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class TestBatchedConstruction(unittest.TestCase):

    maxDiff = None

    def test_many_sets_in_one_group(self) -> None:
        interchange = X12Interchange()
        interchange.isa.sender_id = 'SENDERID'
        interchange.isa.receiver_id = 'RECEIVERID'

        invoice_numbers = ['INV-9981', 'INV-9982', 'INV-9983']

        for invoice_number in invoice_numbers:
            invoice = Invoice810()
            invoice.big.invoice_date = '20260715'
            invoice.big.invoice_number = invoice_number
            interchange.add(invoice)

        # All three invoices file into one IN group.
        self.assertEqual(len(interchange.groups), 1)
        self.assertEqual(len(interchange.groups[0].transaction_sets), 3)

        serialized = interchange.serialize()
        parsed = parse_x12(serialized)

        # The control numbers and counts were computed from the actual structure.
        self.assertEqual(len(parsed.groups), 1)

        group = parsed.groups[0]
        self.assertEqual(group.gs.functional_id_code, 'IN')
        self.assertEqual(group.gs.version, '004010')
        self.assertEqual(group.ge.transaction_set_count, '3')

        control_numbers:'list[str]' = []
        parsed_numbers:'list[str]' = []

        for transaction_set in group.transaction_sets:
            invoice = cast_('Invoice810', transaction_set)
            control_numbers.append(invoice.st.control_number)
            parsed_numbers.append(invoice.big.invoice_number)

        self.assertEqual(control_numbers, ['0001', '0002', '0003'])
        self.assertEqual(parsed_numbers, invoice_numbers)

    def test_many_groups_in_one_interchange(self) -> None:
        interchange = X12Interchange()
        interchange.isa.sender_id = 'SENDERID'
        interchange.isa.receiver_id = 'RECEIVERID'

        order = PurchaseOrder850()
        order.beg.po_number = 'PO-4529'

        notice = ShipNotice856()
        notice.bsn.shipment_id = 'SHIP-88112'

        interchange.add(order)
        interchange.add(notice)

        # The 850 and the 856 land in separate groups by functional identifier.
        self.assertEqual(len(interchange.groups), 2)

        serialized = interchange.serialize()
        parsed = parse_x12(serialized)

        self.assertEqual(len(parsed.groups), 2)
        self.assertEqual(parsed.groups[0].gs.functional_id_code, 'PO')
        self.assertEqual(parsed.groups[1].gs.functional_id_code, 'SH')
        self.assertEqual(parsed.iea.group_count, '2')

        self.assertIsInstance(parsed.groups[0].transaction_sets[0], PurchaseOrder850)
        self.assertIsInstance(parsed.groups[1].transaction_sets[0], ShipNotice856)

    def test_unknown_set_type_is_rejected(self) -> None:
        interchange = X12Interchange()
        message = X12GenericMessage()

        with self.assertRaises(X12EnvelopeError) as ctx:
            interchange.add(message)

        self.assertIn('No functional identifier code found', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class TestLargeInterchange(unittest.TestCase):

    maxDiff = None

    def test_large_interchange_roundtrip(self) -> None:

        # Build a purchase order with a very long note loop ..
        segment_texts = [
            'ST*850*0001~',
            'BEG*00*SA*PO-4529**20260709~',
            'N9*L1*Marking Instructions~',
        ]

        for line_number in range(1, 150_001):
            segment_text = f'MSG*Marking instructions line {line_number} - ship all cartons ' + \
                'on one pallet and label each carton with the store number~'
            segment_texts.append(segment_text)

        # .. the SE counts every segment of the set, itself included ..
        segment_count = len(segment_texts) + 1
        segment_texts.append(f'SE*{segment_count}*0001~')

        body = ''.join(segment_texts)

        raw = _isa + \
            'GS*PO*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
            body + \
            'GE*1*905~' + \
            'IEA*1*000000905~'

        # .. prove the input is well past any size ceiling ..
        self.assertGreater(len(raw), _min_large_size)

        # .. and that it parses and round-trips byte-exact.
        interchange = parse_x12(raw)

        message = interchange.transaction_set
        self.assertIsInstance(message, PurchaseOrder850)
        self.assertEqual(len(message._raw_segments), segment_count)

        serialized = interchange.serialize()
        self.assertEqual(serialized.replace('\n', ''), raw)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
