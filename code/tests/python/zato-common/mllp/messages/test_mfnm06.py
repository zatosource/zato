from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM06
from zato.hl7v2.v2_9.segments import CM0, CM1, MFE, MFI, MSH, UAC


class TestMfnM06:
    """Comprehensive tests for MfnM06 message."""

    def test_mfn_m06_create(self):
        msg = MfnM06()
        assert msg._structure_id == "MFN_M06"

    def test_mfn_m06_segment_access(self):
        msg = MfnM06()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.cm0._segment_id == "CM0"
        assert msg.cm1._segment_id == "CM1"

    def test_mfn_m06_to_dict(self):
        msg = MfnM06()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M06"

    def test_mfn_m06_to_json(self):
        msg = MfnM06()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M06"
