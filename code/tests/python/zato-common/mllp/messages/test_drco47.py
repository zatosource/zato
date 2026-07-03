from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DRC_O47


class TestDrcO47:
    """Comprehensive tests for DrcO47 message."""

    def test_drc_o47_create(self):
        msg = DRC_O47()
        assert msg._structure_id == "DRC_O47"

    def test_drc_o47_segment_access(self):
        msg = DRC_O47()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.obr._segment_id == "OBR"

    def test_drc_o47_to_dict(self):
        msg = DRC_O47()

        result = msg.to_dict()

        assert result["_structure_id"] == "DRC_O47"

    def test_drc_o47_to_json(self):
        msg = DRC_O47()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DRC_O47"
