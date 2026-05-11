from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE24
from zato.hl7v2.v2_9.segments import AUT, IVC, MSA, MSH, PSL


class TestEhcE24:
    """Comprehensive tests for EhcE24 message."""

    def test_ehc_e24_create(self):
        msg = EhcE24()
        assert msg._structure_id == "EHC_E24"

    def test_ehc_e24_segment_access(self):
        msg = EhcE24()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.ivc._segment_id == "IVC"
        assert msg.psl._segment_id == "PSL"
        assert msg.aut._segment_id == "AUT"

    def test_ehc_e24_to_dict(self):
        msg = EhcE24()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E24"

    def test_ehc_e24_to_json(self):
        msg = EhcE24()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E24"
