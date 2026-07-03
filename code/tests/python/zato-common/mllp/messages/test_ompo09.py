from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMP_O09


class TestOmpO09:
    """Comprehensive tests for OmpO09 message."""

    def test_omp_o09_create(self):
        msg = OMP_O09()
        assert msg._structure_id == "OMP_O09"

    def test_omp_o09_segment_access(self):
        msg = OMP_O09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omp_o09_to_dict(self):
        msg = OMP_O09()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMP_O09"

    def test_omp_o09_to_json(self):
        msg = OMP_O09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMP_O09"
