from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import FAC


facility_type = "test_facility_type"
signature_authority_title = "test_signature_authority_"


class TestFAC:
    """Comprehensive tests for FAC segment."""

    def test_fac_build_and_verify(self):
        seg = FAC()

        seg.facility_type = facility_type
        seg.signature_authority_title = signature_authority_title

        assert seg.facility_type == facility_type
        assert seg.signature_authority_title == signature_authority_title

    def test_fac_to_dict(self):
        seg = FAC()

        seg.facility_type = facility_type
        seg.signature_authority_title = signature_authority_title

        result = seg.to_dict()

        assert result["_segment_id"] == "FAC"
        assert result["facility_type"] == facility_type
        assert result["signature_authority_title"] == signature_authority_title

    def test_fac_to_json(self):
        seg = FAC()

        seg.facility_type = facility_type
        seg.signature_authority_title = signature_authority_title

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "FAC"
        assert result["facility_type"] == facility_type
        assert result["signature_authority_title"] == signature_authority_title
