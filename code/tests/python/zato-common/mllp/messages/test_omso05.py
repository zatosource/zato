from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMS_O05


class TestOmsO05:
    """Comprehensive tests for OmsO05 message."""

    def test_oms_o05_create(self):
        msg = OMS_O05()
        assert msg._structure_id == "OMS_O05"

    def test_oms_o05_segment_access(self):
        msg = OMS_O05()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_oms_o05_to_dict(self):
        msg = OMS_O05()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMS_O05"

    def test_oms_o05_to_json(self):
        msg = OMS_O05()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMS_O05"
