from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import MedicinalProductInteraction
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeMedicinalProductInteraction:

    def test_narrative_medicinal_product_interaction_empty(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_medicinal_product_interaction_basic(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.subject = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Subject:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Subject' not found in narrative"

    def test_narrative_medicinal_product_interaction_subject(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.subject = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Subject:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Subject' not found in narrative"

    def test_narrative_medicinal_product_interaction_description(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.description = 'Test Description'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Description:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Description' in p_text
        assert found_field, "Field 'Description' not found in narrative"

    def test_narrative_medicinal_product_interaction_interactant(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.interactant = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Interactant:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Interactant' not found in narrative"

    def test_narrative_medicinal_product_interaction_type_(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.type_ = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Type:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Type' not found in narrative"

    def test_narrative_medicinal_product_interaction_effect(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.effect = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Effect:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Effect' not found in narrative"

    def test_narrative_medicinal_product_interaction_custom_template(self):
        r = MedicinalProductInteraction()
        r.id = 'test-1'
        r.subject = {'display': 'Test Reference'}
        template = NarrativeTemplate(
            fields=['subject'],
            labels={'subject': 'Custom Label'},
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
