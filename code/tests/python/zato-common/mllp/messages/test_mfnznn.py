from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_Znn


class TestMfnZnn:
    """Comprehensive tests for MfnZnn message."""

    def test_mfn_znn_create(self):
        msg = MFN_Znn()
        assert msg._structure_id == "MFN_Znn"

    def test_mfn_znn_segment_access(self):
        msg = MFN_Znn()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"

    def test_mfn_znn_to_dict(self):
        msg = MFN_Znn()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_Znn"

    def test_mfn_znn_to_json(self):
        msg = MFN_Znn()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_Znn"
