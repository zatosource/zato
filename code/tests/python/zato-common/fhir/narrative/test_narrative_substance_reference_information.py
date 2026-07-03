from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import SubstanceReferenceInformation
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeSubstanceReferenceInformation:

    def test_narrative_substance_reference_information_empty(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_substance_reference_information_basic(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.comment = 'Test Comment'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Comment:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Comment' in p_text
        assert found_field, "Field 'Comment' not found in narrative"

    def test_narrative_substance_reference_information_comment(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.comment = 'Test Comment'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Comment:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Comment' in p_text
        assert found_field, "Field 'Comment' not found in narrative"

    def test_narrative_substance_reference_information_gene(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.gene = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Gene:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Gene' not found in narrative"

    def test_narrative_substance_reference_information_geneElement(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.geneElement = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Gene Element:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Gene Element' not found in narrative"

    def test_narrative_substance_reference_information_classification(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.classification = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Classification:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Classification' not found in narrative"

    def test_narrative_substance_reference_information_target(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.target = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Target:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Target' not found in narrative"

    def test_narrative_substance_reference_information_custom_template(self):
        r = SubstanceReferenceInformation()
        r.id = 'test-1'
        r.comment = 'Test Comment'
        template = NarrativeTemplate(
            fields=['comment'],
            labels={'comment': 'Custom Label'},
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
