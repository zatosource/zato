from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RPI_I01


class TestRpiI01:
    """Comprehensive tests for RpiI01 message."""

    def test_rpi_i01_create(self):
        msg = RPI_I01()
        assert msg._structure_id == "RPI_I01"

    def test_rpi_i01_segment_access(self):
        msg = RPI_I01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.pid._segment_id == "PID"

    def test_rpi_i01_to_dict(self):
        msg = RPI_I01()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPI_I01"

    def test_rpi_i01_to_json(self):
        msg = RPI_I01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPI_I01"
