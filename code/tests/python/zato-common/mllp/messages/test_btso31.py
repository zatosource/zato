from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import BTS_O31


class TestBtsO31:
    """Comprehensive tests for BtsO31 message."""

    def test_bts_o31_create(self):
        msg = BTS_O31()
        assert msg._structure_id == "BTS_O31"

    def test_bts_o31_segment_access(self):
        msg = BTS_O31()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.bpo._segment_id == "BPO"
        assert msg.btx._segment_id == "BTX"

    def test_bts_o31_to_dict(self):
        msg = BTS_O31()

        result = msg.to_dict()

        assert result["_structure_id"] == "BTS_O31"

    def test_bts_o31_to_json(self):
        msg = BTS_O31()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BTS_O31"
