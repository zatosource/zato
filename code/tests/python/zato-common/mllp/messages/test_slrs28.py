from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SlrS28
from zato.hl7v2.v2_9.segments import MSH, UAC


class TestSlrS28:
    """Comprehensive tests for SlrS28 message."""

    def test_slr_s28_create(self):
        msg = SlrS28()
        assert msg._structure_id == "SLR_S28"

    def test_slr_s28_segment_access(self):
        msg = SlrS28()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_slr_s28_to_dict(self):
        msg = SlrS28()

        result = msg.to_dict()

        assert result["_structure_id"] == "SLR_S28"

    def test_slr_s28_to_json(self):
        msg = SlrS28()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SLR_S28"
