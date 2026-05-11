from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SiuS12
from zato.hl7v2.v2_9.segments import AIG, AIL, AIP, AIS, MSH, PD1, PID, PV1, PV2, RGS, SCH


class TestSiuS12:
    """Comprehensive tests for SiuS12 message."""

    def test_siu_s12_create(self):
        msg = SiuS12()
        assert msg._structure_id == "SIU_S12"

    def test_siu_s12_segment_access(self):
        msg = SiuS12()

        assert msg.msh._segment_id == "MSH"
        assert msg.sch._segment_id == "SCH"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.rgs._segment_id == "RGS"
        assert msg.ais._segment_id == "AIS"
        assert msg.aig._segment_id == "AIG"
        assert msg.ail._segment_id == "AIL"
        assert msg.aip._segment_id == "AIP"

    def test_siu_s12_to_dict(self):
        msg = SiuS12()

        result = msg.to_dict()

        assert result["_structure_id"] == "SIU_S12"

    def test_siu_s12_to_json(self):
        msg = SiuS12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SIU_S12"
