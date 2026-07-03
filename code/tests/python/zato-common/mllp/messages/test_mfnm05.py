from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M05


class TestMfnM05:
    """Comprehensive tests for MfnM05 message."""

    def test_mfn_m05_create(self):
        msg = MFN_M05()
        assert msg._structure_id == "MFN_M05"

    def test_mfn_m05_segment_access(self):
        msg = MFN_M05()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.loc._segment_id == "LOC"
        assert msg.ldp._segment_id == "LDP"

    def test_mfn_m05_to_dict(self):
        msg = MFN_M05()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M05"

    def test_mfn_m05_to_json(self):
        msg = MFN_M05()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M05"
