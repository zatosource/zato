# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.typing_ import cast_
from zato.x12.envelope import parse_x12
from zato.x12.retail import Invoice810, PurchaseOrder850, PurchaseOrderAcknowledgment855, ShipNotice856

# ################################################################################################################################
# ################################################################################################################################

# A version 00401 retail envelope with the customary separators.
_isa = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
       '*260709*1200*U*00401*000000905*0*P*>~'

_purchase_order_850 = _isa + \
    'GS*PO*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    'ST*850*0001~' + \
    'BEG*00*SA*PO-4529**20260709~' + \
    'CUR*BY*USD~' + \
    'REF*DP*038~' + \
    'PER*BD*Jane Smith*TE*555-0100~' + \
    'FOB*CC~' + \
    'ITD*01*3*2**30**31~' + \
    'DTM*002*20260801~' + \
    'N9*L1*Marking Instructions~' + \
    'MSG*Ship all cartons on one pallet~' + \
    'N1*BY*Acme Retail Corp*92*0042~' + \
    'N2*Purchasing Department~' + \
    'N3*100 Main Street~' + \
    'N4*Columbus*OH*43215*US~' + \
    'N1*ST*Acme DC East*92*0871~' + \
    'N3*55 Distribution Way~' + \
    'N4*Newark*NJ*07105*US~' + \
    'PO1*1*10*EA*9.75*TE*UP*012345678905*VP*ACME-100~' + \
    'PID*F****Blue ceramic mug 350 ml~' + \
    'PO1*2*5*CA*30.00*TE*UP*012345678912*VP*ACME-200~' + \
    'PID*F****Green ceramic bowl~' + \
    'CTT*2~' + \
    'SE*23*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

_acknowledgment_855 = _isa + \
    'GS*PR*SENDERGS*RECEIVERGS*20260709*1200*905*X*004010~' + \
    'ST*855*0001~' + \
    'BAK*00*AD*PO-4529*20260709~' + \
    'PO1*1*10*EA*9.75*TE*UP*012345678905~' + \
    'ACK*IA*10*EA~' + \
    'PO1*2*5*CA*30.00*TE*UP*012345678912~' + \
    'ACK*IR*0*CA~' + \
    'CTT*2~' + \
    'SE*8*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

_ship_notice_856 = _isa + \
    'GS*SH*SENDERGS*RECEIVERGS*20260710*0830*905*X*004010~' + \
    'ST*856*0001~' + \
    'BSN*00*SHIP-88112*20260710*0830~' + \
    'HL*1**S~' + \
    'TD1*CTN25*8~' + \
    'TD5*B*2*UPSN*M~' + \
    'REF*BM*BOL-556677~' + \
    'N1*SH*Acme Supplier~' + \
    'N1*ST*Acme DC East*92*0871~' + \
    'HL*2*1*O~' + \
    'PRF*PO-4529***20260709~' + \
    'HL*3*2*P~' + \
    'MAN*GM*00000123450000000018~' + \
    'HL*4*3*I~' + \
    'LIN**UP*012345678905~' + \
    'SN1**10*EA~' + \
    'HL*5*3*I~' + \
    'LIN**UP*012345678912~' + \
    'SN1**5*CA~' + \
    'CTT*5~' + \
    'SE*20*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

_invoice_810 = _isa + \
    'GS*IN*SENDERGS*RECEIVERGS*20260715*1200*905*X*004010~' + \
    'ST*810*0001~' + \
    'BIG*20260715*INV-9981*20260709*PO-4529~' + \
    'REF*DP*038~' + \
    'N1*BY*Acme Retail Corp*92*0042~' + \
    'N1*RI*Acme Supplier*92*7714~' + \
    'ITD*01*3*2**30**31~' + \
    'DTM*011*20260714~' + \
    'IT1*1*10*EA*9.75*TE*UP*012345678905~' + \
    'PID*F****Blue ceramic mug 350 ml~' + \
    'IT1*2*5*CA*30.00*TE*UP*012345678912~' + \
    'PID*F****Green ceramic bowl~' + \
    'TDS*24750~' + \
    'TXI*ST*12.38~' + \
    'ISS*15*CA~' + \
    'CTT*2~' + \
    'SE*16*0001~' + \
    'GE*1*905~' + \
    'IEA*1*000000905~'

# ################################################################################################################################
# ################################################################################################################################

class TestPurchaseOrder850(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('PurchaseOrder850', parse_x12(_purchase_order_850).transaction_set)
        self.assertIsInstance(message, PurchaseOrder850)

        self.assertEqual(message.beg.po_number, 'PO-4529')
        self.assertEqual(message.beg.date, '20260709')
        self.assertEqual(message.currency.currency_code, 'USD')
        self.assertEqual(message.contacts[0].name, 'Jane Smith')
        self.assertEqual(message.fob.payment_method, 'CC')
        self.assertEqual(message.terms.discount_days, '30')
        self.assertEqual(message.terms.net_days, '31')
        self.assertEqual(message.dates[0].qualifier, '002')

        # The N9 note loop carries its free-form message text.
        self.assertEqual(message.notes[0].n9.value, 'Marking Instructions')
        self.assertEqual(message.notes[0].messages[0].text, 'Ship all cartons on one pallet')

        # The N1 loops with the BY and ST qualifiers.
        self.assertEqual(len(message.parties), 2)
        self.assertEqual(message.parties[0].n1.entity_code, 'BY')
        self.assertEqual(message.parties[0].n1.name, 'Acme Retail Corp')
        self.assertEqual(message.parties[0].additional_name.name, 'Purchasing Department')
        self.assertEqual(message.parties[0].location.city, 'Columbus')
        self.assertEqual(message.parties[1].n1.entity_code, 'ST')
        self.assertEqual(message.parties[1].address[0].address, '55 Distribution Way')

        # The PO1 loops with their product id qualifier pairs and descriptions.
        self.assertEqual(len(message.lines), 2)
        self.assertEqual(message.lines[0].po1.quantity, '10')
        self.assertEqual(message.lines[0].po1.id_qualifier_1, 'UP')
        self.assertEqual(message.lines[0].po1.product_id_1, '012345678905')
        self.assertEqual(message.lines[0].po1.id_qualifier_2, 'VP')
        self.assertEqual(message.lines[0].po1.product_id_2, 'ACME-100')
        self.assertEqual(message.lines[0].descriptions[0].description, 'Blue ceramic mug 350 ml')
        self.assertEqual(message.lines[1].descriptions[0].description, 'Green ceramic bowl')

        self.assertEqual(message.ctt.line_count, '2')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_purchase_order_850)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _purchase_order_850)

# ################################################################################################################################
# ################################################################################################################################

class TestAcknowledgment855(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('PurchaseOrderAcknowledgment855', parse_x12(_acknowledgment_855).transaction_set)
        self.assertIsInstance(message, PurchaseOrderAcknowledgment855)

        self.assertEqual(message.bak.ack_type, 'AD')
        self.assertEqual(message.bak.po_number, 'PO-4529')

        # Each PO1 loop carries its ACK line-status segments.
        self.assertEqual(len(message.lines), 2)
        self.assertEqual(message.lines[0].acknowledgments[0].line_status, 'IA')
        self.assertEqual(message.lines[0].acknowledgments[0].quantity, '10')
        self.assertEqual(message.lines[1].acknowledgments[0].line_status, 'IR')
        self.assertEqual(message.lines[1].acknowledgments[0].quantity, '0')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_acknowledgment_855)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _acknowledgment_855)

# ################################################################################################################################
# ################################################################################################################################

class TestShipNotice856(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('ShipNotice856', parse_x12(_ship_notice_856).transaction_set)
        self.assertIsInstance(message, ShipNotice856)

        self.assertEqual(message.bsn.shipment_id, 'SHIP-88112')
        self.assertEqual(message.ctt.line_count, '5')

# ################################################################################################################################

    def test_hierarchy(self) -> 'None':
        message = parse_x12(_ship_notice_856).transaction_set

        # The HL parent pointers resolve into the shipment/order/pack/item tree.
        roots = message.hierarchy
        self.assertEqual(len(roots), 1)

        shipment = roots[0]
        self.assertEqual(shipment.level_code, 'S')
        self.assertEqual(shipment.segments('TD1')[0].e_1, 'CTN25')
        self.assertEqual(shipment.segments('REF')[0].e_2, 'BOL-556677')

        self.assertEqual(len(shipment.children), 1)
        order = shipment.children[0]
        self.assertEqual(order.level_code, 'O')
        self.assertEqual(order.segments('PRF')[0].e_1, 'PO-4529')

        self.assertEqual(len(order.children), 1)
        pack = order.children[0]
        self.assertEqual(pack.level_code, 'P')

        # The pack carries its SSCC-18 in the MAN segment.
        self.assertEqual(pack.segments('MAN')[0].e_2, '00000123450000000018')

        self.assertEqual(len(pack.children), 2)
        first_item = pack.children[0]
        second_item = pack.children[1]

        self.assertEqual(first_item.level_code, 'I')
        self.assertEqual(first_item.segments('LIN')[0].e_3, '012345678905')
        self.assertEqual(first_item.segments('SN1')[0].e_2, '10')
        self.assertEqual(second_item.segments('LIN')[0].e_3, '012345678912')
        self.assertEqual(second_item.segments('SN1')[0].e_3, 'CA')

        # The set trailer area belongs to no loop.
        self.assertEqual(second_item.segments('CTT'), [])
        self.assertEqual(second_item.segments('SE'), [])

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_ship_notice_856)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _ship_notice_856)

# ################################################################################################################################
# ################################################################################################################################

class TestInvoice810(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('Invoice810', parse_x12(_invoice_810).transaction_set)
        self.assertIsInstance(message, Invoice810)

        self.assertEqual(message.big.invoice_number, 'INV-9981')
        self.assertEqual(message.big.po_number, 'PO-4529')
        self.assertEqual(message.references[0].value, '038')

        self.assertEqual(len(message.parties), 2)
        self.assertEqual(message.parties[1].n1.entity_code, 'RI')
        self.assertEqual(message.parties[1].n1.name, 'Acme Supplier')

        self.assertEqual(len(message.lines), 2)
        self.assertEqual(message.lines[0].it1.unit_price, '9.75')
        self.assertEqual(message.lines[0].descriptions[0].description, 'Blue ceramic mug 350 ml')
        self.assertEqual(message.lines[1].it1.product_id_1, '012345678912')

        self.assertEqual(message.total.total_amount, '24750')
        self.assertEqual(message.taxes[0].amount, '12.38')
        self.assertEqual(message.shipment.quantity, '15')
        self.assertEqual(message.ctt.line_count, '2')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_invoice_810)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _invoice_810)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
