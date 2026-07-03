from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import SRR_S01


class TestSrrS01:
    """Comprehensive tests for SrrS01 message."""

    def test_srr_s01_create(self):
        msg = SRR_S01()
        assert msg._structure_id == "SRR_S01"

    def test_srr_s01_segment_access(self):
        msg = SRR_S01()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"

    def test_srr_s01_to_dict(self):
        msg = SRR_S01()

        result = msg.to_dict()

        assert result["_structure_id"] == "SRR_S01"

    def test_srr_s01_to_json(self):
        msg = SRR_S01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SRR_S01"
