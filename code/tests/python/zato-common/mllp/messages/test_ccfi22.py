from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import CcfI22
from zato.hl7v2.v2_9.segments import MSH, PID, UAC


class TestCcfI22:
    """Comprehensive tests for CcfI22 message."""

    def test_ccf_i22_create(self):
        msg = CcfI22()
        assert msg._structure_id == "CCF_I22"

    def test_ccf_i22_segment_access(self):
        msg = CcfI22()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"

    def test_ccf_i22_to_dict(self):
        msg = CcfI22()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCF_I22"

    def test_ccf_i22_to_json(self):
        msg = CcfI22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCF_I22"
