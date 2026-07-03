from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADT_A52


class TestAdtA52:
    """Comprehensive tests for AdtA52 message."""

    def test_adt_a52_create(self):
        msg = ADT_A52()
        assert msg._structure_id == "ADT_A52"

    def test_adt_a52_segment_access(self):
        msg = ADT_A52()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"

    def test_adt_a52_to_dict(self):
        msg = ADT_A52()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A52"

    def test_adt_a52_to_json(self):
        msg = ADT_A52()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A52"
