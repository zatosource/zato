from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM18
from zato.hl7v2.v2_9.segments import MCP, MFE, MFI, MSH, PM1, UAC


class TestMfnM18:
    """Comprehensive tests for MfnM18 message."""

    def test_mfn_m18_create(self):
        msg = MfnM18()
        assert msg._structure_id == "MFN_M18"

    def test_mfn_m18_segment_access(self):
        msg = MfnM18()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.pm1._segment_id == "PM1"
        assert msg.mcp._segment_id == "MCP"

    def test_mfn_m18_to_dict(self):
        msg = MfnM18()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M18"

    def test_mfn_m18_to_json(self):
        msg = MfnM18()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M18"
