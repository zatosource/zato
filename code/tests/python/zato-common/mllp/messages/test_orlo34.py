from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrlO34
from zato.hl7v2.v2_9.segments import MSA, MSH, OBR, OBX, ORC, PID, SPM, TQ1, UAC


class TestOrlO34:
    """Comprehensive tests for OrlO34 message."""

    def test_orl_o34_create(self):
        msg = OrlO34()
        assert msg._structure_id == "ORL_O34"

    def test_orl_o34_segment_access(self):
        msg = OrlO34()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"

    def test_orl_o34_to_dict(self):
        msg = OrlO34()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O34"

    def test_orl_o34_to_json(self):
        msg = OrlO34()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O34"
