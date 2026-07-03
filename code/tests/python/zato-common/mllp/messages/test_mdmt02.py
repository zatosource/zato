from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import MDM_T02


class TestMdmT02:
    """Comprehensive tests for MdmT02 message."""

    def test_mdm_t02_create(self):
        msg = MDM_T02()
        assert msg._structure_id == "MDM_T02"

    def test_mdm_t02_segment_access(self):
        msg = MDM_T02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.txa._segment_id == "TXA"

    def test_mdm_t02_to_dict(self):
        msg = MDM_T02()

        result = msg.to_dict()

        assert result["_structure_id"] == "MDM_T02"

    def test_mdm_t02_to_json(self):
        msg = MDM_T02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MDM_T02"
