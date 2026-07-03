from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import SubstanceSourceMaterial
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeSubstanceSourceMaterial:

    def test_narrative_substance_source_material_empty(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_substance_source_material_basic(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.sourceMaterialClass = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Source Material Class:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Source Material Class' not found in narrative"

    def test_narrative_substance_source_material_sourceMaterialClass(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.sourceMaterialClass = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Source Material Class:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Source Material Class' not found in narrative"

    def test_narrative_substance_source_material_sourceMaterialType(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.sourceMaterialType = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Source Material Type:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Source Material Type' not found in narrative"

    def test_narrative_substance_source_material_sourceMaterialState(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.sourceMaterialState = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Source Material State:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Source Material State' not found in narrative"

    def test_narrative_substance_source_material_organismId(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.organismId = {'value': 'ID-12345', 'type': {'text': 'MRN'}}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Organism Id:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'MRN: ID-12345' in p_text
        assert found_field, "Field 'Organism Id' not found in narrative"

    def test_narrative_substance_source_material_organismName(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.organismName = 'Test Organismname'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Organism Name:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Organismname' in p_text
        assert found_field, "Field 'Organism Name' not found in narrative"

    def test_narrative_substance_source_material_custom_template(self):
        r = SubstanceSourceMaterial()
        r.id = 'test-1'
        r.sourceMaterialClass = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        template = NarrativeTemplate(
            fields=['sourceMaterialClass'],
            labels={'sourceMaterialClass': 'Custom Label'},
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
