from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EhcE21
from zato.hl7v2.v2_9.segments import AUT, IVC, MSH, PSL


class TestEhcE21:
    """Comprehensive tests for EhcE21 message."""

    def test_ehc_e21_create(self):
        msg = EhcE21()
        assert msg._structure_id == "EHC_E21"

    def test_ehc_e21_segment_access(self):
        msg = EhcE21()

        assert msg.msh._segment_id == "MSH"
        assert msg.ivc._segment_id == "IVC"
        assert msg.psl._segment_id == "PSL"
        assert msg.aut._segment_id == "AUT"

    def test_ehc_e21_to_dict(self):
        msg = EhcE21()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E21"

    def test_ehc_e21_to_json(self):
        msg = EhcE21()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E21"
