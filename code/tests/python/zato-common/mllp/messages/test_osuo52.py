from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OsuO52
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, UAC


class TestOsuO52:
    """Comprehensive tests for OsuO52 message."""

    def test_osu_o52_create(self):
        msg = OsuO52()
        assert msg._structure_id == "OSU_O52"

    def test_osu_o52_segment_access(self):
        msg = OsuO52()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"

    def test_osu_o52_to_dict(self):
        msg = OsuO52()

        result = msg.to_dict()

        assert result["_structure_id"] == "OSU_O52"

    def test_osu_o52_to_json(self):
        msg = OsuO52()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OSU_O52"
