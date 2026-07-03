from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DBC_O42


class TestDbcO42:
    """Comprehensive tests for DbcO42 message."""

    def test_dbc_o42_create(self):
        msg = DBC_O42()
        assert msg._structure_id == "DBC_O42"

    def test_dbc_o42_segment_access(self):
        msg = DBC_O42()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"

    def test_dbc_o42_to_dict(self):
        msg = DBC_O42()

        result = msg.to_dict()

        assert result["_structure_id"] == "DBC_O42"

    def test_dbc_o42_to_json(self):
        msg = DBC_O42()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DBC_O42"
