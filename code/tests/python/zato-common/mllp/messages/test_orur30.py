from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORU_R30


class TestOruR30:
    """Comprehensive tests for OruR30 message."""

    def test_oru_r30_create(self):
        msg = ORU_R30()
        assert msg._structure_id == "ORU_R30"

    def test_oru_r30_segment_access(self):
        msg = ORU_R30()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"

    def test_oru_r30_to_dict(self):
        msg = ORU_R30()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORU_R30"

    def test_oru_r30_to_json(self):
        msg = ORU_R30()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORU_R30"
