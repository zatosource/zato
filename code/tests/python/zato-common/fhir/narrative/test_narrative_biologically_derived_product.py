from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import BiologicallyDerivedProduct
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeBiologicallyDerivedProduct:

    def test_narrative_biologically_derived_product_empty(self):
        r = BiologicallyDerivedProduct()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_biologically_derived_product_basic(self):
        r = BiologicallyDerivedProduct()
        r.id = 'test-1'
        r.identifier = {'value': 'ID-12345', 'type': {'text': 'MRN'}}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Identifier:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'MRN: ID-12345' in p_text
        assert found_field, "Field 'Identifier' not found in narrative"

    def test_narrative_biologically_derived_product_identifier(self):
        r = BiologicallyDerivedProduct()
        r.id = 'test-1'
        r.identifier = {'value': 'ID-12345', 'type': {'text': 'MRN'}}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Identifier:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'MRN: ID-12345' in p_text
        assert found_field, "Field 'Identifier' not found in narrative"

    def test_narrative_biologically_derived_product_custom_template(self):
        r = BiologicallyDerivedProduct()
        r.id = 'test-1'
        r.identifier = {'value': 'ID-12345', 'type': {'text': 'MRN'}}
        template = NarrativeTemplate(
            fields=['identifier'],
            labels={'identifier': 'Custom Label'},
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
