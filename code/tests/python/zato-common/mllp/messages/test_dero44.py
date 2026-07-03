from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DER_O44


class TestDerO44:
    """Comprehensive tests for DerO44 message."""

    def test_der_o44_create(self):
        msg = DER_O44()
        assert msg._structure_id == "DER_O44"

    def test_der_o44_segment_access(self):
        msg = DER_O44()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.obr._segment_id == "OBR"

    def test_der_o44_to_dict(self):
        msg = DER_O44()

        result = msg.to_dict()

        assert result["_structure_id"] == "DER_O44"

    def test_der_o44_to_json(self):
        msg = DER_O44()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DER_O44"
