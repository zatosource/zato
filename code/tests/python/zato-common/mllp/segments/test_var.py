from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import VAR


documented_date_time = "test_documented_date_time"
stated_variance_date_time = "test_stated_variance_date"


class TestVAR:
    """Comprehensive tests for VAR segment."""

    def test_var_build_and_verify(self):
        seg = VAR()

        seg.documented_date_time = documented_date_time
        seg.stated_variance_date_time = stated_variance_date_time

        assert seg.documented_date_time == documented_date_time
        assert seg.stated_variance_date_time == stated_variance_date_time

    def test_var_to_dict(self):
        seg = VAR()

        seg.documented_date_time = documented_date_time
        seg.stated_variance_date_time = stated_variance_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "VAR"
        assert result["documented_date_time"] == documented_date_time
        assert result["stated_variance_date_time"] == stated_variance_date_time

    def test_var_to_json(self):
        seg = VAR()

        seg.documented_date_time = documented_date_time
        seg.stated_variance_date_time = stated_variance_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "VAR"
        assert result["documented_date_time"] == documented_date_time
        assert result["stated_variance_date_time"] == stated_variance_date_time
