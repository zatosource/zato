from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OsmR26
from zato.hl7v2.v2_9.segments import MSH, OBX, PAC, PID, PV1, SAC, SHP, SPM, UAC


class TestOsmR26:
    """Comprehensive tests for OsmR26 message."""

    def test_osm_r26_create(self):
        msg = OsmR26()
        assert msg._structure_id == "OSM_R26"

    def test_osm_r26_segment_access(self):
        msg = OsmR26()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.shp._segment_id == "SHP"
        assert msg.obx._segment_id == "OBX"
        assert msg.pac._segment_id == "PAC"
        assert msg.spm._segment_id == "SPM"
        assert msg.obx._segment_id == "OBX"
        assert msg.sac._segment_id == "SAC"
        assert msg.obx._segment_id == "OBX"
        assert msg.pid._segment_id == "PID"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pid._segment_id == "PID"

    def test_osm_r26_to_dict(self):
        msg = OsmR26()

        result = msg.to_dict()

        assert result["_structure_id"] == "OSM_R26"

    def test_osm_r26_to_json(self):
        msg = OsmR26()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OSM_R26"
