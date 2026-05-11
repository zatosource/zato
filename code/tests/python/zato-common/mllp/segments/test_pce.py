from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PCE


set_id_pce = "test_set_id_pce"


class TestPCE:
    """Comprehensive tests for PCE segment."""

    def test_pce_build_and_verify(self):
        seg = PCE()

        seg.set_id_pce = set_id_pce

        assert seg.set_id_pce == set_id_pce

    def test_pce_to_dict(self):
        seg = PCE()

        seg.set_id_pce = set_id_pce

        result = seg.to_dict()

        assert result["_segment_id"] == "PCE"
        assert result["set_id_pce"] == set_id_pce

    def test_pce_to_json(self):
        seg = PCE()

        seg.set_id_pce = set_id_pce

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PCE"
        assert result["set_id_pce"] == set_id_pce
