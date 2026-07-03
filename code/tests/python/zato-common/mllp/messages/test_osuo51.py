from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OSU_O51


class TestOsuO51:
    """Comprehensive tests for OsuO51 message."""

    def test_osu_o51_create(self):
        msg = OSU_O51()
        assert msg._structure_id == "OSU_O51"

    def test_osu_o51_segment_access(self):
        msg = OSU_O51()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"

    def test_osu_o51_to_dict(self):
        msg = OSU_O51()

        result = msg.to_dict()

        assert result["_structure_id"] == "OSU_O51"

    def test_osu_o51_to_json(self):
        msg = OSU_O51()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OSU_O51"
