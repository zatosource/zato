from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OmiO23
from zato.hl7v2.v2_9.segments import CTD, DEV, GT1, IN1, IN2, IN3, MSH, OBR, OBX, OH3, ORC, PD1, PID, PV1, PV2, REL, TQ1, UAC


class TestOmiO23:
    """Comprehensive tests for OmiO23 message."""

    def test_omi_o23_create(self):
        msg = OmiO23()
        assert msg._structure_id == "OMI_O23"

    def test_omi_o23_segment_access(self):
        msg = OmiO23()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.gt1._segment_id == "GT1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.ctd._segment_id == "CTD"
        assert msg.rel._segment_id == "REL"
        assert msg.obx._segment_id == "OBX"
        assert msg.dev._segment_id == "DEV"

    def test_omi_o23_to_dict(self):
        msg = OmiO23()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMI_O23"

    def test_omi_o23_to_json(self):
        msg = OmiO23()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMI_O23"
