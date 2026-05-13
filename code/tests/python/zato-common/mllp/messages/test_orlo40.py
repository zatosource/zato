from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrlO40
from zato.hl7v2.v2_9.segments import MSA, MSH, OBR, ORC, PAC, PID, SAC, SHP, SPM, TQ1, UAC


class TestOrlO40:
    """Comprehensive tests for OrlO40 message."""

    def test_orl_o40_create(self):
        msg = OrlO40()
        assert msg._structure_id == "ORL_O40"

    def test_orl_o40_segment_access(self):
        msg = OrlO40()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.shp._segment_id == "SHP"
        assert msg.pac._segment_id == "PAC"
        assert msg.spm._segment_id == "SPM"
        assert msg.sac._segment_id == "SAC"

    def test_orl_o40_to_dict(self):
        msg = OrlO40()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O40"

    def test_orl_o40_to_json(self):
        msg = OrlO40()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O40"
