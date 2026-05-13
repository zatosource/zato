from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PRD


effective_start_date_of_provider_role = "test_effective_start_date"


class TestPRD:
    """Comprehensive tests for PRD segment."""

    def test_prd_build_and_verify(self):
        seg = PRD()

        seg.effective_start_date_of_provider_role = effective_start_date_of_provider_role

        assert seg.effective_start_date_of_provider_role == effective_start_date_of_provider_role

    def test_prd_to_dict(self):
        seg = PRD()

        seg.effective_start_date_of_provider_role = effective_start_date_of_provider_role

        result = seg.to_dict()

        assert result["_segment_id"] == "PRD"
        assert result["effective_start_date_of_provider_role"] == effective_start_date_of_provider_role

    def test_prd_to_json(self):
        seg = PRD()

        seg.effective_start_date_of_provider_role = effective_start_date_of_provider_role

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PRD"
        assert result["effective_start_date_of_provider_role"] == effective_start_date_of_provider_role
