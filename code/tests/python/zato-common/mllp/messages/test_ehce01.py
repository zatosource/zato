from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE01
from zato.hl7v2.v2_9.segments import AUT, DG1, IN1, IN2, IVC, MSH, PID, PR1, PSG, PSL, PSS, PV1, PV2, PYE


class TestEhcE01:
    """Comprehensive tests for EhcE01 message."""

    def test_ehc_e01_create(self):
        msg = EhcE01()
        assert msg._structure_id == "EHC_E01"

    def test_ehc_e01_segment_access(self):
        msg = EhcE01()

        assert msg.msh._segment_id == "MSH"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pye._segment_id == "PYE"
        assert msg.aut._segment_id == "AUT"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.dg1._segment_id == "DG1"
        assert msg.psl._segment_id == "PSL"
        assert msg.aut._segment_id == "AUT"
        assert msg.pr1._segment_id == "PR1"

    def test_ehc_e01_to_dict(self):
        msg = EhcE01()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E01"

    def test_ehc_e01_to_json(self):
        msg = EhcE01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E01"
