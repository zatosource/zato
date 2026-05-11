from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SrmS01
from zato.hl7v2.v2_9.segments import AIG, AIL, AIP, AIS, APR, ARQ, MSH, OBX, PID, PV1, PV2, RGS


class TestSrmS01:
    """Comprehensive tests for SrmS01 message."""

    def test_srm_s01_create(self):
        msg = SrmS01()
        assert msg._structure_id == "SRM_S01"

    def test_srm_s01_segment_access(self):
        msg = SrmS01()

        assert msg.msh._segment_id == "MSH"
        assert msg.arq._segment_id == "ARQ"
        assert msg.apr._segment_id == "APR"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.obx._segment_id == "OBX"
        assert msg.rgs._segment_id == "RGS"
        assert msg.ais._segment_id == "AIS"
        assert msg.apr._segment_id == "APR"
        assert msg.aig._segment_id == "AIG"
        assert msg.apr._segment_id == "APR"
        assert msg.ail._segment_id == "AIL"
        assert msg.apr._segment_id == "APR"
        assert msg.aip._segment_id == "AIP"
        assert msg.apr._segment_id == "APR"

    def test_srm_s01_to_dict(self):
        msg = SrmS01()

        result = msg.to_dict()

        assert result["_structure_id"] == "SRM_S01"

    def test_srm_s01_to_json(self):
        msg = SrmS01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SRM_S01"
