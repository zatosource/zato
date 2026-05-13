from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ARV


set_id = "test_set_id"


class TestARV:
    """Comprehensive tests for ARV segment."""

    def test_arv_build_and_verify(self):
        seg = ARV()

        seg.set_id = set_id

        assert seg.set_id == set_id

    def test_arv_to_dict(self):
        seg = ARV()

        seg.set_id = set_id

        result = seg.to_dict()

        assert result["_segment_id"] == "ARV"
        assert result["set_id"] == set_id

    def test_arv_to_json(self):
        seg = ARV()

        seg.set_id = set_id

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ARV"
        assert result["set_id"] == set_id
