from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import PGL_PC6


class TestPglPc6:
    """Comprehensive tests for PglPc6 message."""

    def test_pgl_pc6_create(self):
        msg = PGL_PC6()
        assert msg._structure_id == "PGL_PC6"

    def test_pgl_pc6_segment_access(self):
        msg = PGL_PC6()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"

    def test_pgl_pc6_to_dict(self):
        msg = PGL_PC6()

        result = msg.to_dict()

        assert result["_structure_id"] == "PGL_PC6"

    def test_pgl_pc6_to_json(self):
        msg = PGL_PC6()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "PGL_PC6"
