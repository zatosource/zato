from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import DbcO41
from zato.hl7v2.v2_9.segments import MSH, OBX, PD1, PID, UAC


class TestDbcO41:
    """Comprehensive tests for DbcO41 message."""

    def test_dbc_o41_create(self):
        msg = DbcO41()
        assert msg._structure_id == "DBC_O41"

    def test_dbc_o41_segment_access(self):
        msg = DbcO41()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"

    def test_dbc_o41_to_dict(self):
        msg = DbcO41()

        result = msg.to_dict()

        assert result["_structure_id"] == "DBC_O41"

    def test_dbc_o41_to_json(self):
        msg = DbcO41()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DBC_O41"
