from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EHC_E10


class TestEhcE10:
    """Comprehensive tests for EhcE10 message."""

    def test_ehc_e10_create(self):
        msg = EHC_E10()
        assert msg._structure_id == "EHC_E10"

    def test_ehc_e10_segment_access(self):
        msg = EHC_E10()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"

    def test_ehc_e10_to_dict(self):
        msg = EHC_E10()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E10"

    def test_ehc_e10_to_json(self):
        msg = EHC_E10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E10"
