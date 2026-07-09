# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
import unittest

# Zato
from zato.x12.base import X12Message
from zato.x12.control import ControlNumberStore
from zato.x12.envelope import parse_x12
from zato.x12.preflight import check_usage_indicator, gs1_check_digit, is_valid_gtin, is_valid_sscc, preflight_invoice, \
     preflight_purchase_order, preflight_ship_notice

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators - a production interchange.
_isa = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
       '*260709*1200*U*00401*000000905*0*P*>~'

# A valid SSCC-18 and a valid UPC-A - both with correct GS1 check digits.
_sscc = '000001234500000003'
_gtin = '036000291452'


def _in_group(functional_id:'str', body:'str') -> 'str':
    """ Wraps a transaction set body in a full interchange.
    """
    out = _isa + \
        f'GS*{functional_id}*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
        body + \
        'GE*1*905~' + \
        'IEA*1*000000905~'
    return out


def _ship_notice(hl_segments:'str', man_segments:'str', segment_count:'int') -> 'str':
    """ Builds an 856 body around the given HL tree and MAN marks.
    """
    out = 'ST*856*0001~' + \
        'BSN*00*SHIP-88112*20260710*0830~' + \
        hl_segments + \
        man_segments + \
        f'SE*{segment_count}*0001~'
    return out


# A coherent standard-pack tree - shipment, order, pack, item.
_tree_clean = 'HL*1**S~HL*2*1*O~HL*3*2*P~HL*4*3*I~'

# A coherent pick-and-pack tree - the item sits right under the order.
_tree_pick_and_pack = 'HL*1**S~HL*2*1*O~HL*3*2*I~'

# An 810 whose lines balance and whose product ids are valid.
_invoice_clean = 'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    f'IT1*1*10*EA*9.75*TE*UP*{_gtin}~' + \
    'TDS*9750~' + \
    'CTT*1~' + \
    'SE*6*0001~'

# An 850 ordering the same product in eaches.
_order_each = 'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    f'PO1*1*10*EA*9.75*TE*UP*{_gtin}~' + \
    'CTT*1~' + \
    'SE*5*0001~'

# The same 850 ordering in cases instead.
_order_case = 'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    f'PO1*1*10*CA*9.75*TE*UP*{_gtin}~' + \
    'CTT*1~' + \
    'SE*5*0001~'

# ################################################################################################################################
# ################################################################################################################################

class TestCheckDigits(unittest.TestCase):

    maxDiff = None

    def test_gs1_check_digit(self) -> None:
        # The canonical UPC-A example - 03600029145 carries the check digit 2
        self.assertEqual(gs1_check_digit('03600029145'), 2)

    def test_valid_gtin(self) -> None:
        self.assertTrue(is_valid_gtin(_gtin))

    def test_invalid_gtin_check_digit(self) -> None:
        self.assertFalse(is_valid_gtin('036000291453'))

    def test_invalid_gtin_length(self) -> None:
        self.assertFalse(is_valid_gtin('0360002914'))

    def test_invalid_gtin_characters(self) -> None:
        self.assertFalse(is_valid_gtin('03600029145X'))

    def test_valid_sscc(self) -> None:
        self.assertTrue(is_valid_sscc(_sscc))

    def test_invalid_sscc_check_digit(self) -> None:
        bad = _sscc[:-1] + '9'
        self.assertFalse(is_valid_sscc(bad))

    def test_invalid_sscc_length(self) -> None:
        self.assertFalse(is_valid_sscc('12345'))

# ################################################################################################################################
# ################################################################################################################################

class TestShipNoticePreflight(unittest.TestCase):

    maxDiff = None

    def _parse(self, body:'str') -> 'X12Message':
        out = parse_x12(_in_group('SH', body)).transaction_set
        return out

    def test_clean_standard_pack(self) -> None:
        body = _ship_notice(_tree_clean, f'MAN*GM*{_sscc}~', 8)
        message = self._parse(body)

        self.assertEqual(preflight_ship_notice(message), [])

    def test_clean_pick_and_pack(self) -> None:
        body = _ship_notice(_tree_pick_and_pack, '', 6)
        message = self._parse(body)

        self.assertEqual(preflight_ship_notice(message), [])

    def test_missing_parent(self) -> None:
        tree = 'HL*1**S~HL*2*1*O~HL*3*9*I~'
        body = _ship_notice(tree, '', 6)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('parent `9` which does not exist', issues[0])

    def test_two_roots(self) -> None:
        tree = 'HL*1**S~HL*2**S~'
        body = _ship_notice(tree, '', 5)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertIn('Expected exactly 1 top-level HL, found 2', issues[0])

    def test_root_is_not_shipment(self) -> None:
        tree = 'HL*1**O~HL*2*1*I~'
        body = _ship_notice(tree, '', 5)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('has level `O` instead of `S`', issues[0])

    def test_invalid_level_transition(self) -> None:
        # A pack directly under a shipment skips the order level
        tree = 'HL*1**S~HL*2*1*P~'
        body = _ship_notice(tree, '', 5)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('level `P` cannot be a child of level `S`', issues[0])

    def test_duplicate_hl_id(self) -> None:
        tree = 'HL*1**S~HL*1*1*O~'
        body = _ship_notice(tree, '', 5)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertIn('Duplicate HL01 id `1`', issues[0])

    def test_bad_sscc_check_digit(self) -> None:
        bad_sscc = _sscc[:-1] + '9'
        body = _ship_notice(_tree_clean, f'MAN*GM*{bad_sscc}~', 8)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('is not a valid SSCC-18', issues[0])

    def test_duplicate_sscc_within_notice(self) -> None:
        body = _ship_notice(_tree_clean, f'MAN*GM*{_sscc}~MAN*GM*{_sscc}~', 9)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('Duplicate SSCC', issues[0])

    def test_sscc_per_partner_uniqueness(self) -> None:
        body = _ship_notice(_tree_clean, f'MAN*GM*{_sscc}~', 8)

        with tempfile.TemporaryDirectory() as temp_dir:
            store = ControlNumberStore(os.path.join(temp_dir, 'control.db'))

            # The first notice registers the SSCC ..
            message = self._parse(body)
            issues = preflight_ship_notice(message, store, 'SENDERID', 'RECEIVERID')
            self.assertEqual(issues, [])

            # .. and a later notice reusing it is flagged.
            message = self._parse(body)
            issues = preflight_ship_notice(message, store, 'SENDERID', 'RECEIVERID')
            self.assertEqual(len(issues), 1)
            self.assertIn('already used with this partner', issues[0])

            store.close()

    def test_bad_gtin_on_lin(self) -> None:
        tree = _tree_clean + 'LIN**UP*036000291453~'
        body = _ship_notice(tree, '', 8)
        message = self._parse(body)

        issues = preflight_ship_notice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('is not a valid GTIN/UPC', issues[0])

# ################################################################################################################################
# ################################################################################################################################

class TestInvoicePreflight(unittest.TestCase):

    maxDiff = None

    def test_clean_invoice(self) -> None:
        message = parse_x12(_in_group('IN', _invoice_clean)).transaction_set
        self.assertEqual(preflight_invoice(message), [])

    def test_bad_gtin(self) -> None:
        body = _invoice_clean.replace(_gtin, '036000291453')
        message = parse_x12(_in_group('IN', body)).transaction_set

        issues = preflight_invoice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('is not a valid GTIN/UPC', issues[0])

    def test_unbalanced_total(self) -> None:
        body = _invoice_clean.replace('TDS*9750~', 'TDS*10000~')
        message = parse_x12(_in_group('IN', body)).transaction_set

        issues = preflight_invoice(message)
        self.assertEqual(len(issues), 1)
        self.assertIn('TDS01', issues[0])

    def test_uom_echo_matches(self) -> None:
        message = parse_x12(_in_group('IN', _invoice_clean)).transaction_set
        order = parse_x12(_in_group('PO', _order_each)).transaction_set

        self.assertEqual(preflight_invoice(message, order), [])

    def test_uom_echo_mismatch(self) -> None:
        message = parse_x12(_in_group('IN', _invoice_clean)).transaction_set
        order = parse_x12(_in_group('PO', _order_case)).transaction_set

        issues = preflight_invoice(message, order)
        self.assertEqual(len(issues), 1)
        self.assertIn('uses unit `EA` but the purchase order used `CA`', issues[0])

    def test_duplicate_invoice_number(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ControlNumberStore(os.path.join(temp_dir, 'control.db'))

            # The first invoice registers its number ..
            message = parse_x12(_in_group('IN', _invoice_clean)).transaction_set
            issues = preflight_invoice(message, store=store, sender='SENDERID', receiver='RECEIVERID')
            self.assertEqual(issues, [])

            # .. and sending the same number again is flagged.
            message = parse_x12(_in_group('IN', _invoice_clean)).transaction_set
            issues = preflight_invoice(message, store=store, sender='SENDERID', receiver='RECEIVERID')
            self.assertEqual(len(issues), 1)
            self.assertIn('Invoice number `INV-9981` was already used', issues[0])

            store.close()

# ################################################################################################################################
# ################################################################################################################################

class TestPurchaseOrderPreflight(unittest.TestCase):

    maxDiff = None

    def test_clean_order(self) -> None:
        message = parse_x12(_in_group('PO', _order_each)).transaction_set
        self.assertEqual(preflight_purchase_order(message), [])

    def test_bad_gtin_and_count(self) -> None:
        body = _order_each.replace(_gtin, '036000291453').replace('CTT*1~', 'CTT*2~')
        message = parse_x12(_in_group('PO', body)).transaction_set

        issues = preflight_purchase_order(message)
        self.assertEqual(len(issues), 2)
        self.assertIn('is not a valid GTIN/UPC', issues[0])
        self.assertIn('CTT01', issues[1])

# ################################################################################################################################
# ################################################################################################################################

class TestUsageIndicatorGuard(unittest.TestCase):

    maxDiff = None

    def test_production_document_on_production_endpoint(self) -> None:
        interchange = parse_x12(_in_group('IN', _invoice_clean))
        self.assertEqual(check_usage_indicator(interchange, 'P'), [])

    def test_production_document_on_test_endpoint(self) -> None:
        interchange = parse_x12(_in_group('IN', _invoice_clean))

        issues = check_usage_indicator(interchange, 'T')
        self.assertEqual(len(issues), 1)
        self.assertIn('ISA15 is `P` but this endpoint expects `T`', issues[0])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
