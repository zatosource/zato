from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OSM_R26


class TestOsmR26:
    """Comprehensive tests for OsmR26 message."""

    def test_osm_r26_create(self):
        msg = OSM_R26()
        assert msg._structure_id == "OSM_R26"

    def test_osm_r26_segment_access(self):
        msg = OSM_R26()

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
        msg = OSM_R26()

        result = msg.to_dict()

        assert result["_structure_id"] == "OSM_R26"

    def test_osm_r26_to_json(self):
        msg = OSM_R26()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OSM_R26"
