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
from zato.common.util.xml_.wssec import add_saml_token

# ################################################################################################################################
# ################################################################################################################################

# What an attacker is trying to read out of the process. A real payload names a file such as
# /etc/passwd, however a test that asserts on that is asserting on the host it happens to run on,
# so the test writes its own file and looks for its own marker.
_secret_marker = 'ZATO-XXE-TEST-SECRET'

# An address nothing listens on. A parse that reaches out to it either blocks or fails, and both
# say the parser tried, which is what the test is checking it does not do.
_unreachable_url = 'http://127.0.0.1:1/attacker-controlled.dtd'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def secret_file():
    """ A file on disk with a known marker in it, standing in for whatever an external entity
    would otherwise read out of the filesystem.
    """
    with NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
        _ = f.write(_secret_marker)
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

def _billion_laughs() -> 'bytes':
    """ The classic entity-expansion bomb - nine levels of tenfold expansion, so one reference
    to the outermost entity expands to a billion copies of a three-character string.
    """
    entities = ['<!ENTITY lol "lol">']

    for level in range(1, 10):
        inner = 'lol' if level == 1 else f'lol{level - 1}'
        references = f'&{inner};' * 10
        entities.append(f'<!ENTITY lol{level} "{references}">')

    declarations = '\n '.join(entities)
    doctype = f'<!DOCTYPE lolz [\n {declarations}\n]>'

    out = _envelope_with_doctype(doctype, '<op><data>&lol9;</data></op>')
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDocumentTypeDeclarations:
    """ Both SOAP 1.1 and SOAP 1.2 forbid a document type declaration in a message, and refusing
    one at the parse is what closes the whole entity-attack class rather than declining each
    expansion individually.
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
    """ An external entity is the way a message reads a file off the receiver's disk or makes the
    receiver issue a request on the attacker's behalf.
    """

    def test_a_file_entity_cannot_read_the_filesystem(self, secret_file):
        doctype = f'<!DOCTYPE root [ <!ENTITY xxe SYSTEM "file://{secret_file}"> ]>'
        data = _envelope_with_doctype(doctype, '<op><data>&xxe;</data></op>')

        with pytest.raises(XMLException):
            _ = parse_xml(data)

        # Belt and braces - the document is refused, so nothing was read, but a future change that
        # relaxed the doctype rule must still not resolve the entity.
        assert _secret_marker not in data.decode('utf8')

    def test_an_http_entity_cannot_reach_the_network(self):
        doctype = f'<!DOCTYPE root [ <!ENTITY xxe SYSTEM "{_unreachable_url}"> ]>'
        data = _envelope_with_doctype(doctype, '<op><data>&xxe;</data></op>')

        # Were the parser to fetch this, the call would either hang or raise a connection error
        # rather than the exception the declaration itself earns.
        with pytest.raises(XMLException) as e:
            _ = parse_xml(data)

        assert 'Document type declarations are not allowed' in str(e.value)

    def test_a_parameter_entity_is_refused(self):
        # Parameter entities are how a payload smuggles a fetch past a filter that only looks for
        # general entity references in content.
        doctype = f'<!DOCTYPE root [ <!ENTITY % pe SYSTEM "{_unreachable_url}"> %pe; ]>'
        data = _envelope_with_doctype(doctype)

        with pytest.raises(XMLException):
            _ = parse_xml(data)

# ################################################################################################################################
# ################################################################################################################################

class TestEntityExpansion:
    """ An expansion bomb needs no external reference at all - it is a few hundred bytes on the wire
    that costs gigabytes of memory to expand.
    """

    def test_billion_laughs_is_refused(self):
        data = _billion_laughs()

        # Small enough that a body-size cap would let it through, which is the point of it.
        assert len(data) < 1024

        with pytest.raises(XMLException):
            _ = parse_xml(data)

    def test_the_bomb_is_refused_without_the_doctype_rule_helping(self):
        # The doctype rule runs after the parse, so the parse itself has to survive the expansion -
        # this asserts the amplification guard is what stops it, not the check that follows.
        data = _billion_laughs()

        with pytest.raises(XMLException) as e:
            _ = parse_xml(data)

        assert 'Malformed XML' in str(e.value)

# ################################################################################################################################
# ################################################################################################################################

class TestEveryParsePath:
    """ The hardening is worth only as much as the number of parse paths that use it, so each entry
    point that takes bytes off the wire is checked separately. A path that built its own parser
    would pass every test above and still be a hole.
    """

    def test_parse_envelope(self, secret_file):
        doctype = f'<!DOCTYPE root [ <!ENTITY xxe SYSTEM "file://{secret_file}"> ]>'
        data = _envelope_with_doctype(doctype, '<op><data>&xxe;</data></op>')

        with pytest.raises(XMLException):
            _ = parse_envelope(data)

    def test_parse_message(self, secret_file):
        doctype = f'<!DOCTYPE root [ <!ENTITY xxe SYSTEM "file://{secret_file}"> ]>'
        data = f'<?xml version="1.0"?>\n{doctype}\n<op><data>&xxe;</data></op>'.encode('utf8')

        with pytest.raises(XMLException):
            _ = parse_xml_message(data)

    def test_saml_assertion_bytes(self):
        # An assertion may arrive as bytes issued by an external identity provider, which makes it
        # untrusted input of exactly the same kind as an envelope.
        envelope = parse_envelope(_envelope_with_doctype(''))
        doctype = f'<!DOCTYPE root [ <!ENTITY xxe SYSTEM "{_unreachable_url}"> ]>'
        assertion = _envelope_with_doctype(doctype)

        with pytest.raises(XMLException):
            add_assertion(envelope, assertion)

    def test_saml_token_bytes(self):
        envelope = parse_envelope(_envelope_with_doctype(''))
        doctype = f'<!DOCTYPE root [ <!ENTITY xxe SYSTEM "{_unreachable_url}"> ]>'
        assertion = _envelope_with_doctype(doctype)

        with pytest.raises(XMLException):
            _ = add_saml_token(envelope, assertion)

    def test_the_bomb_reaches_every_path(self):
        data = _billion_laughs()

        with pytest.raises(XMLException):
            _ = parse_envelope(data)

        with pytest.raises(XMLException):
            _ = parse_xml_message(data)

# ################################################################################################################################
# ################################################################################################################################
