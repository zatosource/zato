from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import LAN


set_id_lan = "test_set_id_lan"


class TestLAN:
    """Comprehensive tests for LAN segment."""

    def test_lan_build_and_verify(self):
        seg = LAN()

        seg.set_id_lan = set_id_lan

        assert seg.set_id_lan == set_id_lan

    def test_lan_to_dict(self):
        seg = LAN()

        seg.set_id_lan = set_id_lan

        result = seg.to_dict()

        assert result["_segment_id"] == "LAN"
        assert result["set_id_lan"] == set_id_lan

    def test_lan_to_json(self):
        seg = LAN()

        seg.set_id_lan = set_id_lan

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "LAN"
        assert result["set_id_lan"] == set_id_lan
