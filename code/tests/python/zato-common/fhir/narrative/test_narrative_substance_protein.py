from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import SubstanceProtein
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeSubstanceProtein:

    def test_narrative_substance_protein_empty(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_substance_protein_basic(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        r.sequenceType = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Sequence Type:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Sequence Type' not found in narrative"

    def test_narrative_substance_protein_sequenceType(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        r.sequenceType = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Sequence Type:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Sequence Type' not found in narrative"

    def test_narrative_substance_protein_numberOfSubunits(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        r.numberOfSubunits = 42
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Number Of Subunits:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert '42' in p_text
        assert found_field, "Field 'Number Of Subunits' not found in narrative"

    def test_narrative_substance_protein_disulfideLinkage(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        r.disulfideLinkage = 'Test Disulfidelinkage'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Disulfide Linkage:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Disulfidelinkage' in p_text
        assert found_field, "Field 'Disulfide Linkage' not found in narrative"

    def test_narrative_substance_protein_subunit(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        r.subunit = {'value': 'test'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Subunit:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'test' in p_text
        assert found_field, "Field 'Subunit' not found in narrative"

    def test_narrative_substance_protein_custom_template(self):
        r = SubstanceProtein()
        r.id = 'test-1'
        r.sequenceType = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        template = NarrativeTemplate(
            fields=['sequenceType'],
            labels={'sequenceType': 'Custom Label'},
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
