from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EHC_E04


class TestEhcE04:
    """Comprehensive tests for EhcE04 message."""

    def test_ehc_e04_create(self):
        msg = EHC_E04()
        assert msg._structure_id == "EHC_E04"

    def test_ehc_e04_segment_access(self):
        msg = EHC_E04()

        assert msg.msh._segment_id == "MSH"

    def test_ehc_e04_to_dict(self):
        msg = EHC_E04()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E04"

    def test_ehc_e04_to_json(self):
        msg = EHC_E04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E04"
