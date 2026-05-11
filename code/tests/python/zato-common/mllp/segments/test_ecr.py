from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ECR


date_time_completed = "test_date_time_completed"


class TestECR:
    """Comprehensive tests for ECR segment."""

    def test_ecr_build_and_verify(self):
        seg = ECR()

        seg.date_time_completed = date_time_completed

        assert seg.date_time_completed == date_time_completed

    def test_ecr_to_dict(self):
        seg = ECR()

        seg.date_time_completed = date_time_completed

        result = seg.to_dict()

        assert result["_segment_id"] == "ECR"
        assert result["date_time_completed"] == date_time_completed

    def test_ecr_to_json(self):
        seg = ECR()

        seg.date_time_completed = date_time_completed

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ECR"
        assert result["date_time_completed"] == date_time_completed
