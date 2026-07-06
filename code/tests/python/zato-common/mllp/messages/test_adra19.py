from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ADR_A19


class TestAdrA19:
    """Comprehensive tests for AdrA19 message."""

    def test_adr_a19_create(self):
        msg = ADR_A19()
        assert msg._structure_id == "ADR_A19"

    def test_adr_a19_segment_access(self):
        msg = ADR_A19()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.dsc._segment_id == "DSC"

    def test_adr_a19_to_dict(self):
        msg = ADR_A19()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADR_A19"

    def test_adr_a19_to_json(self):
        msg = ADR_A19()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADR_A19"
