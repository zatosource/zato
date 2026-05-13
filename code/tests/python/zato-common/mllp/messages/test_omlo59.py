from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OmlO59
from zato.hl7v2.v2_9.segments import BLG, CTD, GT1, IN1, IN2, IN3, IPC, MSH, OBR, OBX, ORC, PD1, PID, PRT, PV1, PV2, REL, SAC, SGH, SGT, SPM, TCD, TQ1, UAC


class TestOmlO59:
    """Comprehensive tests for OmlO59 message."""

    def test_oml_o59_create(self):
        msg = OmlO59()
        assert msg._structure_id == "OML_O59"

    def test_oml_o59_segment_access(self):
        msg = OmlO59()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.gt1._segment_id == "GT1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.tcd._segment_id == "TCD"
        assert msg.ctd._segment_id == "CTD"
        assert msg.rel._segment_id == "REL"
        assert msg.obx._segment_id == "OBX"
        assert msg.tcd._segment_id == "TCD"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.sac._segment_id == "SAC"
        assert msg.obx._segment_id == "OBX"
        assert msg.ipc._segment_id == "IPC"
        assert msg.sgh._segment_id == "SGH"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.prt._segment_id == "PRT"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obx._segment_id == "OBX"
        assert msg.sgt._segment_id == "SGT"
        assert msg.blg._segment_id == "BLG"

    def test_oml_o59_to_dict(self):
        msg = OmlO59()

        result = msg.to_dict()

        assert result["_structure_id"] == "OML_O59"

    def test_oml_o59_to_json(self):
        msg = OmlO59()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OML_O59"
