from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IPC


scheduled_station_ae_title = "test_scheduled_station_ae"
action_code = "test_action_code"


class TestIPC:
    """Comprehensive tests for IPC segment."""

    def test_ipc_build_and_verify(self):
        seg = IPC()

        seg.scheduled_station_ae_title = scheduled_station_ae_title
        seg.action_code = action_code

        assert seg.scheduled_station_ae_title == scheduled_station_ae_title
        assert seg.action_code == action_code

    def test_ipc_to_dict(self):
        seg = IPC()

        seg.scheduled_station_ae_title = scheduled_station_ae_title
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "IPC"
        assert result["scheduled_station_ae_title"] == scheduled_station_ae_title
        assert result["action_code"] == action_code

    def test_ipc_to_json(self):
        seg = IPC()

        seg.scheduled_station_ae_title = scheduled_station_ae_title
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IPC"
        assert result["scheduled_station_ae_title"] == scheduled_station_ae_title
        assert result["action_code"] == action_code
