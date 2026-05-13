from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM13
from zato.hl7v2.v2_9.segments import MFI, MSH, UAC


class TestMfnM13:
    """Comprehensive tests for MfnM13 message."""

    def test_mfn_m13_create(self):
        msg = MfnM13()
        assert msg._structure_id == "MFN_M13"

    def test_mfn_m13_segment_access(self):
        msg = MfnM13()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"

    def test_mfn_m13_to_dict(self):
        msg = MfnM13()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M13"

    def test_mfn_m13_to_json(self):
        msg = MfnM13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M13"
