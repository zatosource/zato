from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import TCD


automatic_repeat_allowed = "test_automatic_repeat_all"
reflex_allowed = "test_reflex_allowed"
pool_size = "test_pool_size"


class TestTCD:
    """Comprehensive tests for TCD segment."""

    def test_tcd_build_and_verify(self):
        seg = TCD()

        seg.automatic_repeat_allowed = automatic_repeat_allowed
        seg.reflex_allowed = reflex_allowed
        seg.pool_size = pool_size

        assert seg.automatic_repeat_allowed == automatic_repeat_allowed
        assert seg.reflex_allowed == reflex_allowed
        assert seg.pool_size == pool_size

    def test_tcd_to_dict(self):
        seg = TCD()

        seg.automatic_repeat_allowed = automatic_repeat_allowed
        seg.reflex_allowed = reflex_allowed
        seg.pool_size = pool_size

        result = seg.to_dict()

        assert result["_segment_id"] == "TCD"
        assert result["automatic_repeat_allowed"] == automatic_repeat_allowed
        assert result["reflex_allowed"] == reflex_allowed
        assert result["pool_size"] == pool_size

    def test_tcd_to_json(self):
        seg = TCD()

        seg.automatic_repeat_allowed = automatic_repeat_allowed
        seg.reflex_allowed = reflex_allowed
        seg.pool_size = pool_size

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "TCD"
        assert result["automatic_repeat_allowed"] == automatic_repeat_allowed
        assert result["reflex_allowed"] == reflex_allowed
        assert result["pool_size"] == pool_size
