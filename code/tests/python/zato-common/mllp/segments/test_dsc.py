from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DSC


continuation_pointer = "test_continuation_pointer"
continuation_style = "test_continuation_style"


class TestDSC:
    """Comprehensive tests for DSC segment."""

    def test_dsc_build_and_verify(self):
        seg = DSC()

        seg.continuation_pointer = continuation_pointer
        seg.continuation_style = continuation_style

        assert seg.continuation_pointer == continuation_pointer
        assert seg.continuation_style == continuation_style

    def test_dsc_to_dict(self):
        seg = DSC()

        seg.continuation_pointer = continuation_pointer
        seg.continuation_style = continuation_style

        result = seg.to_dict()

        assert result["_segment_id"] == "DSC"
        assert result["continuation_pointer"] == continuation_pointer
        assert result["continuation_style"] == continuation_style

    def test_dsc_to_json(self):
        seg = DSC()

        seg.continuation_pointer = continuation_pointer
        seg.continuation_style = continuation_style

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DSC"
        assert result["continuation_pointer"] == continuation_pointer
        assert result["continuation_style"] == continuation_style
