# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.as4.common import AS4ProtocolException, EbMSError
from zato.common.as4.inbound import handle
from zato.common.as4.profiles import new_edelivery1_pmode
from zato.common.as4.sbdh import parse_sbdh
from zato.common.util.xml_.keystore import new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The contents of the file that the documents below name in an entity declaration.
External_Text = 'as4-external-file-contents'

# One entity referencing the next, each ten times over, so three levels turn ten bytes into ten thousand.
_nested_entity_declarations = (
    b'<!ENTITY level_one "aaaaaaaaaa">'
    b'<!ENTITY level_two "&level_one;&level_one;&level_one;&level_one;&level_one;'
    b'&level_one;&level_one;&level_one;&level_one;&level_one;">'
    b'<!ENTITY level_three "&level_two;&level_two;&level_two;&level_two;&level_two;'
    b'&level_two;&level_two;&level_two;&level_two;&level_two;">'
)

_expanded_marker = b'a' * 1000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def external_file(tmp_path:'any_') -> 'str':
    """ A file on disk that the documents below name in an entity declaration.
    """
    path = tmp_path / 'as4-external-file.txt'
    _ = path.write_text(External_Text)

    out = str(path)
    return out

# ################################################################################################################################

def _envelope_with_doctype(declarations:'bytes', body:'bytes') -> 'bytes':
    """ Builds a SOAP envelope carrying an inline DTD.
    """
    out = (
        b'<?xml version="1.0"?>'
        b'<!DOCTYPE s12:Envelope [' + declarations + b']>'
        b'<s12:Envelope xmlns:s12="http://www.w3.org/2003/05/soap-envelope">'
        b'<s12:Header/><s12:Body>' + body + b'</s12:Body>'
        b'</s12:Envelope>'
    )

    return out

# ################################################################################################################################

def _standard_business_document(doctype:'str', receiver_id:'str') -> 'bytes':
    """ Builds a StandardBusinessDocument with the doctype and receiver id given.
    """
    out = (
        '<?xml version="1.0"?>'
        f'{doctype}'
        '<sbdh:StandardBusinessDocument'
        ' xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader">'
        '<sbdh:StandardBusinessDocumentHeader>'
        '<sbdh:Sender><sbdh:Identifier Authority="iso6523-actorid-upis">0192:111</sbdh:Identifier></sbdh:Sender>'
        f'<sbdh:Receiver><sbdh:Identifier Authority="iso6523-actorid-upis">{receiver_id}</sbdh:Identifier></sbdh:Receiver>'
        '<sbdh:DocumentIdentification><sbdh:InstanceIdentifier>instance-01</sbdh:InstanceIdentifier>'
        '</sbdh:DocumentIdentification>'
        '</sbdh:StandardBusinessDocumentHeader>'
        '<Invoice xmlns="urn:test"/>'
        '</sbdh:StandardBusinessDocument>'
    ).encode('utf8')

    return out

# ################################################################################################################################

def _handle(body:'bytes') -> 'any_':
    """ Runs one envelope through the inbound pipeline with a minimal configuration.
    """
    pmode = new_edelivery1_pmode()

    out = handle(body, 'application/soap+xml', [pmode], new_keystore())
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInboundXMLParsing:
    """ What the inbound pipeline accepts from a document, which is the same set of parse rules
    the whole SOAP family follows.
    """

    def test_nested_entities_are_not_expanded(self) -> 'None':
        body = _envelope_with_doctype(_nested_entity_declarations, b'&level_three;')

        result = _handle(body)

        assert result.is_error
        assert result.error_code == EbMSError.Invalid_Header

        # No expanded text reaches the response.
        assert _expanded_marker not in result.body

# ################################################################################################################################

    def test_external_entities_are_not_resolved(self, external_file:'str') -> 'None':
        declarations = f'<!ENTITY declared SYSTEM "file://{external_file}">'.encode('utf8')
        body = _envelope_with_doctype(declarations, b'&declared;')

        result = _handle(body)

        assert result.is_error
        assert External_Text.encode('utf8') not in result.body

# ################################################################################################################################

    def test_envelope_without_a_messaging_header_is_refused(self) -> 'None':
        result = _handle(b'<not-an-envelope/>')

        assert result.is_error
        assert result.error_code == EbMSError.Invalid_Header

# ################################################################################################################################
# ################################################################################################################################

class TestSBDHParsing:
    """ The same parse rules apply to a Peppol payload as to the envelope that carried it.
    """

    def test_a_document_naming_an_external_entity_is_refused(self, external_file:'str') -> 'None':
        doctype = f'<!DOCTYPE sbdh:StandardBusinessDocument [<!ENTITY declared SYSTEM "file://{external_file}">]>'
        document = _standard_business_document(doctype, '&declared;')

        with pytest.raises(AS4ProtocolException) as raised:
            _ = parse_sbdh(document)

        assert raised.value.error_code == EbMSError.Value_Not_Recognized

# ################################################################################################################################

    def test_the_same_document_without_a_doctype_parses(self) -> 'None':

        # The counterpart to the test above, which would otherwise pass on any document at all.
        document = _standard_business_document('', '0192:222')

        details, _ = parse_sbdh(document)

        assert details.sender_id == '0192:111'
        assert details.receiver_id == '0192:222'

# ################################################################################################################################

    def test_nested_entities_are_not_expanded(self) -> 'None':
        document = (
            b'<?xml version="1.0"?>'
            b'<!DOCTYPE sbdh:StandardBusinessDocument [' + _nested_entity_declarations + b']>'
            b'<sbdh:StandardBusinessDocument'
            b' xmlns:sbdh="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader">'
            b'<sbdh:StandardBusinessDocumentHeader>&level_three;</sbdh:StandardBusinessDocumentHeader>'
            b'</sbdh:StandardBusinessDocument>'
        )

        with pytest.raises(AS4ProtocolException) as raised:
            _ = parse_sbdh(document)

        assert raised.value.error_code == EbMSError.Value_Not_Recognized

# ################################################################################################################################
# ################################################################################################################################

class TestExternalFileFixture:

    def test_the_named_file_really_exists(self, external_file:'str') -> 'None':
        """ The counterpart to the two tests that name this file.
        """
        assert os.path.exists(external_file)

        with open(external_file) as file_:
            contents = file_.read()

        assert contents == External_Text

# ################################################################################################################################
# ################################################################################################################################
