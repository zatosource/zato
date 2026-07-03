from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import BAR_P12


class TestBarP12:
    """Comprehensive tests for BarP12 message."""

    def test_bar_p12_create(self):
        msg = BAR_P12()
        assert msg._structure_id == "BAR_P12"

    def test_bar_p12_segment_access(self):
        msg = BAR_P12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.drg._segment_id == "DRG"
        assert msg.obx._segment_id == "OBX"

    def test_bar_p12_to_dict(self):
        msg = BAR_P12()

        result = msg.to_dict()

        assert result["_structure_id"] == "BAR_P12"

    def test_bar_p12_to_json(self):
        msg = BAR_P12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BAR_P12"
