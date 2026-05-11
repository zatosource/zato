from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MdmT01
from zato.hl7v2.v2_9.segments import EVN, MSH, OBR, ORC, PID, PV1, TQ1, TXA, UAC


class TestMdmT01:
    """Comprehensive tests for MdmT01 message."""

    def test_mdm_t01_create(self):
        msg = MdmT01()
        assert msg._structure_id == "MDM_T01"

    def test_mdm_t01_segment_access(self):
        msg = MdmT01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.txa._segment_id == "TXA"

    def test_mdm_t01_to_dict(self):
        msg = MdmT01()

        result = msg.to_dict()

        assert result["_structure_id"] == "MDM_T01"

    def test_mdm_t01_to_json(self):
        msg = MdmT01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MDM_T01"
