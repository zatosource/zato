from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import AFF


set_id_aff = "test_set_id_aff"
professional_affiliation_additional_information = "test_professional_affilia"


class TestAFF:
    """Comprehensive tests for AFF segment."""

    def test_aff_build_and_verify(self):
        seg = AFF()

        seg.set_id_aff = set_id_aff
        seg.professional_affiliation_additional_information = professional_affiliation_additional_information

        assert seg.set_id_aff == set_id_aff
        assert seg.professional_affiliation_additional_information == professional_affiliation_additional_information

    def test_aff_to_dict(self):
        seg = AFF()

        seg.set_id_aff = set_id_aff
        seg.professional_affiliation_additional_information = professional_affiliation_additional_information

        result = seg.to_dict()

        assert result["_segment_id"] == "AFF"
        assert result["set_id_aff"] == set_id_aff
        assert result["professional_affiliation_additional_information"] == professional_affiliation_additional_information

    def test_aff_to_json(self):
        seg = AFF()

        seg.set_id_aff = set_id_aff
        seg.professional_affiliation_additional_information = professional_affiliation_additional_information

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "AFF"
        assert result["set_id_aff"] == set_id_aff
        assert result["professional_affiliation_additional_information"] == professional_affiliation_additional_information
