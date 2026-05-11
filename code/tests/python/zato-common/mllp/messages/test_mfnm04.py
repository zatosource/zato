from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfnM04
from zato.hl7v2.v2_9.segments import CDM, MFE, MFI, MSH, UAC


class TestMfnM04:
    """Comprehensive tests for MfnM04 message."""

    def test_mfn_m04_create(self):
        msg = MfnM04()
        assert msg._structure_id == "MFN_M04"

    def test_mfn_m04_segment_access(self):
        msg = MfnM04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.mfi._segment_id == "MFI"
        assert msg.mfe._segment_id == "MFE"
        assert msg.cdm._segment_id == "CDM"

    def test_mfn_m04_to_dict(self):
        msg = MfnM04()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFN_M04"

    def test_mfn_m04_to_json(self):
        msg = MfnM04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFN_M04"
