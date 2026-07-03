from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import ImmunizationEvaluation
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeImmunizationEvaluation:

    def test_narrative_immunization_evaluation_empty(self):
        r = ImmunizationEvaluation()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_immunization_evaluation_basic(self):
        r = ImmunizationEvaluation()
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

    def test_narrative_immunization_evaluation_status(self):
        r = ImmunizationEvaluation()
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

    def test_narrative_immunization_evaluation_patient(self):
        r = ImmunizationEvaluation()
        r.id = 'test-1'
        r.patient = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Patient:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Patient' not found in narrative"

    def test_narrative_immunization_evaluation_targetDisease(self):
        r = ImmunizationEvaluation()
        r.id = 'test-1'
        r.targetDisease = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Target Disease:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Target Disease' not found in narrative"

    def test_narrative_immunization_evaluation_immunizationEvent(self):
        r = ImmunizationEvaluation()
        r.id = 'test-1'
        r.immunizationEvent = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Immunization Event:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Immunization Event' not found in narrative"

    def test_narrative_immunization_evaluation_doseStatus(self):
        r = ImmunizationEvaluation()
        r.id = 'test-1'
        r.doseStatus = {'text': 'Test Code', 'coding': [{'display': 'Test Display'}]}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Dose Status:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Code' in p_text
        assert found_field, "Field 'Dose Status' not found in narrative"

    def test_narrative_immunization_evaluation_custom_template(self):
        r = ImmunizationEvaluation()
        r.id = 'test-1'
        r.status = 'active'
        template = NarrativeTemplate(
            fields=['status'],
            labels={'status': 'Custom Label'},
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
