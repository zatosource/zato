from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RPI_I04


class TestRpiI04:
    """Comprehensive tests for RpiI04 message."""

    def test_rpi_i04_create(self):
        msg = RPI_I04()
        assert msg._structure_id == "RPI_I04"

    def test_rpi_i04_segment_access(self):
        msg = RPI_I04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.pid._segment_id == "PID"

    def test_rpi_i04_to_dict(self):
        msg = RPI_I04()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPI_I04"

    def test_rpi_i04_to_json(self):
        msg = RPI_I04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPI_I04"
