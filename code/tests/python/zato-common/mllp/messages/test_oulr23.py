from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OUL_R23


class TestOulR23:
    """Comprehensive tests for OulR23 message."""

    def test_oul_r23_create(self):
        msg = OUL_R23()
        assert msg._structure_id == "OUL_R23"

    def test_oul_r23_segment_access(self):
        msg = OUL_R23()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.nte._segment_id == "NTE"
        assert msg.dsc._segment_id == "DSC"

    def test_oul_r23_to_dict(self):
        msg = OUL_R23()

        result = msg.to_dict()

        assert result["_structure_id"] == "OUL_R23"

    def test_oul_r23_to_json(self):
        msg = OUL_R23()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OUL_R23"
