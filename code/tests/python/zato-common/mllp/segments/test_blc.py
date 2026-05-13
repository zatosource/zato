from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import BLC




class TestBLC:
    """Comprehensive tests for BLC segment."""

    def test_blc_build_and_verify(self):
        seg = BLC()



    def test_blc_to_dict(self):
        seg = BLC()


        result = seg.to_dict()

        assert result["_segment_id"] == "BLC"

    def test_blc_to_json(self):
        seg = BLC()


        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "BLC"
