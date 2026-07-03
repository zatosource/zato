from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EHC_E02


class TestEhcE02:
    """Comprehensive tests for EhcE02 message."""

    def test_ehc_e02_create(self):
        msg = EHC_E02()
        assert msg._structure_id == "EHC_E02"

    def test_ehc_e02_segment_access(self):
        msg = EHC_E02()

        assert msg.msh._segment_id == "MSH"

    def test_ehc_e02_to_dict(self):
        msg = EHC_E02()

        result = msg.to_dict()

        assert result["_structure_id"] == "EHC_E02"

    def test_ehc_e02_to_json(self):
        msg = EHC_E02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EHC_E02"
