from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ADD


addendum_continuation_pointer = "test_addendum_continuatio"


class TestADD:
    """Comprehensive tests for ADD segment."""

    def test_add_build_and_verify(self):
        seg = ADD()

        seg.addendum_continuation_pointer = addendum_continuation_pointer

        assert seg.addendum_continuation_pointer == addendum_continuation_pointer

    def test_add_to_dict(self):
        seg = ADD()

        seg.addendum_continuation_pointer = addendum_continuation_pointer

        result = seg.to_dict()

        assert result["_segment_id"] == "ADD"
        assert result["addendum_continuation_pointer"] == addendum_continuation_pointer

    def test_add_to_json(self):
        seg = ADD()

        seg.addendum_continuation_pointer = addendum_continuation_pointer

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ADD"
        assert result["addendum_continuation_pointer"] == addendum_continuation_pointer
