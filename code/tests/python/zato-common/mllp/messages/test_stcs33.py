from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import StcS33
from zato.hl7v2.v2_9.segments import MSH, UAC


class TestStcS33:
    """Comprehensive tests for StcS33 message."""

    def test_stc_s33_create(self):
        msg = StcS33()
        assert msg._structure_id == "STC_S33"

    def test_stc_s33_segment_access(self):
        msg = StcS33()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_stc_s33_to_dict(self):
        msg = StcS33()

        result = msg.to_dict()

        assert result["_structure_id"] == "STC_S33"

    def test_stc_s33_to_json(self):
        msg = StcS33()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "STC_S33"
