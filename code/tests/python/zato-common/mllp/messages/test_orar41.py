from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORA_R41


class TestOraR41:
    """Comprehensive tests for OraR41 message."""

    def test_ora_r41_create(self):
        msg = ORA_R41()
        assert msg._structure_id == "ORA_R41"

    def test_ora_r41_segment_access(self):
        msg = ORA_R41()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"

    def test_ora_r41_to_dict(self):
        msg = ORA_R41()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORA_R41"

    def test_ora_r41_to_json(self):
        msg = ORA_R41()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORA_R41"
