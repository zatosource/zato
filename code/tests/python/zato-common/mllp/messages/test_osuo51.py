from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OsuO51
from zato.hl7v2.v2_9.segments import MSH, ORC, PID, UAC


class TestOsuO51:
    """Comprehensive tests for OsuO51 message."""

    def test_osu_o51_create(self):
        msg = OsuO51()
        assert msg._structure_id == "OSU_O51"

    def test_osu_o51_segment_access(self):
        msg = OsuO51()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"

    def test_osu_o51_to_dict(self):
        msg = OsuO51()

        result = msg.to_dict()

        assert result["_structure_id"] == "OSU_O51"

    def test_osu_o51_to_json(self):
        msg = OsuO51()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OSU_O51"
