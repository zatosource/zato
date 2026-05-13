from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RriI12
from zato.hl7v2.v2_9.segments import ACC, AUT, CTD, MSA, MSH, OBR, OBX, PID, PR1, PRD, PV1, PV2, RF1, UAC


class TestRriI12:
    """Comprehensive tests for RriI12 message."""

    def test_rri_i12_create(self):
        msg = RriI12()
        assert msg._structure_id == "RRI_I12"

    def test_rri_i12_segment_access(self):
        msg = RriI12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.rf1._segment_id == "RF1"
        assert msg.aut._segment_id == "AUT"
        assert msg.ctd._segment_id == "CTD"
        assert msg.prd._segment_id == "PRD"
        assert msg.pid._segment_id == "PID"
        assert msg.acc._segment_id == "ACC"
        assert msg.pr1._segment_id == "PR1"
        assert msg.aut._segment_id == "AUT"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"

    def test_rri_i12_to_dict(self):
        msg = RriI12()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRI_I12"

    def test_rri_i12_to_json(self):
        msg = RriI12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRI_I12"
