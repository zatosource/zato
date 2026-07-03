from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFN_M12


class TestMfnM12:
    """Comprehensive tests for MfnM12 message."""

    def test_mfn_m12_create(self):
        msg = MFN_M12()
        assert msg._structure_id == "MFN_M12"

    def test_mfn_m12_segment_access(self):
        msg = MFN_M12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.om1._segment_id == "OM1"
        assert msg.om7._segment_id == "OM7"

    def test_mfn_m12_to_dict(self):
        msg = MFN_M12()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M12"

    def test_mfn_m12_to_json(self):
        msg = MFN_M12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M12"
