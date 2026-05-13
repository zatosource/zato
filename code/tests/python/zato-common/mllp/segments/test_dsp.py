from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DSP


set_id_dsp = "test_set_id_dsp"
display_level = "test_display_level"
data_line = "test_data_line"
logical_break_point = "test_logical_break_point"
result_id = "test_result_id"


class TestDSP:
    """Comprehensive tests for DSP segment."""

    def test_dsp_build_and_verify(self):
        seg = DSP()

        seg.set_id_dsp = set_id_dsp
        seg.display_level = display_level
        seg.data_line = data_line
        seg.logical_break_point = logical_break_point
        seg.result_id = result_id

        assert seg.set_id_dsp == set_id_dsp
        assert seg.display_level == display_level
        assert seg.data_line == data_line
        assert seg.logical_break_point == logical_break_point
        assert seg.result_id == result_id

    def test_dsp_to_dict(self):
        seg = DSP()

        seg.set_id_dsp = set_id_dsp
        seg.display_level = display_level
        seg.data_line = data_line
        seg.logical_break_point = logical_break_point
        seg.result_id = result_id

        result = seg.to_dict()

        assert result["_segment_id"] == "DSP"
        assert result["set_id_dsp"] == set_id_dsp
        assert result["display_level"] == display_level
        assert result["data_line"] == data_line
        assert result["logical_break_point"] == logical_break_point
        assert result["result_id"] == result_id

    def test_dsp_to_json(self):
        seg = DSP()

        seg.set_id_dsp = set_id_dsp
        seg.display_level = display_level
        seg.data_line = data_line
        seg.logical_break_point = logical_break_point
        seg.result_id = result_id

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DSP"
        assert result["set_id_dsp"] == set_id_dsp
        assert result["display_level"] == display_level
        assert result["data_line"] == data_line
        assert result["logical_break_point"] == logical_break_point
        assert result["result_id"] == result_id
