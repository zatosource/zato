from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EHC_E12


class TestEhcE12:
    """Comprehensive tests for EhcE12 message."""

    def test_ehc_e12_create(self):
        msg = EHC_E12()
        assert msg._structure_id == "EHC_E12"

    def test_ehc_e12_segment_access(self):
        msg = EHC_E12()

        assert msg.msh._segment_id == "MSH"
        assert msg.rfi._segment_id == "RFI"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.pid._segment_id == "PID"

    def test_ehc_e12_to_dict(self):
        msg = EHC_E12()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E12"

    def test_ehc_e12_to_json(self):
        msg = EHC_E12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E12"
