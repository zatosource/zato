from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RGV_O15


class TestRgvO15:
    """Comprehensive tests for RgvO15 message."""

    def test_rgv_o15_create(self):
        msg = RGV_O15()
        assert msg._structure_id == "RGV_O15"

    def test_rgv_o15_segment_access(self):
        msg = RGV_O15()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_rgv_o15_to_dict(self):
        msg = RGV_O15()

        result = msg.to_dict()

        assert result["_structure_id"] == "RGV_O15"

    def test_rgv_o15_to_json(self):
        msg = RGV_O15()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RGV_O15"
