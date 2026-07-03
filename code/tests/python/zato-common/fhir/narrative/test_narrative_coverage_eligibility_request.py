from __future__ import annotations

from xml.etree import ElementTree

from zato.fhir.r4_0_1 import CoverageEligibilityRequest
from zato.fhir.narrative import generate_narrative, NarrativeTemplate


XHTML_NS = '{http://www.w3.org/1999/xhtml}'


def parse_xhtml(div: str) -> ElementTree.Element:
    """Parse XHTML and return root element. Raises if invalid."""
    return ElementTree.fromstring(div)


class TestNarrativeCoverageEligibilityRequest:

    def test_narrative_coverage_eligibility_request_empty(self):
        r = CoverageEligibilityRequest()
        r.id = 'test-1'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'

    def test_narrative_coverage_eligibility_request_basic(self):
        r = CoverageEligibilityRequest()
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

    def test_narrative_coverage_eligibility_request_status(self):
        r = CoverageEligibilityRequest()
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

    def test_narrative_coverage_eligibility_request_purpose(self):
        r = CoverageEligibilityRequest()
        r.id = 'test-1'
        r.purpose = 'active'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Purpose:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'active' in p_text
        assert found_field, "Field 'Purpose' not found in narrative"

    def test_narrative_coverage_eligibility_request_patient(self):
        r = CoverageEligibilityRequest()
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

    def test_narrative_coverage_eligibility_request_created(self):
        r = CoverageEligibilityRequest()
        r.id = 'test-1'
        r.created = '2024-01-15'
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Created:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert '2024-01-15' in p_text
        assert found_field, "Field 'Created' not found in narrative"

    def test_narrative_coverage_eligibility_request_insurer(self):
        r = CoverageEligibilityRequest()
        r.id = 'test-1'
        r.insurer = {'display': 'Test Reference'}
        narrative = generate_narrative(r)
        assert narrative['status'] == 'generated'
        root = parse_xhtml(narrative['div'])
        assert root.tag == XHTML_NS + 'div'
        p_elements = root.findall(XHTML_NS + 'p')
        assert len(p_elements) >= 1
        found_field = False
        for p in p_elements:
            b = p.find(XHTML_NS + 'b')
            if b is not None and 'Insurer:' in (b.text or ''):
                found_field = True
                p_text = ElementTree.tostring(p, encoding='unicode')
                assert 'Test Reference' in p_text
        assert found_field, "Field 'Insurer' not found in narrative"

    def test_narrative_coverage_eligibility_request_custom_template(self):
        r = CoverageEligibilityRequest()
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
