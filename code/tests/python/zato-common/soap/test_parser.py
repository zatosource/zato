# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import NamedTemporaryFile

# pytest
import pytest

# Zato
from zato.common.soap.envelope import parse_envelope
from zato.common.soap.security.saml import add_assertion
from zato.common.util.xml_.core import parse_xml, XMLException
from zato.common.util.xml_.message import parse as parse_xml_message
from zato.common.util.xml_.tokens import add_saml_token

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The contents of the file the documents below name in an entity declaration. The test writes its own
# file rather than naming one belonging to the host it happens to run on.
_external_file_marker = 'zato-external-file-contents'

# An address nothing listens on. A parse that reached out to it would block or raise a connection
# error rather than the exception these tests assert on.
_unreachable_url = 'http://127.0.0.1:1/declared-external.dtd'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def external_file():
    """ A file on disk with a known marker in it, named by the entity declarations below.
    """
    with NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
        _ = f.write(_external_file_marker)
        path = f.name

    yield path

    os.unlink(path)

# ################################################################################################################################
# ################################################################################################################################

def _envelope_with_doctype(doctype:'str', body:'str'='<op/>') -> 'bytes':
    """ Builds a well-formed SOAP 1.2 envelope carrying the doctype given.
    """
    out = f"""<?xml version="1.0"?>
{doctype}
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Body>{body}</soap:Body>
</soap:Envelope>"""

    return out.encode('utf8')

# ################################################################################################################################

def _nested_entity_expansion() -> 'bytes':
    """ Nine levels of tenfold entity expansion - one reference to the outermost entity names a
    billion copies of a three-character string.
    """
    entities = ['<!ENTITY level "abc">']

    for level in range(1, 10):
        inner = 'level' if level == 1 else f'level{level - 1}'
        references = f'&{inner};' * 10
        entities.append(f'<!ENTITY level{level} "{references}">')

    declarations = '\n '.join(entities)
    doctype = f'<!DOCTYPE root [\n {declarations}\n]>'

    out = _envelope_with_doctype(doctype, '<op><data>&level9;</data></op>')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDocumentTypeDeclarations:
    """ Both SOAP 1.1 and SOAP 1.2 forbid a document type declaration in a message, so parse_xml
    refuses one whatever it declares.
    """

    def test_internal_dtd_is_refused(self):
        data = _envelope_with_doctype('<!DOCTYPE soap:Envelope [ <!ELEMENT op EMPTY> ]>')

        with pytest.raises(XMLException) as e:
            _ = parse_xml(data)

        assert 'Document type declarations are not allowed' in str(e.value)

    def test_external_dtd_is_refused(self):
        data = _envelope_with_doctype(f'<!DOCTYPE soap:Envelope SYSTEM "{_unreachable_url}">')

        with pytest.raises(XMLException):
            _ = parse_xml(data)

    def test_a_document_without_one_is_accepted(self):
        data = _envelope_with_doctype('')

        root = parse_xml(data)
        assert root.tag == '{http://www.w3.org/2003/05/soap-envelope}Envelope'

    def test_malformed_xml_raises_our_own_exception(self):
        # The bytes come off the wire, so a caller has one exception type to handle rather than
        # lxml's leaking through whatever it happens to be.
        with pytest.raises(XMLException) as e:
            _ = parse_xml(b'<soap:Envelope><unclosed>')

        assert 'Malformed XML' in str(e.value)

# ################################################################################################################################
# ################################################################################################################################

class TestExternalEntities:
    """ Entity declarations naming a file or a URL, in the forms the parse rules cover.
    """

    def test_a_file_entity_does_not_read_the_filesystem(self, external_file:'any_'):
        doctype = f'<!DOCTYPE root [ <!ENTITY declared SYSTEM "file://{external_file}"> ]>'
        data = _envelope_with_doctype(doctype, '<op><data>&declared;</data></op>')

        with pytest.raises(XMLException):
            _ = parse_xml(data)

        # The marker is in the file the declaration names, never in the document itself.
        assert _external_file_marker not in data.decode('utf8')

    def test_an_http_entity_does_not_reach_the_network(self):
        doctype = f'<!DOCTYPE root [ <!ENTITY declared SYSTEM "{_unreachable_url}"> ]>'
        data = _envelope_with_doctype(doctype, '<op><data>&declared;</data></op>')

        with pytest.raises(XMLException) as e:
            _ = parse_xml(data)

        assert 'Document type declarations are not allowed' in str(e.value)

    def test_a_parameter_entity_is_refused(self):
        # A parameter entity is declared and referenced inside the DTD itself rather than in content,
        # which is a separate case from the general entities above.
        doctype = f'<!DOCTYPE root [ <!ENTITY % declared SYSTEM "{_unreachable_url}"> %declared; ]>'
        data = _envelope_with_doctype(doctype)

        with pytest.raises(XMLException):
            _ = parse_xml(data)

# ################################################################################################################################
# ################################################################################################################################

class TestEntityExpansion:
    """ Entities declared and referenced entirely within the document, naming no external resource.
    """

    def test_nested_expansion_is_refused(self):
        data = _nested_entity_expansion()

        # Small enough that a body-size cap would let it through, which is the point of it.
        assert len(data) < 2048

        with pytest.raises(XMLException):
            _ = parse_xml(data)

    def test_nested_expansion_is_refused_by_the_parse_itself(self):
        # The doctype rule runs after the parse, so the message states that the parse itself declined
        # the expansion rather than the check that follows it.
        data = _nested_entity_expansion()

        with pytest.raises(XMLException) as e:
            _ = parse_xml(data)

        assert 'Malformed XML' in str(e.value)

# ################################################################################################################################
# ################################################################################################################################

class TestEveryParsePath:
    """ Every entry point that takes XML as bytes, each checked separately, so that they are all
    confirmed to go through parse_xml rather than a parser of their own.
    """

    def test_parse_envelope(self, external_file:'any_'):
        doctype = f'<!DOCTYPE root [ <!ENTITY declared SYSTEM "file://{external_file}"> ]>'
        data = _envelope_with_doctype(doctype, '<op><data>&declared;</data></op>')

        with pytest.raises(XMLException):
            _ = parse_envelope(data)

    def test_parse_message(self, external_file:'any_'):
        doctype = f'<!DOCTYPE root [ <!ENTITY declared SYSTEM "file://{external_file}"> ]>'
        data = f'<?xml version="1.0"?>\n{doctype}\n<op><data>&declared;</data></op>'.encode('utf8')

        with pytest.raises(XMLException):
            _ = parse_xml_message(data)

    def test_saml_assertion_bytes(self):
        # An assertion arrives as bytes issued by an external identity provider, so it is parsed
        # the same way an envelope is.
        envelope = parse_envelope(_envelope_with_doctype(''))
        doctype = f'<!DOCTYPE root [ <!ENTITY declared SYSTEM "{_unreachable_url}"> ]>'
        assertion = _envelope_with_doctype(doctype)

        with pytest.raises(XMLException):
            add_assertion(envelope, assertion)

    def test_saml_token_bytes(self):
        envelope = parse_envelope(_envelope_with_doctype(''))
        doctype = f'<!DOCTYPE root [ <!ENTITY declared SYSTEM "{_unreachable_url}"> ]>'
        assertion = _envelope_with_doctype(doctype)

        with pytest.raises(XMLException):
            _ = add_saml_token(envelope, assertion)

    def test_nested_expansion_reaches_every_path(self):
        data = _nested_entity_expansion()

        with pytest.raises(XMLException):
            _ = parse_envelope(data)

        with pytest.raises(XMLException):
            _ = parse_xml_message(data)

# ################################################################################################################################
# ################################################################################################################################
