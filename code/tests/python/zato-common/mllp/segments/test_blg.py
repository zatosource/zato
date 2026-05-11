from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BLG


charge_type = "test_charge_type"


class TestBLG:
    """Comprehensive tests for BLG segment."""

    def test_blg_build_and_verify(self):
        seg = BLG()

        seg.charge_type = charge_type

        assert seg.charge_type == charge_type

    def test_blg_to_dict(self):
        seg = BLG()

        seg.charge_type = charge_type

        result = seg.to_dict()

        assert result["_segment_id"] == "BLG"
        assert result["charge_type"] == charge_type

    def test_blg_to_json(self):
        seg = BLG()

        seg.charge_type = charge_type

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BLG"
        assert result["charge_type"] == charge_type
