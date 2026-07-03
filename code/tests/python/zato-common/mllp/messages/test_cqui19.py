from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CQU_I19


class TestCquI19:
    """Comprehensive tests for CquI19 message."""

    def test_cqu_i19_create(self):
        msg = CQU_I19()
        assert msg._structure_id == "CQU_I19"

    def test_cqu_i19_segment_access(self):
        msg = CQU_I19()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.rf1._segment_id == "RF1"
        assert msg.prd._segment_id == "PRD"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.sch._segment_id == "SCH"
        assert msg.rgs._segment_id == "RGS"
        assert msg.ais._segment_id == "AIS"
        assert msg.aig._segment_id == "AIG"
        assert msg.ail._segment_id == "AIL"
        assert msg.aip._segment_id == "AIP"
        assert msg.obx._segment_id == "OBX"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.ods._segment_id == "ODS"
        assert msg.pr1._segment_id == "PR1"
        assert msg.rf1._segment_id == "RF1"
        assert msg.al1._segment_id == "AL1"
        assert msg.iam._segment_id == "IAM"
        assert msg.acc._segment_id == "ACC"
        assert msg.rmi._segment_id == "RMI"
        assert msg.db1._segment_id == "DB1"
        assert msg.dg1._segment_id == "DG1"
        assert msg.drg._segment_id == "DRG"
        assert msg.pda._segment_id == "PDA"
        assert msg.obx._segment_id == "OBX"
        assert msg.prt._segment_id == "PRT"
        assert msg.prd._segment_id == "PRD"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.rxo._segment_id == "RXO"
        assert msg.obx._segment_id == "OBX"
        assert msg.rxe._segment_id == "RXE"
        assert msg.obx._segment_id == "OBX"
        assert msg.rxr._segment_id == "RXR"
        assert msg.obx._segment_id == "OBX"
        assert msg.prb._segment_id == "PRB"
        assert msg.prt._segment_id == "PRT"
        assert msg.prd._segment_id == "PRD"
        assert msg.obx._segment_id == "OBX"
        assert msg.gol._segment_id == "GOL"
        assert msg.prt._segment_id == "PRT"
        assert msg.prd._segment_id == "PRD"
        assert msg.obx._segment_id == "OBX"
        assert msg.pth._segment_id == "PTH"
        assert msg.prt._segment_id == "PRT"
        assert msg.prd._segment_id == "PRD"
        assert msg.obx._segment_id == "OBX"

    def test_cqu_i19_to_dict(self):
        msg = CQU_I19()

        result = msg.to_dict()

        assert result["_structure_id"] == "CQU_I19"

    def test_cqu_i19_to_json(self):
        msg = CQU_I19()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CQU_I19"
