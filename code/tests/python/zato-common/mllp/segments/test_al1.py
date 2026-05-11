from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import AL1


set_id_al1 = "test_set_id_al1"


class TestAL1:
    """Comprehensive tests for AL1 segment."""

    def test_al1_build_and_verify(self):
        seg = AL1()

        seg.set_id_al1 = set_id_al1

        assert seg.set_id_al1 == set_id_al1

    def test_al1_to_dict(self):
        seg = AL1()

        seg.set_id_al1 = set_id_al1

        result = seg.to_dict()

        assert result["_segment_id"] == "AL1"
        assert result["set_id_al1"] == set_id_al1

    def test_al1_to_json(self):
        seg = AL1()

        seg.set_id_al1 = set_id_al1

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "AL1"
        assert result["set_id_al1"] == set_id_al1
