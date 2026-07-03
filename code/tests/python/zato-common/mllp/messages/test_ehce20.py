from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EHC_E20


class TestEhcE20:
    """Comprehensive tests for EhcE20 message."""

    def test_ehc_e20_create(self):
        msg = EHC_E20()
        assert msg._structure_id == "EHC_E20"

    def test_ehc_e20_segment_access(self):
        msg = EHC_E20()

        assert msg.msh._segment_id == "MSH"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pid._segment_id == "PID"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.dg1._segment_id == "DG1"
        assert msg.psl._segment_id == "PSL"

    def test_ehc_e20_to_dict(self):
        msg = EHC_E20()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E20"

    def test_ehc_e20_to_json(self):
        msg = EHC_E20()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E20"
