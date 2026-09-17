# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import IMAPMessage
from zato.common.ext.bunch import Bunch
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.typing_ import cast_
from zato.common.util.xml_.message import parse as parse_xml_message
from zato.edifact import EDIInterchange
from zato.edifact.nl.messages import MEDLAB
from zato.server.service.reqresp import Request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# A minimal interchange with one ORDERS message.
_interchange = "UNB+UNOA:2+SENDER1+RECIPIENT1+260709:1200+REF001'" + \
    "UNH+1+ORDERS:D:96A:UN'" + \
    "BGM+220+PO-1'" + \
    "UNT+3+1'" + \
    "UNZ+1+REF001'"

# A MEDLAB report with one specimen and two determinations, as a mailbox delivers it.
_medlab = "UNH+3001+MEDLAB:1'\n" + \
    "ZKH+Riverside Laboratory+Main Street:12::Springfield:62701+?+15551234567'\n" + \
    "PID+1980:05:21+M+Smith:::::J.++PAT100200'\n" + \
    "AFD+Clinical chemistry'\n" + \
    "ARA+Dr. Anna Miller'\n" + \
    "DET+26:07:09+09:30'\n" + \
    "IDE+C+26070001+blood'\n" + \
    "SEC+HAEMATOLOGY'\n" + \
    "BEP+1+Haemoglobin+8.6++mmol/l+N+8.5+11.0'\n" + \
    "BEP+1+Leukocytes+12.4++10*9/l+H+4.0+10.0'\n" + \
    "UNT+11+3001'"

# ################################################################################################################################
# ################################################################################################################################

def _request(raw:'any_', payload:'any_') -> 'Request':
    out = Request(MagicMock())
    out.raw = raw
    out.payload = payload

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRequestEdifact(TestCase):

    maxDiff = None

# ################################################################################################################################

    def test_imap(self) -> None:
        data = Bunch()
        data.body = {'plain': [_interchange], 'html': []}
        message = IMAPMessage('1001', cast_('any_', None), data)

        request = _request(message, message)
        interchange = request.edifact

        self.assertIsInstance(interchange, EDIInterchange)
        self.assertEqual(interchange.header.sender.identification, 'SENDER1')

# ################################################################################################################################

    def test_file_transfer(self) -> None:
        data = _interchange.encode('ascii')
        item = FileTransferItem(
            'sftp',
            'Lab results',
            'Every hour',
            '/inbound',
            'orders.edi',
            '/inbound/orders.edi',
            len(data),
            '2026-07-09T12:00:00',
            data,
        )

        request = _request(item, item)
        interchange = request.edifact

        self.assertIsInstance(interchange, EDIInterchange)
        self.assertEqual(interchange.header.recipient.identification, 'RECIPIENT1')

# ################################################################################################################################

    def test_rest_str(self) -> None:
        request = _request(_interchange, _interchange)
        interchange = request.edifact

        self.assertIsInstance(interchange, EDIInterchange)
        self.assertEqual(len(interchange.messages), 1)

# ################################################################################################################################

    def test_rest_bytes(self) -> None:
        data = _interchange.encode('ascii')

        request = _request(data, data)
        interchange = request.edifact

        self.assertIsInstance(interchange, EDIInterchange)
        self.assertEqual(interchange.trailer.control_reference, 'REF001')

# ################################################################################################################################

    def test_soap_uses_payload_not_raw(self) -> None:
        envelope = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>' + \
            f'<ReceiveInterchange xmlns="urn:example:edi">{_interchange}</ReceiveInterchange>' + \
            '</soap:Body></soap:Envelope>'
        operation = f'<ReceiveInterchange xmlns="urn:example:edi">{_interchange}</ReceiveInterchange>'
        operation_bytes = operation.encode('utf-8')
        payload = parse_xml_message(operation_bytes)

        request = _request(envelope, payload)
        interchange = request.edifact

        self.assertIsInstance(interchange, EDIInterchange)
        self.assertEqual(interchange.header.sender.identification, 'SENDER1')

# ################################################################################################################################

    def test_cached(self) -> None:
        request = _request(_interchange, _interchange)

        first = request.edifact
        second = request.edifact

        self.assertIs(first, second)

# ################################################################################################################################

    def test_typed_medlab(self) -> None:
        request = _request(_medlab, _medlab)
        report = cast_(MEDLAB, request.edifact.message)

        self.assertIsInstance(report, MEDLAB)
        self.assertEqual(report.pid.receiver_reference, 'PAT100200')
        self.assertEqual(report.pid.sex, 'M')

        materials = list(report.materials)
        self.assertEqual(len(materials), 1)

        determinations = list(materials[0].determinations)
        self.assertEqual(len(determinations), 2)
        self.assertEqual(determinations[1].normality_indicator, 'H')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
