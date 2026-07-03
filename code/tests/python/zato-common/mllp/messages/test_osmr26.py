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

    def test_osm_r26_to_dict(self):
        msg = OSM_R26()

        result = msg.to_dict()

        assert result["_structure_id"] == "OSM_R26"

    def test_osm_r26_to_json(self):
        msg = OSM_R26()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OSM_R26"
