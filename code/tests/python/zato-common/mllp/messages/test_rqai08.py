from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RqaI08
from zato.hl7v2.v2_9.segments import ACC, AUT, CTD, IN1, IN2, IN3, MSH, OBR, OBX, PID, PR1, PRD, PV1, PV2, RF1, UAC


class TestRqaI08:
    """Comprehensive tests for RqaI08 message."""

    def test_rqa_i08_create(self):
        msg = RqaI08()
        assert msg._structure_id == "RQA_I08"

    def test_rqa_i08_segment_access(self):
        msg = RqaI08()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.rf1._segment_id == "RF1"
        assert msg.aut._segment_id == "AUT"
        assert msg.ctd._segment_id == "CTD"
        assert msg.prd._segment_id == "PRD"
        assert msg.pid._segment_id == "PID"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.acc._segment_id == "ACC"
        assert msg.pr1._segment_id == "PR1"
        assert msg.aut._segment_id == "AUT"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"

    def test_rqa_i08_to_dict(self):
        msg = RqaI08()

        result = msg.to_dict()

        assert result["_structure_id"] == "RQA_I08"

    def test_rqa_i08_to_json(self):
        msg = RqaI08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RQA_I08"
