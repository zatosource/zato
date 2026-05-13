from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM17
from zato.hl7v2.v2_9.segments import DMI, MFE, MFI, MSH, UAC


class TestMfnM17:
    """Comprehensive tests for MfnM17 message."""

    def test_mfn_m17_create(self):
        msg = MfnM17()
        assert msg._structure_id == "MFN_M17"

    def test_mfn_m17_segment_access(self):
        msg = MfnM17()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.dmi._segment_id == "DMI"

    def test_mfn_m17_to_dict(self):
        msg = MfnM17()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M17"

    def test_mfn_m17_to_json(self):
        msg = MfnM17()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M17"
