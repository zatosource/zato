from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import CciI22
from zato.hl7v2.v2_9.segments import ACC, AIG, AIL, AIP, AIS, AL1, DB1, DG1, DRG, GOL, IAM, IN1, IN2, IN3, MSA, MSH, OBR, OBX, ODS, ORC, PD1, PDA, PID, PR1, PRB, PRD, PRT, PTH, PV1, PV2, RF1, RGS, RMI, RXA, RXE, RXO, RXR, SCH, UAC


class TestCciI22:
    """Comprehensive tests for CciI22 message."""

    def test_cci_i22_create(self):
        msg = CciI22()
        assert msg._structure_id == "CCI_I22"

    def test_cci_i22_segment_access(self):
        msg = CciI22()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
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
        assert msg.rxa._segment_id == "RXA"
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

    def test_cci_i22_to_dict(self):
        msg = CciI22()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCI_I22"

    def test_cci_i22_to_json(self):
        msg = CciI22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCI_I22"
