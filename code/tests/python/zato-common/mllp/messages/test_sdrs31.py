from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import SDR_S31


class TestSdrS31:
    """Comprehensive tests for SdrS31 message."""

    def test_sdr_s31_create(self):
        msg = SDR_S31()
        assert msg._structure_id == "SDR_S31"

    def test_sdr_s31_segment_access(self):
        msg = SDR_S31()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.sdd._segment_id == "SDD"

    def test_sdr_s31_to_dict(self):
        msg = SDR_S31()

        result = msg.to_dict()

        assert result["_structure_id"] == "SDR_S31"

    def test_sdr_s31_to_json(self):
        msg = SDR_S31()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SDR_S31"
