from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import DBC_O41


class TestDbcO41:
    """Comprehensive tests for DbcO41 message."""

    def test_dbc_o41_create(self):
        msg = DBC_O41()
        assert msg._structure_id == "DBC_O41"

    def test_dbc_o41_segment_access(self):
        msg = DBC_O41()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_dbc_o41_to_dict(self):
        msg = DBC_O41()

        result = msg.to_dict()

        assert result["_structure_id"] == "DBC_O41"

    def test_dbc_o41_to_json(self):
        msg = DBC_O41()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "DBC_O41"
