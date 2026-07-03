from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DRG_O43


class TestDrgO43:
    """Comprehensive tests for DrgO43 message."""

    def test_drg_o43_create(self):
        msg = DRG_O43()
        assert msg._structure_id == "DRG_O43"

    def test_drg_o43_segment_access(self):
        msg = DRG_O43()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"

    def test_drg_o43_to_dict(self):
        msg = DRG_O43()

        result = msg.to_dict()

        assert result["_structure_id"] == "DRG_O43"

    def test_drg_o43_to_json(self):
        msg = DRG_O43()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DRG_O43"
