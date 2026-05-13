from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM16
from zato.hl7v2.v2_9.segments import ITM, IVT, MFE, MFI, MSH, PKG, STZ, UAC, VND


class TestMfnM16:
    """Comprehensive tests for MfnM16 message."""

    def test_mfn_m16_create(self):
        msg = MfnM16()
        assert msg._structure_id == "MFN_M16"

    def test_mfn_m16_segment_access(self):
        msg = MfnM16()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.itm._segment_id == "ITM"
        assert msg.stz._segment_id == "STZ"
        assert msg.vnd._segment_id == "VND"
        assert msg.pkg._segment_id == "PKG"
        assert msg.ivt._segment_id == "IVT"

    def test_mfn_m16_to_dict(self):
        msg = MfnM16()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M16"

    def test_mfn_m16_to_json(self):
        msg = MfnM16()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M16"
