# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.api import IMAPMessage
from zato.common.ext.bunch import Bunch
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.typing_ import cast_
from zato.common.util.xml_.message import parse as parse_xml_message
from zato.edifact import EDIEnvelopeError, wire_text_from

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# A minimal interchange with one ORDERS message.
_interchange = "UNB+UNOA:2+SENDER1+RECIPIENT1+260709:1200+REF001'" + \
    "UNH+1+ORDERS:D:96A:UN'" + \
    "BGM+220+PO-1'" + \
    "UNT+3+1'" + \
    "UNZ+1+REF001'"

# The same interchange as a mailbox delivers it, without the UNB-UNZ envelope.
_bare_message = "UNH+1+ORDERS:D:96A:UN'" + \
    "BGM+220+PO-1'" + \
    "UNT+3+1'"

# ################################################################################################################################
# ################################################################################################################################

def _imap_message(plain_parts:'strlist') -> 'IMAPMessage':
    data = Bunch()
    data.body = {'plain': plain_parts, 'html': []}

    out = IMAPMessage('1001', cast_('any_', None), data)
    return out

# ################################################################################################################################

def _file_transfer_item(conn_type:'str', data:'bytes') -> 'FileTransferItem':
    out = FileTransferItem(
        conn_type,
        'Lab results',
        'Every hour',
        '/inbound',
        'orders.edi',
        '/inbound/orders.edi',
        len(data),
        '2026-07-09T12:00:00',
        data,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestWireTextFrom(unittest.TestCase):

    maxDiff = None

# ################################################################################################################################

    def test_imap(self) -> None:
        message = _imap_message([_bare_message])

        text = wire_text_from(message, message)

        self.assertEqual(text, _bare_message)

# ################################################################################################################################

    def test_imap_no_plain_part(self) -> None:
        message = _imap_message([])

        with self.assertRaises(EDIEnvelopeError) as ctx:
            _ = wire_text_from(message, message)

        self.assertIn('No plain-text part', str(ctx.exception))

# ################################################################################################################################

    def test_file_transfer_sftp(self) -> None:
        item = _file_transfer_item('sftp', _interchange.encode('ascii'))

        text = wire_text_from(item, item)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_file_transfer_smb(self) -> None:
        item = _file_transfer_item('smb', _interchange.encode('ascii'))

        text = wire_text_from(item, item)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_rest_str(self) -> None:
        text = wire_text_from(_interchange, _interchange)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_rest_bytes(self) -> None:
        data = _interchange.encode('ascii')

        text = wire_text_from(data, data)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_soap_operation_text(self) -> None:
        envelope = f'<ReceiveInterchange xmlns="urn:example:edi">{_interchange}</ReceiveInterchange>'
        envelope_bytes = envelope.encode('utf-8')
        payload = parse_xml_message(envelope_bytes)

        text = wire_text_from(envelope, payload)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_soap_child_element(self) -> None:
        envelope = '<ReceiveInterchange xmlns="urn:example:edi">' + \
            f'<interchange>{_interchange}</interchange>' + \
            '</ReceiveInterchange>'
        envelope_bytes = envelope.encode('utf-8')
        payload = parse_xml_message(envelope_bytes)

        text = wire_text_from(envelope, payload)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_soap_no_text(self) -> None:
        envelope = '<ReceiveInterchange xmlns="urn:example:edi">' + \
            '<sender>SENDER1</sender>' + \
            '<recipient>RECIPIENT1</recipient>' + \
            '</ReceiveInterchange>'
        envelope_bytes = envelope.encode('utf-8')
        payload = parse_xml_message(envelope_bytes)

        with self.assertRaises(EDIEnvelopeError) as ctx:
            _ = wire_text_from(envelope, payload)

        self.assertIn('found 2', str(ctx.exception))

# ################################################################################################################################

    def test_mllp_bytes(self) -> None:
        data = _interchange.encode('ascii')

        text = wire_text_from(data, data)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_amqp_bytes(self) -> None:
        data = _interchange.encode('ascii')

        text = wire_text_from(data, data)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_kafka_str(self) -> None:
        text = wire_text_from(_interchange, _interchange)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_ibm_mq_str(self) -> None:
        text = wire_text_from(_interchange, _interchange)

        self.assertEqual(text, _interchange)

# ################################################################################################################################

    def test_unsupported_type(self) -> None:
        payload = {'order_id': 'PO-1'}

        with self.assertRaises(EDIEnvelopeError) as ctx:
            _ = wire_text_from(payload, payload)

        self.assertIn('`dict`', str(ctx.exception))

# ################################################################################################################################

    def test_bytes_unoc_latin1(self) -> None:
        interchange = _interchange.replace('UNOA:2', 'UNOC:3').replace('PO-1', 'PO-é')
        data = interchange.encode('iso-8859-1')

        text = wire_text_from(data, data)

        self.assertEqual(text, interchange)

# ################################################################################################################################

    def test_bytes_unoy_utf8(self) -> None:
        interchange = _interchange.replace('UNOA:2', 'UNOY:4').replace('PO-1', 'PO-é')
        data = interchange.encode('utf-8')

        text = wire_text_from(data, data)

        self.assertEqual(text, interchange)

# ################################################################################################################################

    def test_bytes_bare_unh_default_encoding(self) -> None:
        message = _bare_message.replace('PO-1', 'PO-é')
        data = message.encode('iso-8859-1')

        text = wire_text_from(data, data)

        self.assertEqual(text, message)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
