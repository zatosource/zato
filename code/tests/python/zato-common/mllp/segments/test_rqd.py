from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RQD


requisition_line_number = "test_requisition_line_num"
requisition_quantity = "test_requisition_quantity"
date_needed = "test_date_needed"


class TestRQD:
    """Comprehensive tests for RQD segment."""

    def test_rqd_build_and_verify(self):
        seg = RQD()

        seg.requisition_line_number = requisition_line_number
        seg.requisition_quantity = requisition_quantity
        seg.date_needed = date_needed

        assert seg.requisition_line_number == requisition_line_number
        assert seg.requisition_quantity == requisition_quantity
        assert seg.date_needed == date_needed

    def test_rqd_to_dict(self):
        seg = RQD()

        seg.requisition_line_number = requisition_line_number
        seg.requisition_quantity = requisition_quantity
        seg.date_needed = date_needed

        result = seg.to_dict()

        assert result["_segment_id"] == "RQD"
        assert result["requisition_line_number"] == requisition_line_number
        assert result["requisition_quantity"] == requisition_quantity
        assert result["date_needed"] == date_needed

    def test_rqd_to_json(self):
        seg = RQD()

        seg.requisition_line_number = requisition_line_number
        seg.requisition_quantity = requisition_quantity
        seg.date_needed = date_needed

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RQD"
        assert result["requisition_line_number"] == requisition_line_number
        assert result["requisition_quantity"] == requisition_quantity
        assert result["date_needed"] == date_needed
