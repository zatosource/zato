from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import EDU


set_id_edu = "test_set_id_edu"
academic_degree_granted_date = "test_academic_degree_gran"


class TestEDU:
    """Comprehensive tests for EDU segment."""

    def test_edu_build_and_verify(self):
        seg = EDU()

        seg.set_id_edu = set_id_edu
        seg.academic_degree_granted_date = academic_degree_granted_date

        assert seg.set_id_edu == set_id_edu
        assert seg.academic_degree_granted_date == academic_degree_granted_date

    def test_edu_to_dict(self):
        seg = EDU()

        seg.set_id_edu = set_id_edu
        seg.academic_degree_granted_date = academic_degree_granted_date

        result = seg.to_dict()

        assert result["_segment_id"] == "EDU"
        assert result["set_id_edu"] == set_id_edu
        assert result["academic_degree_granted_date"] == academic_degree_granted_date

    def test_edu_to_json(self):
        seg = EDU()

        seg.set_id_edu = set_id_edu
        seg.academic_degree_granted_date = academic_degree_granted_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "EDU"
        assert result["set_id_edu"] == set_id_edu
        assert result["academic_degree_granted_date"] == academic_degree_granted_date
