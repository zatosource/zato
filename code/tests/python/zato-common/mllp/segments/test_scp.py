from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SCP


number_of_decontamination_sterilization_devices = "test_number_of_decontamin"
device_name = "test_device_name"
device_model_name = "test_device_model_name"


class TestSCP:
    """Comprehensive tests for SCP segment."""

    def test_scp_build_and_verify(self):
        seg = SCP()

        seg.number_of_decontamination_sterilization_devices = number_of_decontamination_sterilization_devices
        seg.device_name = device_name
        seg.device_model_name = device_model_name

        assert seg.number_of_decontamination_sterilization_devices == number_of_decontamination_sterilization_devices
        assert seg.device_name == device_name
        assert seg.device_model_name == device_model_name

    def test_scp_to_dict(self):
        seg = SCP()

        seg.number_of_decontamination_sterilization_devices = number_of_decontamination_sterilization_devices
        seg.device_name = device_name
        seg.device_model_name = device_model_name

        result = seg.to_dict()

        assert result["_segment_id"] == "SCP"
        assert result["number_of_decontamination_sterilization_devices"] == number_of_decontamination_sterilization_devices
        assert result["device_name"] == device_name
        assert result["device_model_name"] == device_model_name

    def test_scp_to_json(self):
        seg = SCP()

        seg.number_of_decontamination_sterilization_devices = number_of_decontamination_sterilization_devices
        seg.device_name = device_name
        seg.device_model_name = device_model_name

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SCP"
        assert result["number_of_decontamination_sterilization_devices"] == number_of_decontamination_sterilization_devices
        assert result["device_name"] == device_name
        assert result["device_model_name"] == device_model_name
