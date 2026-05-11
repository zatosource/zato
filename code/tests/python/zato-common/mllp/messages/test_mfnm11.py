from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM11
from zato.hl7v2.v2_9.segments import MFE, MFI, MSH, OM1, OM2, OM6, UAC


class TestMfnM11:
    """Comprehensive tests for MfnM11 message."""

    def test_mfn_m11_create(self):
        msg = MfnM11()
        assert msg._structure_id == "MFN_M11"

    def test_mfn_m11_segment_access(self):
        msg = MfnM11()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.om1._segment_id == "OM1"
        assert msg.om6._segment_id == "OM6"
        assert msg.om2._segment_id == "OM2"

    def test_mfn_m11_to_dict(self):
        msg = MfnM11()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M11"

    def test_mfn_m11_to_json(self):
        msg = MfnM11()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M11"
