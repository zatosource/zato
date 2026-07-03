from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MFK_M01


class TestMfkM01:
    """Comprehensive tests for MfkM01 message."""

    def test_mfk_m01_create(self):
        msg = MFK_M01()
        assert msg._structure_id == "MFK_M01"

    def test_mfk_m01_segment_access(self):
        msg = MFK_M01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.mfi._segment_id == "MFI"

    def test_mfk_m01_to_dict(self):
        msg = MFK_M01()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFK_M01"

    def test_mfk_m01_to_json(self):
        msg = MFK_M01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFK_M01"
