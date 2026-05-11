from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RDT




class TestRDT:
    """Comprehensive tests for RDT segment."""

    def test_rdt_build_and_verify(self):
        seg = RDT()



    def test_rdt_to_dict(self):
        seg = RDT()


        result = seg.to_dict()

        assert result["_segment_id"] == "RDT"

    def test_rdt_to_json(self):
        seg = RDT()


        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RDT"
