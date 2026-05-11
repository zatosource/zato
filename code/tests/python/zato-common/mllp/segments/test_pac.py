from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PAC


set_id_pac = "test_set_id_pac"
action_code = "test_action_code"


class TestPAC:
    """Comprehensive tests for PAC segment."""

    def test_pac_build_and_verify(self):
        seg = PAC()

        seg.set_id_pac = set_id_pac
        seg.action_code = action_code

        assert seg.set_id_pac == set_id_pac
        assert seg.action_code == action_code

    def test_pac_to_dict(self):
        seg = PAC()

        seg.set_id_pac = set_id_pac
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "PAC"
        assert result["set_id_pac"] == set_id_pac
        assert result["action_code"] == action_code

    def test_pac_to_json(self):
        seg = PAC()

        seg.set_id_pac = set_id_pac
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PAC"
        assert result["set_id_pac"] == set_id_pac
        assert result["action_code"] == action_code
