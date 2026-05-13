from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import VND


set_id_vnd = "test_set_id_vnd"
vendor_name = "test_vendor_name"


class TestVND:
    """Comprehensive tests for VND segment."""

    def test_vnd_build_and_verify(self):
        seg = VND()

        seg.set_id_vnd = set_id_vnd
        seg.vendor_name = vendor_name

        assert seg.set_id_vnd == set_id_vnd
        assert seg.vendor_name == vendor_name

    def test_vnd_to_dict(self):
        seg = VND()

        seg.set_id_vnd = set_id_vnd
        seg.vendor_name = vendor_name

        result = seg.to_dict()

        assert result["_segment_id"] == "VND"
        assert result["set_id_vnd"] == set_id_vnd
        assert result["vendor_name"] == vendor_name

    def test_vnd_to_json(self):
        seg = VND()

        seg.set_id_vnd = set_id_vnd
        seg.vendor_name = vendor_name

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "VND"
        assert result["set_id_vnd"] == set_id_vnd
        assert result["vendor_name"] == vendor_name
