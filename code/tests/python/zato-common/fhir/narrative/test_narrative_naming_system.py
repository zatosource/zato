from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import NamingSystem
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeNamingSystem:

    def test_narrative_naming_system_empty(self):
        r = NamingSystem()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_naming_system_basic(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.name = 'Test Name'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Name:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Name' in p_text
        assert found_field, "Field 'Name' not found in narrative"

    def test_narrative_naming_system_name(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.name = 'Test Name'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Name:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Name' in p_text
        assert found_field, "Field 'Name' not found in narrative"

    def test_narrative_naming_system_status(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.status = 'active'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Status:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'active' in p_text
        assert found_field, "Field 'Status' not found in narrative"

    def test_narrative_naming_system_kind(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.kind = 'active'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Kind:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'active' in p_text
        assert found_field, "Field 'Kind' not found in narrative"

    def test_narrative_naming_system_date(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.date = '2024-01-15'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Date:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert '2024-01-15' in p_text
        assert found_field, "Field 'Date' not found in narrative"

    def test_narrative_naming_system_publisher(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.publisher = 'Test Publisher'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Publisher:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Publisher' in p_text
        assert found_field, "Field 'Publisher' not found in narrative"

    def test_narrative_naming_system_custom_template(self):
        r = NamingSystem()
        r.id = 'test-1'
        r.name = 'Test Name'
        template = NarrativeTemplate(
            fields=['name'],
            labels={'name': 'Custom Label'},
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
