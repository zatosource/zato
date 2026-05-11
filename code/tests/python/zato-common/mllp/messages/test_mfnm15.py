from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM15
from zato.hl7v2.v2_9.segments import IIM, MFE, MFI, MSH, UAC


class TestMfnM15:
    """Comprehensive tests for MfnM15 message."""

    def test_mfn_m15_create(self):
        msg = MfnM15()
        assert msg._structure_id == "MFN_M15"

    def test_mfn_m15_segment_access(self):
        msg = MfnM15()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.iim._segment_id == "IIM"

    def test_mfn_m15_to_dict(self):
        msg = MfnM15()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M15"

    def test_mfn_m15_to_json(self):
        msg = MfnM15()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M15"
