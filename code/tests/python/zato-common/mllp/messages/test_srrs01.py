from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SrrS01
from zato.hl7v2.v2_9.segments import AIG, AIL, AIP, AIS, MSA, MSH, PID, PV1, PV2, RGS, SCH


class TestSrrS01:
    """Comprehensive tests for SrrS01 message."""

    def test_srr_s01_create(self):
        msg = SrrS01()
        assert msg._structure_id == "SRR_S01"

    def test_srr_s01_segment_access(self):
        msg = SrrS01()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.sch._segment_id == "SCH"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.rgs._segment_id == "RGS"
        assert msg.ais._segment_id == "AIS"
        assert msg.aig._segment_id == "AIG"
        assert msg.ail._segment_id == "AIL"
        assert msg.aip._segment_id == "AIP"

    def test_srr_s01_to_dict(self):
        msg = SrrS01()

        result = msg.to_dict()

        assert result["_structure_id"] == "SRR_S01"

    def test_srr_s01_to_json(self):
        msg = SrrS01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SRR_S01"
