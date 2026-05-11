from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import TCC


inventory_limits_warning_level = "test_inventory_limits_war"
automatic_rerun_allowed = "test_automatic_rerun_allo"
automatic_repeat_allowed = "test_automatic_repeat_all"
automatic_reflex_allowed = "test_automatic_reflex_all"


class TestTCC:
    """Comprehensive tests for TCC segment."""

    def test_tcc_build_and_verify(self):
        seg = TCC()

        seg.inventory_limits_warning_level = inventory_limits_warning_level
        seg.automatic_rerun_allowed = automatic_rerun_allowed
        seg.automatic_repeat_allowed = automatic_repeat_allowed
        seg.automatic_reflex_allowed = automatic_reflex_allowed

        assert seg.inventory_limits_warning_level == inventory_limits_warning_level
        assert seg.automatic_rerun_allowed == automatic_rerun_allowed
        assert seg.automatic_repeat_allowed == automatic_repeat_allowed
        assert seg.automatic_reflex_allowed == automatic_reflex_allowed

    def test_tcc_to_dict(self):
        seg = TCC()

        seg.inventory_limits_warning_level = inventory_limits_warning_level
        seg.automatic_rerun_allowed = automatic_rerun_allowed
        seg.automatic_repeat_allowed = automatic_repeat_allowed
        seg.automatic_reflex_allowed = automatic_reflex_allowed

        result = seg.to_dict()

        assert result["_segment_id"] == "TCC"
        assert result["inventory_limits_warning_level"] == inventory_limits_warning_level
        assert result["automatic_rerun_allowed"] == automatic_rerun_allowed
        assert result["automatic_repeat_allowed"] == automatic_repeat_allowed
        assert result["automatic_reflex_allowed"] == automatic_reflex_allowed

    def test_tcc_to_json(self):
        seg = TCC()

        seg.inventory_limits_warning_level = inventory_limits_warning_level
        seg.automatic_rerun_allowed = automatic_rerun_allowed
        seg.automatic_repeat_allowed = automatic_repeat_allowed
        seg.automatic_reflex_allowed = automatic_reflex_allowed

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "TCC"
        assert result["inventory_limits_warning_level"] == inventory_limits_warning_level
        assert result["automatic_rerun_allowed"] == automatic_rerun_allowed
        assert result["automatic_repeat_allowed"] == automatic_repeat_allowed
        assert result["automatic_reflex_allowed"] == automatic_reflex_allowed
