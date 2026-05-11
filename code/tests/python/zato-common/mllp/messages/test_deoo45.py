from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import DeoO45
from zato.hl7v2.v2_9.segments import MSH, OBR, OBX, PID, PV1, UAC


class TestDeoO45:
    """Comprehensive tests for DeoO45 message."""

    def test_deo_o45_create(self):
        msg = DeoO45()
        assert msg._structure_id == "DEO_O45"

    def test_deo_o45_segment_access(self):
        msg = DeoO45()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.obr._segment_id == "OBR"
        assert msg.obx._segment_id == "OBX"

    def test_deo_o45_to_dict(self):
        msg = DeoO45()

        result = msg.to_dict()

        assert result["_structure_id"] == "DEO_O45"

    def test_deo_o45_to_json(self):
        msg = DeoO45()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DEO_O45"
