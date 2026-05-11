from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import MCP


set_id_mcp = "test_set_id_mcp"
reason_for_universal_service_cost_range = "test_reason_for_universal"


class TestMCP:
    """Comprehensive tests for MCP segment."""

    def test_mcp_build_and_verify(self):
        seg = MCP()

        seg.set_id_mcp = set_id_mcp
        seg.reason_for_universal_service_cost_range = reason_for_universal_service_cost_range

        assert seg.set_id_mcp == set_id_mcp
        assert seg.reason_for_universal_service_cost_range == reason_for_universal_service_cost_range

    def test_mcp_to_dict(self):
        seg = MCP()

        seg.set_id_mcp = set_id_mcp
        seg.reason_for_universal_service_cost_range = reason_for_universal_service_cost_range

        result = seg.to_dict()

        assert result["_segment_id"] == "MCP"
        assert result["set_id_mcp"] == set_id_mcp
        assert result["reason_for_universal_service_cost_range"] == reason_for_universal_service_cost_range

    def test_mcp_to_json(self):
        seg = MCP()

        seg.set_id_mcp = set_id_mcp
        seg.reason_for_universal_service_cost_range = reason_for_universal_service_cost_range

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "MCP"
        assert result["set_id_mcp"] == set_id_mcp
        assert result["reason_for_universal_service_cost_range"] == reason_for_universal_service_cost_range
