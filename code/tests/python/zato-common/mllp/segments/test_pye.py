from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PYE


set_id_pye = "test_set_id_pye"


class TestPYE:
    """Comprehensive tests for PYE segment."""

    def test_pye_build_and_verify(self):
        seg = PYE()

        seg.set_id_pye = set_id_pye

        assert seg.set_id_pye == set_id_pye

    def test_pye_to_dict(self):
        seg = PYE()

        seg.set_id_pye = set_id_pye

        result = seg.to_dict()

        assert result["_segment_id"] == "PYE"
        assert result["set_id_pye"] == set_id_pye

    def test_pye_to_json(self):
        seg = PYE()

        seg.set_id_pye = set_id_pye

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PYE"
        assert result["set_id_pye"] == set_id_pye
