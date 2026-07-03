from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RPR_I03


class TestRprI03:
    """Comprehensive tests for RprI03 message."""

    def test_rpr_i03_create(self):
        msg = RPR_I03()
        assert msg._structure_id == "RPR_I03"

    def test_rpr_i03_segment_access(self):
        msg = RPR_I03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"

    def test_rpr_i03_to_dict(self):
        msg = RPR_I03()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPR_I03"

    def test_rpr_i03_to_json(self):
        msg = RPR_I03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPR_I03"
