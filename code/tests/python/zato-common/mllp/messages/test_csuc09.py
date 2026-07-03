from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CSU_C09


class TestCsuC09:
    """Comprehensive tests for CsuC09 message."""

    def test_csu_c09_create(self):
        msg = CSU_C09()
        assert msg._structure_id == "CSU_C09"

    def test_csu_c09_segment_access(self):
        msg = CSU_C09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_csu_c09_to_dict(self):
        msg = CSU_C09()

        result = msg.to_dict()

        assert result["_structure_id"] == "CSU_C09"

    def test_csu_c09_to_json(self):
        msg = CSU_C09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CSU_C09"
