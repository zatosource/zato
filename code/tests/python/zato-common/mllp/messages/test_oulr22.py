from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OUL_R22


class TestOulR22:
    """Comprehensive tests for OulR22 message."""

    def test_oul_r22_create(self):
        msg = OUL_R22()
        assert msg._structure_id == "OUL_R22"

    def test_oul_r22_segment_access(self):
        msg = OUL_R22()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.nte._segment_id == "NTE"
        assert msg.dsc._segment_id == "DSC"

    def test_oul_r22_to_dict(self):
        msg = OUL_R22()

        result = msg.to_dict()

        assert result["_structure_id"] == "OUL_R22"

    def test_oul_r22_to_json(self):
        msg = OUL_R22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OUL_R22"
