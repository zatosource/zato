from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import MessageHeader
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeMessageHeader:

    def test_narrative_message_header_empty(self):
        r = MessageHeader()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_message_header_basic(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.event = {'display': 'Test Coding'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Event:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Coding' in p_text
        assert found_field, "Field 'Event' not found in narrative"

    def test_narrative_message_header_event(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.event = {'display': 'Test Coding'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Event:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Coding' in p_text
        assert found_field, "Field 'Event' not found in narrative"

    def test_narrative_message_header_destination(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.destination = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Destination:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Destination' not found in narrative"

    def test_narrative_message_header_sender(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.sender = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Sender:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Sender' not found in narrative"

    def test_narrative_message_header_enterer(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.enterer = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Enterer:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Enterer' not found in narrative"

    def test_narrative_message_header_author(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.author = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Author:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Author' not found in narrative"

    def test_narrative_message_header_custom_template(self):
        r = MessageHeader()
        r.id = 'test-1'
        r.event = {'display': 'Test Coding'}
        template = NarrativeTemplate(
            fields=['event'],
            labels={'event': 'Custom Label'},
        )
        narrative = generate_narrative(r, template=template)
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_label = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Custom Label:' in (b.text or ''):
                found_label = True
        assert found_label, "Custom label not found in narrative"
