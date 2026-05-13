from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import EQP


file_name = "test_file_name"
start_date_time = "test_start_date_time"
end_date_time = "test_end_date_time"
transaction_data = "test_transaction_data"


class TestEQP:
    """Comprehensive tests for EQP segment."""

    def test_eqp_build_and_verify(self):
        seg = EQP()

        seg.file_name = file_name
        seg.start_date_time = start_date_time
        seg.end_date_time = end_date_time
        seg.transaction_data = transaction_data

        assert seg.file_name == file_name
        assert seg.start_date_time == start_date_time
        assert seg.end_date_time == end_date_time
        assert seg.transaction_data == transaction_data

    def test_eqp_to_dict(self):
        seg = EQP()

        seg.file_name = file_name
        seg.start_date_time = start_date_time
        seg.end_date_time = end_date_time
        seg.transaction_data = transaction_data

        result = seg.to_dict()

        assert result["_segment_id"] == "EQP"
        assert result["file_name"] == file_name
        assert result["start_date_time"] == start_date_time
        assert result["end_date_time"] == end_date_time
        assert result["transaction_data"] == transaction_data

    def test_eqp_to_json(self):
        seg = EQP()

        seg.file_name = file_name
        seg.start_date_time = start_date_time
        seg.end_date_time = end_date_time
        seg.transaction_data = transaction_data

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "EQP"
        assert result["file_name"] == file_name
        assert result["start_date_time"] == start_date_time
        assert result["end_date_time"] == end_date_time
        assert result["transaction_data"] == transaction_data
