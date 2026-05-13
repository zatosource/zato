from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MdmT02
from zato.hl7v2.v2_9.segments import EVN, MSH, OBR, OBX, ORC, PID, PV1, TQ1, TXA, UAC


class TestMdmT02:
    """Comprehensive tests for MdmT02 message."""

    def test_mdm_t02_create(self):
        msg = MdmT02()
        assert msg._structure_id == "MDM_T02"

    def test_mdm_t02_segment_access(self):
        msg = MdmT02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.txa._segment_id == "TXA"
        assert msg.obx._segment_id == "OBX"

    def test_mdm_t02_to_dict(self):
        msg = MdmT02()

        result = msg.to_dict()

        assert result["_structure_id"] == "MDM_T02"

    def test_mdm_t02_to_json(self):
        msg = MdmT02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MDM_T02"
