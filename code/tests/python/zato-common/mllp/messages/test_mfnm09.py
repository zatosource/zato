from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM09
from zato.hl7v2.v2_9.segments import MFE, MFI, MSH, OM1, OM3, UAC


class TestMfnM09:
    """Comprehensive tests for MfnM09 message."""

    def test_mfn_m09_create(self):
        msg = MfnM09()
        assert msg._structure_id == "MFN_M09"

    def test_mfn_m09_segment_access(self):
        msg = MfnM09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.om1._segment_id == "OM1"
        assert msg.om3._segment_id == "OM3"

    def test_mfn_m09_to_dict(self):
        msg = MfnM09()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M09"

    def test_mfn_m09_to_json(self):
        msg = MfnM09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M09"
