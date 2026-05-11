from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE04
from zato.hl7v2.v2_9.segments import IVC, MSH, PSG, PSS


class TestEhcE04:
    """Comprehensive tests for EhcE04 message."""

    def test_ehc_e04_create(self):
        msg = EhcE04()
        assert msg._structure_id == "EHC_E04"

    def test_ehc_e04_segment_access(self):
        msg = EhcE04()

        assert msg.msh._segment_id == "MSH"
        assert msg.ivc._segment_id == "IVC"
        assert msg.pss._segment_id == "PSS"
        assert msg.psg._segment_id == "PSG"

    def test_ehc_e04_to_dict(self):
        msg = EhcE04()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E04"

    def test_ehc_e04_to_json(self):
        msg = EhcE04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E04"
