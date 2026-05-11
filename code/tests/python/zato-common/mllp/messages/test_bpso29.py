from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BpsO29
from zato.hl7v2.v2_9.segments import BPO, BPX, MSH, ORC, PD1, PID, PV1, PV2, TQ1, UAC


class TestBpsO29:
    """Comprehensive tests for BpsO29 message."""

    def test_bps_o29_create(self):
        msg = BpsO29()
        assert msg._structure_id == "BPS_O29"

    def test_bps_o29_segment_access(self):
        msg = BpsO29()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.bpo._segment_id == "BPO"
        assert msg.bpx._segment_id == "BPX"

    def test_bps_o29_to_dict(self):
        msg = BpsO29()

        result = msg.to_dict()

        assert result["_structure_id"] == "BPS_O29"

    def test_bps_o29_to_json(self):
        msg = BpsO29()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BPS_O29"
