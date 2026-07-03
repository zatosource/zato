from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import VXU_V04


class TestVxuV04:
    """Comprehensive tests for VxuV04 message."""

    def test_vxu_v04_create(self):
        msg = VXU_V04()
        assert msg._structure_id == "VXU_V04"

    def test_vxu_v04_segment_access(self):
        msg = VXU_V04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"

    def test_vxu_v04_to_dict(self):
        msg = VXU_V04()

        result = msg.to_dict()

        assert result["_structure_id"] == "VXU_V04"

    def test_vxu_v04_to_json(self):
        msg = VXU_V04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "VXU_V04"
