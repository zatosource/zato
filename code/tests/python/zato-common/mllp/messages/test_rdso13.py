from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RDS_O13


class TestRdsO13:
    """Comprehensive tests for RdsO13 message."""

    def test_rds_o13_create(self):
        msg = RDS_O13()
        assert msg._structure_id == "RDS_O13"

    def test_rds_o13_segment_access(self):
        msg = RDS_O13()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxo._segment_id == "RXO"
        assert msg.rxc._segment_id == "RXC"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxd._segment_id == "RXD"
        assert msg.obx._segment_id == "OBX"

    def test_rds_o13_to_dict(self):
        msg = RDS_O13()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDS_O13"

    def test_rds_o13_to_json(self):
        msg = RDS_O13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDS_O13"
