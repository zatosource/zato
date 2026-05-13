from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IAR


management = "test_management"


class TestIAR:
    """Comprehensive tests for IAR segment."""

    def test_iar_build_and_verify(self):
        seg = IAR()

        seg.management = management

        assert seg.management == management

    def test_iar_to_dict(self):
        seg = IAR()

        seg.management = management

        result = seg.to_dict()

        assert result["_segment_id"] == "IAR"
        assert result["management"] == management

    def test_iar_to_json(self):
        seg = IAR()

        seg.management = management

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IAR"
        assert result["management"] == management
