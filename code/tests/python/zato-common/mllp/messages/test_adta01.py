from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A01


class TestAdtA01:
    """Comprehensive tests for AdtA01 message."""

    def test_adt_a01_create(self):
        msg = ADT_A01()
        assert msg._structure_id == "ADT_A01"

    def test_adt_a01_segment_access(self):
        msg = ADT_A01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.oh3._segment_id == "OH3"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.drg._segment_id == "DRG"
        assert msg.acc._segment_id == "ACC"
        assert msg.ub2._segment_id == "UB2"
        assert msg.pda._segment_id == "PDA"

    def test_adt_a01_to_dict(self):
        msg = ADT_A01()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A01"

    def test_adt_a01_to_json(self):
        msg = ADT_A01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A01"
