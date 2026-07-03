from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M13


class TestMfnM13:
    """Comprehensive tests for MfnM13 message."""

    def test_mfn_m13_create(self):
        msg = MFN_M13()
        assert msg._structure_id == "MFN_M13"

    def test_mfn_m13_segment_access(self):
        msg = MFN_M13()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"

    def test_mfn_m13_to_dict(self):
        msg = MFN_M13()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M13"

    def test_mfn_m13_to_json(self):
        msg = MFN_M13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M13"
