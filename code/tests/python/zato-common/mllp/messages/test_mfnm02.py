from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M02


class TestMfnM02:
    """Comprehensive tests for MfnM02 message."""

    def test_mfn_m02_create(self):
        msg = MFN_M02()
        assert msg._structure_id == "MFN_M02"

    def test_mfn_m02_segment_access(self):
        msg = MFN_M02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.stf._segment_id == "STF"

    def test_mfn_m02_to_dict(self):
        msg = MFN_M02()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M02"

    def test_mfn_m02_to_json(self):
        msg = MFN_M02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M02"
