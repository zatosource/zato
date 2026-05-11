from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnZnn
from zato.hl7v2.v2_9.segments import MFE, MFI, MSH, UAC


class TestMfnZnn:
    """Comprehensive tests for MfnZnn message."""

    def test_mfn_znn_create(self):
        msg = MfnZnn()
        assert msg._structure_id == "MFN_Znn"

    def test_mfn_znn_segment_access(self):
        msg = MfnZnn()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"

    def test_mfn_znn_to_dict(self):
        msg = MfnZnn()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_Znn"

    def test_mfn_znn_to_json(self):
        msg = MfnZnn()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_Znn"
