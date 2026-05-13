from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM08
from zato.hl7v2.v2_9.segments import MFE, MFI, MSH, OM1, OM2, OM3, UAC


class TestMfnM08:
    """Comprehensive tests for MfnM08 message."""

    def test_mfn_m08_create(self):
        msg = MfnM08()
        assert msg._structure_id == "MFN_M08"

    def test_mfn_m08_segment_access(self):
        msg = MfnM08()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.om1._segment_id == "OM1"
        assert msg.om2._segment_id == "OM2"
        assert msg.om3._segment_id == "OM3"

    def test_mfn_m08_to_dict(self):
        msg = MfnM08()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M08"

    def test_mfn_m08_to_json(self):
        msg = MfnM08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M08"
