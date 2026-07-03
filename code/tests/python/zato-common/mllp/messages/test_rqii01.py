from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RQI_I01


class TestRqiI01:
    """Comprehensive tests for RqiI01 message."""

    def test_rqi_i01_create(self):
        msg = RQI_I01()
        assert msg._structure_id == "RQI_I01"

    def test_rqi_i01_segment_access(self):
        msg = RQI_I01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"

    def test_rqi_i01_to_dict(self):
        msg = RQI_I01()

        result = msg.to_dict()

        assert result["_structure_id"] == "RQI_I01"

    def test_rqi_i01_to_json(self):
        msg = RQI_I01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RQI_I01"
