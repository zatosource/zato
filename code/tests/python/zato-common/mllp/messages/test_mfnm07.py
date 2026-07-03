from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M07


class TestMfnM07:
    """Comprehensive tests for MfnM07 message."""

    def test_mfn_m07_create(self):
        msg = MFN_M07()
        assert msg._structure_id == "MFN_M07"

    def test_mfn_m07_segment_access(self):
        msg = MFN_M07()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.cm0._segment_id == "CM0"

    def test_mfn_m07_to_dict(self):
        msg = MFN_M07()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M07"

    def test_mfn_m07_to_json(self):
        msg = MFN_M07()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M07"
