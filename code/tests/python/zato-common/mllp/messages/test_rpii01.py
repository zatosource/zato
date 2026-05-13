from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RpiI01
from zato.hl7v2.v2_9.segments import IN1, IN2, IN3, MSA, MSH, PID, PRD, UAC


class TestRpiI01:
    """Comprehensive tests for RpiI01 message."""

    def test_rpi_i01_create(self):
        msg = RpiI01()
        assert msg._structure_id == "RPI_I01"

    def test_rpi_i01_segment_access(self):
        msg = RpiI01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.prd._segment_id == "PRD"
        assert msg.pid._segment_id == "PID"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"

    def test_rpi_i01_to_dict(self):
        msg = RpiI01()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPI_I01"

    def test_rpi_i01_to_json(self):
        msg = RpiI01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPI_I01"
