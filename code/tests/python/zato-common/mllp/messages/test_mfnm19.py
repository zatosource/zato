from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M19


class TestMfnM19:
    """Comprehensive tests for MfnM19 message."""

    def test_mfn_m19_create(self):
        msg = MFN_M19()
        assert msg._structure_id == "MFN_M19"

    def test_mfn_m19_segment_access(self):
        msg = MFN_M19()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.ctr._segment_id == "CTR"
        assert msg.itm._segment_id == "ITM"
        assert msg.vnd._segment_id == "VND"
        assert msg.pkg._segment_id == "PKG"

    def test_mfn_m19_to_dict(self):
        msg = MFN_M19()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M19"

    def test_mfn_m19_to_json(self):
        msg = MFN_M19()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M19"
