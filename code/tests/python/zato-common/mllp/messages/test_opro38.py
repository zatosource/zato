from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OPR_O38


class TestOprO38:
    """Comprehensive tests for OprO38 message."""

    def test_opr_o38_create(self):
        msg = OPR_O38()
        assert msg._structure_id == "OPR_O38"

    def test_opr_o38_segment_access(self):
        msg = OPR_O38()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.tq1._segment_id == "TQ1"

    def test_opr_o38_to_dict(self):
        msg = OPR_O38()

        result = msg.to_dict()

        assert result["_structure_id"] == "OPR_O38"

    def test_opr_o38_to_json(self):
        msg = OPR_O38()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OPR_O38"
