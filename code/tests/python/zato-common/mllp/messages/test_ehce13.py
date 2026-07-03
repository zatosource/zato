from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EHC_E13


class TestEhcE13:
    """Comprehensive tests for EhcE13 message."""

    def test_ehc_e13_create(self):
        msg = EHC_E13()
        assert msg._structure_id == "EHC_E13"

    def test_ehc_e13_segment_access(self):
        msg = EHC_E13()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.rfi._segment_id == "RFI"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.pid._segment_id == "PID"
        assert msg.psl._segment_id == "PSL"

    def test_ehc_e13_to_dict(self):
        msg = EHC_E13()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E13"

    def test_ehc_e13_to_json(self):
        msg = EHC_E13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E13"
