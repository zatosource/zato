# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The join point of the EDI codecs and the AS2 transport - a typed purchase order
# built with the X12 dictionaries travels through the full send and handle pipeline,
# the receiver parses it back typed, builds the functional acknowledgment and returns
# it over AS2, and the original sender reconciles it against the audit log.
# The same loop then runs with an EDIFACT interchange and its CONTRL.

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# httpx
import httpx

# Zato
from zato.common.as2.inbound import handle
from zato.common.as2.outbound import send
from zato.common.as2.partnership import new_partnership
from zato.common.typing_ import any_, anylist
from zato.common.util.api import utcnow
from zato.common.util.xml_.keystore import Keystore
from zato.edi.reconcile import Reconciler
from zato.edifact.contrl import build_contrl, parse_contrl
from zato.edifact.envelope import parse_edifact
from zato.x12.ack import build_997, parse_997
from zato.x12.envelope import parse_x12, X12Interchange
from zato.x12.retail import PurchaseOrder850
from zato.x12.retail.messages import PurchaseOrderLine

# ################################################################################################################################
# ################################################################################################################################

_endpoint_url = 'https://partnercorp.example.com/as2'

# The AS2 identities of the two parties.
_buyer_identifier    = 'ZatoRetail'
_supplier_identifier = 'PartnerCorp'

# The EDI identities of the same two parties.
_buyer_edi_id    = 'ZATORETAIL'
_supplier_edi_id = 'PARTNERCORP'

# The interchange control number of the outbound 850 and its unpadded 997 echo.
_x12_control_number = '000000905'
_x12_group_control_number = '905'

# An EDIFACT purchase order interchange with its control reference.
_edifact_control_reference = 'REF001'

_edifact_interchange = "UNB+UNOA:2+ZATORETAIL+PARTNERCORP+260709:1200+REF001'" + \
    "UNH+1+ORDERS:D:96A:UN'" + \
    "BGM+220+PO-4529'" + \
    "UNT+3+1'" + \
    "UNZ+1+REF001'"

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _Exchange:
    """ One simulated wire between an AS2 sender and an AS2 receiver - the receiver
    runs the real inbound pipeline behind an HTTP mock transport.
    """
    sender_partnership: 'any_'
    receiver_partnerships: 'anylist'
    sender_keystore: 'Keystore'
    receiver_keystore: 'Keystore'

    # Everything the receiver decided about what arrived.
    results: 'anylist'

    client: 'httpx.Client'

# ################################################################################################################################

def _new_exchange(
    from_identifier:'str',
    to_identifier:'str',
    sender_keystore:'Keystore',
    receiver_keystore:'Keystore',
    ) -> '_Exchange':
    """ Wires an AS2 sender and receiver together over a mock HTTP transport,
    with the given identities and keystores - so the same helper serves
    both the document leg and the acknowledgment leg going the other way.
    """

    out = _Exchange()

    sender_partnership = new_partnership()
    sender_partnership.as2_from = from_identifier
    sender_partnership.as2_to = to_identifier
    sender_partnership.endpoint_url = _endpoint_url

    # The receiving side keeps the same relationship with the identities swapped.
    receiver_partnership = new_partnership()
    receiver_partnership.as2_from = to_identifier
    receiver_partnership.as2_to = from_identifier

    out.sender_partnership = sender_partnership
    out.receiver_partnerships = [receiver_partnership]
    out.sender_keystore = sender_keystore
    out.receiver_keystore = receiver_keystore

    out.results = []

    def _is_duplicate(as2_from:'str', as2_to:'str', message_id:'str') -> 'None':
        return None

    def _handler(request:'httpx.Request') -> 'httpx.Response':

        body = request.read()

        result = handle(body, dict(request.headers), out.receiver_partnerships, out.receiver_keystore, _is_duplicate)
        out.results.append(result)

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)
    out.client = httpx.Client(transport=transport)

    return out

# ################################################################################################################################

def _send(exchange:'_Exchange', payload:'bytes', filename:'str') -> 'any_':
    """ Delivers one payload through the exchange's mock wire.
    """
    out = send(
        exchange.sender_partnership,
        exchange.sender_keystore,
        payload,
        filename,
        exchange.client,
    )

    return out

# ################################################################################################################################

def _received_payload(exchange:'_Exchange') -> 'str':
    """ Returns the single document the exchange's receiver delivered, as text.
    """
    inbound = exchange.results[0]

    assert not inbound.is_error
    assert len(inbound.payloads) == 1

    data = inbound.payloads[0].data

    out = data.decode('utf-8')
    return out

# ################################################################################################################################

def _build_purchase_order_interchange() -> 'X12Interchange':
    """ Builds a typed 850 with the retail dictionary, enveloped so that the group
    control number is the unpadded echo of the interchange control number -
    the shape a 997's AK1 reconciles against.
    """
    order:'any_' = PurchaseOrder850()
    order.beg.purpose_code = '00'
    order.beg.po_type = 'NE'
    order.beg.po_number = 'PO-4529'
    order.beg.date = '20260709'

    line = PurchaseOrderLine()
    line.po1.line_number = '1'
    line.po1.quantity = '10'
    line.po1.unit = 'EA'
    line.po1.unit_price = '9.75'
    order.lines = [line]

    out = X12Interchange()
    out.isa.sender_id = _buyer_edi_id
    out.isa.receiver_id = _supplier_edi_id
    out.isa.control_number = _x12_control_number

    out.add(order)
    out.groups[0].gs.control_number = _x12_group_control_number

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestX12OverAS2:
    """ A typed 850 out, the 997 back, both legs over the full AS2 pipeline,
    with the audit log reconciling the acknowledgment.
    """

    def test_purchase_order_and_997_reconcile(self, parties:'any_') -> 'None':
        reconciler = Reconciler('test-server')

        # The buyer builds a typed 850 with the dictionaries ..
        interchange = _build_purchase_order_interchange()
        payload = interchange.serialize().encode('utf-8')

        # .. records the interchange as awaiting its acknowledgment ..
        reconciler.record_interchange_sent(_buyer_edi_id, _supplier_edi_id, _x12_control_number, document_type='850')

        # .. and delivers it over AS2, signed and encrypted, with the sync MDN reconciling.
        document_leg = _new_exchange(_buyer_identifier, _supplier_identifier, parties.sender, parties.receiver)

        send_result = _send(document_leg, payload, 'orders-850.edi')
        assert send_result.is_ok

        # The supplier received the exact bytes and parses them back typed ..
        received_text = _received_payload(document_leg)
        assert received_text.encode('utf-8') == payload

        received_interchange = parse_x12(received_text)
        received_order = received_interchange.transaction_set

        assert isinstance(received_order, PurchaseOrder850)
        assert received_order.beg.po_number == 'PO-4529'

        # .. the 850 is still outstanding on the buyer's side ..
        cutoff = utcnow() + timedelta(seconds=1)
        outstanding = reconciler.outstanding(cutoff)

        assert len(outstanding) == 1
        assert outstanding[0].control_number == _x12_group_control_number

        # .. the supplier builds the 997 and returns it over AS2 the other way ..
        acknowledgment = build_997(received_interchange)
        acknowledgment_payload = acknowledgment.serialize().encode('utf-8')

        acknowledgment_leg = _new_exchange(_supplier_identifier, _buyer_identifier, parties.receiver, parties.sender)

        acknowledgment_send_result = _send(acknowledgment_leg, acknowledgment_payload, 'orders-997.edi')
        assert acknowledgment_send_result.is_ok

        # .. the buyer parses the 997 and sees its 850 accepted ..
        acknowledgment_text = _received_payload(acknowledgment_leg)
        acknowledgment_interchange = parse_x12(acknowledgment_text)
        acknowledgment_result = parse_997(acknowledgment_interchange)

        assert acknowledgment_result.is_accepted
        assert acknowledgment_result.set_results[0].identifier_code == '850'
        assert acknowledgment_result.set_results[0].is_accepted

        # .. and reconciling it leaves nothing outstanding.
        reconciler.record_ack_received(_buyer_edi_id, _supplier_edi_id, acknowledgment_result.group_control_number)

        assert reconciler.outstanding(cutoff) == []

# ################################################################################################################################
# ################################################################################################################################

class TestEDIFACTOverAS2:
    """ The same loop with an EDIFACT interchange - the ORDERS out, the CONTRL back,
    both legs over the full AS2 pipeline, reconciled through the audit log.
    """

    def test_orders_and_contrl_reconcile(self, parties:'any_') -> 'None':
        reconciler = Reconciler('test-server')

        payload = _edifact_interchange.encode('utf-8')

        # The buyer records the interchange as awaiting its acknowledgment ..
        reconciler.record_interchange_sent(_buyer_edi_id, _supplier_edi_id, _edifact_control_reference)

        # .. and delivers it over AS2.
        document_leg = _new_exchange(_buyer_identifier, _supplier_identifier, parties.sender, parties.receiver)

        send_result = _send(document_leg, payload, 'orders.edi')
        assert send_result.is_ok

        # The supplier received the exact bytes and parses the interchange ..
        received_text = _received_payload(document_leg)
        assert received_text.encode('utf-8') == payload

        received_interchange = parse_edifact(received_text)
        assert received_interchange.header.control_reference == _edifact_control_reference

        # .. the interchange is still outstanding on the buyer's side ..
        cutoff = utcnow() + timedelta(seconds=1)
        outstanding = reconciler.outstanding(cutoff)

        assert len(outstanding) == 1
        assert outstanding[0].control_number == _edifact_control_reference

        # .. the supplier builds the CONTRL and returns it over AS2 the other way ..
        acknowledgment = build_contrl(received_interchange)
        acknowledgment_payload = acknowledgment.serialize().encode('utf-8')

        acknowledgment_leg = _new_exchange(_supplier_identifier, _buyer_identifier, parties.receiver, parties.sender)

        acknowledgment_send_result = _send(acknowledgment_leg, acknowledgment_payload, 'orders-contrl.edi')
        assert acknowledgment_send_result.is_ok

        # .. the buyer parses the CONTRL and sees its interchange acknowledged ..
        acknowledgment_text = _received_payload(acknowledgment_leg)
        acknowledgment_interchange = parse_edifact(acknowledgment_text)
        acknowledgment_result = parse_contrl(acknowledgment_interchange)

        assert acknowledgment_result.is_accepted
        assert acknowledgment_result.interchange_reference == _edifact_control_reference
        assert acknowledgment_result.message_results[0].is_accepted

        # .. and reconciling it leaves nothing outstanding.
        reconciler.record_ack_received(_buyer_edi_id, _supplier_edi_id, acknowledgment_result.interchange_reference)

        assert reconciler.outstanding(cutoff) == []

# ################################################################################################################################
# ################################################################################################################################
