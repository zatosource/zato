from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OraR33
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, UAC


class TestOraR33:
    """Comprehensive tests for OraR33 message."""

    def test_ora_r33_create(self):
        msg = OraR33()
        assert msg._structure_id == "ORA_R33"

    def test_ora_r33_segment_access(self):
        msg = OraR33()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.orc._segment_id == "ORC"

    def test_ora_r33_to_dict(self):
        msg = OraR33()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORA_R33"

    def test_ora_r33_to_json(self):
        msg = OraR33()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORA_R33"
