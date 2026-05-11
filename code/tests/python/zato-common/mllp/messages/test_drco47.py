from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import DrcO47
from zato.hl7v2.v2_9.segments import MSH, OBR, OBX, PD1, PID, PV1, UAC


class TestDrcO47:
    """Comprehensive tests for DrcO47 message."""

    def test_drc_o47_create(self):
        msg = DrcO47()
        assert msg._structure_id == "DRC_O47"

    def test_drc_o47_segment_access(self):
        msg = DrcO47()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.obr._segment_id == "OBR"

    def test_drc_o47_to_dict(self):
        msg = DrcO47()

        result = msg.to_dict()

        assert result["_structure_id"] == "DRC_O47"

    def test_drc_o47_to_json(self):
        msg = DrcO47()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DRC_O47"
