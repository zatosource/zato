from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RCP


query_priority = "test_query_priority"
execution_and_delivery_time = "test_execution_and_delive"
modify_indicator = "test_modify_indicator"


class TestRCP:
    """Comprehensive tests for RCP segment."""

    def test_rcp_build_and_verify(self):
        seg = RCP()

        seg.query_priority = query_priority
        seg.execution_and_delivery_time = execution_and_delivery_time
        seg.modify_indicator = modify_indicator

        assert seg.query_priority == query_priority
        assert seg.execution_and_delivery_time == execution_and_delivery_time
        assert seg.modify_indicator == modify_indicator

    def test_rcp_to_dict(self):
        seg = RCP()

        seg.query_priority = query_priority
        seg.execution_and_delivery_time = execution_and_delivery_time
        seg.modify_indicator = modify_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "RCP"
        assert result["query_priority"] == query_priority
        assert result["execution_and_delivery_time"] == execution_and_delivery_time
        assert result["modify_indicator"] == modify_indicator

    def test_rcp_to_json(self):
        seg = RCP()

        seg.query_priority = query_priority
        seg.execution_and_delivery_time = execution_and_delivery_time
        seg.modify_indicator = modify_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RCP"
        assert result["query_priority"] == query_priority
        assert result["execution_and_delivery_time"] == execution_and_delivery_time
        assert result["modify_indicator"] == modify_indicator
