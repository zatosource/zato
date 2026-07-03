from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M08


class TestMfnM08:
    """Comprehensive tests for MfnM08 message."""

    def test_mfn_m08_create(self):
        msg = MFN_M08()
        assert msg._structure_id == "MFN_M08"

    def test_mfn_m08_segment_access(self):
        msg = MFN_M08()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"

    def test_mfn_m08_to_dict(self):
        msg = MFN_M08()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M08"

    def test_mfn_m08_to_json(self):
        msg = MFN_M08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M08"
