from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE10
from zato.hl7v2.v2_9.segments import IN1, IN2, IPR, IVC, MSA, MSH, PSG, PSL, PSS, PYE


class TestEhcE10:
    """Comprehensive tests for EhcE10 message."""

    def test_ehc_e10_create(self):
        msg = EhcE10()
        assert msg._structure_id == "EHC_E10"

    def test_ehc_e10_segment_access(self):
        msg = EhcE10()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.ipr._segment_id == "IPR"
        assert msg.pye._segment_id == "PYE"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.psl._segment_id == "PSL"

    def test_ehc_e10_to_dict(self):
        msg = EhcE10()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E10"

    def test_ehc_e10_to_json(self):
        msg = EhcE10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E10"
