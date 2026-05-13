from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ZL7


display_sort_key = "test_display_sort_key"
display_sort_key_2 = "test_display_sort_key_2"


class TestZL7:
    """Comprehensive tests for ZL7 segment."""

    def test_zl7_build_and_verify(self):
        seg = ZL7()

        seg.display_sort_key = display_sort_key
        seg.display_sort_key_2 = display_sort_key_2

        assert seg.display_sort_key == display_sort_key
        assert seg.display_sort_key_2 == display_sort_key_2

    def test_zl7_to_dict(self):
        seg = ZL7()

        seg.display_sort_key = display_sort_key
        seg.display_sort_key_2 = display_sort_key_2

        result = seg.to_dict()

        assert result["_segment_id"] == "ZL7"
        assert result["display_sort_key"] == display_sort_key
        assert result["display_sort_key_2"] == display_sort_key_2

    def test_zl7_to_json(self):
        seg = ZL7()

        seg.display_sort_key = display_sort_key
        seg.display_sort_key_2 = display_sort_key_2

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ZL7"
        assert result["display_sort_key"] == display_sort_key
        assert result["display_sort_key_2"] == display_sort_key_2
