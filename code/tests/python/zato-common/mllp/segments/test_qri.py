from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import QRI


candidate_confidence = "test_candidate_confidence"


class TestQRI:
    """Comprehensive tests for QRI segment."""

    def test_qri_build_and_verify(self):
        seg = QRI()

        seg.candidate_confidence = candidate_confidence

        assert seg.candidate_confidence == candidate_confidence

    def test_qri_to_dict(self):
        seg = QRI()

        seg.candidate_confidence = candidate_confidence

        result = seg.to_dict()

        assert result["_segment_id"] == "QRI"
        assert result["candidate_confidence"] == candidate_confidence

    def test_qri_to_json(self):
        seg = QRI()

        seg.candidate_confidence = candidate_confidence

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "QRI"
        assert result["candidate_confidence"] == candidate_confidence
