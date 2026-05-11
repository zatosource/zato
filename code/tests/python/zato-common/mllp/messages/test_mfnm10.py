from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM10
from zato.hl7v2.v2_9.segments import MFE, MFI, MSH, OM1, OM5, UAC


class TestMfnM10:
    """Comprehensive tests for MfnM10 message."""

    def test_mfn_m10_create(self):
        msg = MfnM10()
        assert msg._structure_id == "MFN_M10"

    def test_mfn_m10_segment_access(self):
        msg = MfnM10()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.om1._segment_id == "OM1"
        assert msg.om5._segment_id == "OM5"

    def test_mfn_m10_to_dict(self):
        msg = MfnM10()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M10"

    def test_mfn_m10_to_json(self):
        msg = MfnM10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M10"
