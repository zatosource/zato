from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import NSC


current_cpu = "test_current_cpu"
current_fileserver = "test_current_fileserver"
new_cpu = "test_new_cpu"
new_fileserver = "test_new_fileserver"


class TestNSC:
    """Comprehensive tests for NSC segment."""

    def test_nsc_build_and_verify(self):
        seg = NSC()

        seg.current_cpu = current_cpu
        seg.current_fileserver = current_fileserver
        seg.new_cpu = new_cpu
        seg.new_fileserver = new_fileserver

        assert seg.current_cpu == current_cpu
        assert seg.current_fileserver == current_fileserver
        assert seg.new_cpu == new_cpu
        assert seg.new_fileserver == new_fileserver

    def test_nsc_to_dict(self):
        seg = NSC()

        seg.current_cpu = current_cpu
        seg.current_fileserver = current_fileserver
        seg.new_cpu = new_cpu
        seg.new_fileserver = new_fileserver

        result = seg.to_dict()

        assert result["_segment_id"] == "NSC"
        assert result["current_cpu"] == current_cpu
        assert result["current_fileserver"] == current_fileserver
        assert result["new_cpu"] == new_cpu
        assert result["new_fileserver"] == new_fileserver

    def test_nsc_to_json(self):
        seg = NSC()

        seg.current_cpu = current_cpu
        seg.current_fileserver = current_fileserver
        seg.new_cpu = new_cpu
        seg.new_fileserver = new_fileserver

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "NSC"
        assert result["current_cpu"] == current_cpu
        assert result["current_fileserver"] == current_fileserver
        assert result["new_cpu"] == new_cpu
        assert result["new_fileserver"] == new_fileserver
