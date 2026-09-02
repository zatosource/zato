from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import VXR_V03


class TestVxrV03:
    """Comprehensive tests for VxrV03 message."""

    def test_vxr_v03_create(self):
        msg = VXR_V03()
        assert msg._structure_id == "VXR_V03"

    def test_vxr_v03_segment_access(self):
        msg = VXR_V03()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"

    def test_vxr_v03_to_dict(self):
        msg = VXR_V03()

        result = msg.to_dict()

        assert result["_structure_id"] == "VXR_V03"

    def test_vxr_v03_to_json(self):
        msg = VXR_V03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "VXR_V03"
