from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrmO01
from zato.hl7v2.v2_9.segments import BLG, CTD, GT1, IN1, IN2, IN3, MSH, OBR, OBX, ORC, PD1, PID, PV1, PV2, UAC


class TestOrmO01:
    """Comprehensive tests for OrmO01 message."""

    def test_orm_o01_create(self):
        msg = OrmO01()
        assert msg._structure_id == "ORM_O01"

    def test_orm_o01_segment_access(self):
        msg = OrmO01()

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
        assert msg.obr._segment_id == "OBR"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obx._segment_id == "OBX"
        assert msg.blg._segment_id == "BLG"

    def test_orm_o01_to_dict(self):
        msg = OrmO01()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORM_O01"

    def test_orm_o01_to_json(self):
        msg = OrmO01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORM_O01"
