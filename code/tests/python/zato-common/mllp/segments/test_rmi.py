from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RMI


date_time_incident = "test_date_time_incident"


class TestRMI:
    """Comprehensive tests for RMI segment."""

    def test_rmi_build_and_verify(self):
        seg = RMI()

        seg.date_time_incident = date_time_incident

        assert seg.date_time_incident == date_time_incident

    def test_rmi_to_dict(self):
        seg = RMI()

        seg.date_time_incident = date_time_incident

        result = seg.to_dict()

        assert result["_segment_id"] == "RMI"
        assert result["date_time_incident"] == date_time_incident

    def test_rmi_to_json(self):
        seg = RMI()

        seg.date_time_incident = date_time_incident

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RMI"
        assert result["date_time_incident"] == date_time_incident
