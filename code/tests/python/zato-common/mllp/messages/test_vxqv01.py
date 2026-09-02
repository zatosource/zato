from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import VXQ_V01


class TestVxqV01:
    """Comprehensive tests for VxqV01 message."""

    def test_vxq_v01_create(self):
        msg = VXQ_V01()
        assert msg._structure_id == "VXQ_V01"

    def test_vxq_v01_segment_access(self):
        msg = VXQ_V01()

        assert msg.msh._segment_id == "MSH"

    def test_vxq_v01_to_dict(self):
        msg = VXQ_V01()

        result = msg.to_dict()

        assert result["_structure_id"] == "VXQ_V01"

    def test_vxq_v01_to_json(self):
        msg = VXQ_V01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "VXQ_V01"
