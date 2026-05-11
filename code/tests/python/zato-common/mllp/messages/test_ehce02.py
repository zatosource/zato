from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE02
from zato.hl7v2.v2_9.segments import IVC, MSH, PSG, PSS, PYE


class TestEhcE02:
    """Comprehensive tests for EhcE02 message."""

    def test_ehc_e02_create(self):
        msg = EhcE02()
        assert msg._structure_id == "EHC_E02"

    def test_ehc_e02_segment_access(self):
        msg = EhcE02()

        assert msg.msh._segment_id == "MSH"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pye._segment_id == "PYE"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"

    def test_ehc_e02_to_dict(self):
        msg = EhcE02()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E02"

    def test_ehc_e02_to_json(self):
        msg = EhcE02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E02"
