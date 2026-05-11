from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SAC


registration_date_time = "test_registration_date_ti"
container_height = "test_container_height"
container_diameter = "test_container_diameter"
barrier_delta = "test_barrier_delta"
bottom_delta = "test_bottom_delta"
container_volume = "test_container_volume"
available_specimen_volume = "test_available_specimen_v"
initial_specimen_volume = "test_initial_specimen_vol"
hemolysis_index = "test_hemolysis_index"
lipemia_index = "test_lipemia_index"
icterus_index = "test_icterus_index"
fibrin_index = "test_fibrin_index"


class TestSAC:
    """Comprehensive tests for SAC segment."""

    def test_sac_build_and_verify(self):
        seg = SAC()

        seg.registration_date_time = registration_date_time
        seg.container_height = container_height
        seg.container_diameter = container_diameter
        seg.barrier_delta = barrier_delta
        seg.bottom_delta = bottom_delta
        seg.container_volume = container_volume
        seg.available_specimen_volume = available_specimen_volume
        seg.initial_specimen_volume = initial_specimen_volume
        seg.hemolysis_index = hemolysis_index
        seg.lipemia_index = lipemia_index
        seg.icterus_index = icterus_index
        seg.fibrin_index = fibrin_index

        assert seg.registration_date_time == registration_date_time
        assert seg.container_height == container_height
        assert seg.container_diameter == container_diameter
        assert seg.barrier_delta == barrier_delta
        assert seg.bottom_delta == bottom_delta
        assert seg.container_volume == container_volume
        assert seg.available_specimen_volume == available_specimen_volume
        assert seg.initial_specimen_volume == initial_specimen_volume
        assert seg.hemolysis_index == hemolysis_index
        assert seg.lipemia_index == lipemia_index
        assert seg.icterus_index == icterus_index
        assert seg.fibrin_index == fibrin_index

    def test_sac_to_dict(self):
        seg = SAC()

        seg.registration_date_time = registration_date_time
        seg.container_height = container_height
        seg.container_diameter = container_diameter
        seg.barrier_delta = barrier_delta
        seg.bottom_delta = bottom_delta
        seg.container_volume = container_volume
        seg.available_specimen_volume = available_specimen_volume
        seg.initial_specimen_volume = initial_specimen_volume
        seg.hemolysis_index = hemolysis_index
        seg.lipemia_index = lipemia_index
        seg.icterus_index = icterus_index
        seg.fibrin_index = fibrin_index

        result = seg.to_dict()

        assert result["_segment_id"] == "SAC"
        assert result["registration_date_time"] == registration_date_time
        assert result["container_height"] == container_height
        assert result["container_diameter"] == container_diameter
        assert result["barrier_delta"] == barrier_delta
        assert result["bottom_delta"] == bottom_delta
        assert result["container_volume"] == container_volume
        assert result["available_specimen_volume"] == available_specimen_volume
        assert result["initial_specimen_volume"] == initial_specimen_volume
        assert result["hemolysis_index"] == hemolysis_index
        assert result["lipemia_index"] == lipemia_index
        assert result["icterus_index"] == icterus_index
        assert result["fibrin_index"] == fibrin_index

    def test_sac_to_json(self):
        seg = SAC()

        seg.registration_date_time = registration_date_time
        seg.container_height = container_height
        seg.container_diameter = container_diameter
        seg.barrier_delta = barrier_delta
        seg.bottom_delta = bottom_delta
        seg.container_volume = container_volume
        seg.available_specimen_volume = available_specimen_volume
        seg.initial_specimen_volume = initial_specimen_volume
        seg.hemolysis_index = hemolysis_index
        seg.lipemia_index = lipemia_index
        seg.icterus_index = icterus_index
        seg.fibrin_index = fibrin_index

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SAC"
        assert result["registration_date_time"] == registration_date_time
        assert result["container_height"] == container_height
        assert result["container_diameter"] == container_diameter
        assert result["barrier_delta"] == barrier_delta
        assert result["bottom_delta"] == bottom_delta
        assert result["container_volume"] == container_volume
        assert result["available_specimen_volume"] == available_specimen_volume
        assert result["initial_specimen_volume"] == initial_specimen_volume
        assert result["hemolysis_index"] == hemolysis_index
        assert result["lipemia_index"] == lipemia_index
        assert result["icterus_index"] == icterus_index
        assert result["fibrin_index"] == fibrin_index
