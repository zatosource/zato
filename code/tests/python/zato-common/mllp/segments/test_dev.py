from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DEV


action_code = "test_action_code"
brand_name = "test_brand_name"
model_identifier = "test_model_identifier"
catalogue_identifier = "test_catalogue_identifier"
device_lot_number = "test_device_lot_number"
device_serial_number = "test_device_serial_number"
device_manufacture_date = "test_device_manufacture_d"
device_expiry_date = "test_device_expiry_date"
software_version_number = "test_software_version_num"


class TestDEV:
    """Comprehensive tests for DEV segment."""

    def test_dev_build_and_verify(self):
        seg = DEV()

        seg.action_code = action_code
        seg.brand_name = brand_name
        seg.model_identifier = model_identifier
        seg.catalogue_identifier = catalogue_identifier
        seg.device_lot_number = device_lot_number
        seg.device_serial_number = device_serial_number
        seg.device_manufacture_date = device_manufacture_date
        seg.device_expiry_date = device_expiry_date
        seg.software_version_number = software_version_number

        assert seg.action_code == action_code
        assert seg.brand_name == brand_name
        assert seg.model_identifier == model_identifier
        assert seg.catalogue_identifier == catalogue_identifier
        assert seg.device_lot_number == device_lot_number
        assert seg.device_serial_number == device_serial_number
        assert seg.device_manufacture_date == device_manufacture_date
        assert seg.device_expiry_date == device_expiry_date
        assert seg.software_version_number == software_version_number

    def test_dev_to_dict(self):
        seg = DEV()

        seg.action_code = action_code
        seg.brand_name = brand_name
        seg.model_identifier = model_identifier
        seg.catalogue_identifier = catalogue_identifier
        seg.device_lot_number = device_lot_number
        seg.device_serial_number = device_serial_number
        seg.device_manufacture_date = device_manufacture_date
        seg.device_expiry_date = device_expiry_date
        seg.software_version_number = software_version_number

        result = seg.to_dict()

        assert result["_segment_id"] == "DEV"
        assert result["action_code"] == action_code
        assert result["brand_name"] == brand_name
        assert result["model_identifier"] == model_identifier
        assert result["catalogue_identifier"] == catalogue_identifier
        assert result["device_lot_number"] == device_lot_number
        assert result["device_serial_number"] == device_serial_number
        assert result["device_manufacture_date"] == device_manufacture_date
        assert result["device_expiry_date"] == device_expiry_date
        assert result["software_version_number"] == software_version_number

    def test_dev_to_json(self):
        seg = DEV()

        seg.action_code = action_code
        seg.brand_name = brand_name
        seg.model_identifier = model_identifier
        seg.catalogue_identifier = catalogue_identifier
        seg.device_lot_number = device_lot_number
        seg.device_serial_number = device_serial_number
        seg.device_manufacture_date = device_manufacture_date
        seg.device_expiry_date = device_expiry_date
        seg.software_version_number = software_version_number

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DEV"
        assert result["action_code"] == action_code
        assert result["brand_name"] == brand_name
        assert result["model_identifier"] == model_identifier
        assert result["catalogue_identifier"] == catalogue_identifier
        assert result["device_lot_number"] == device_lot_number
        assert result["device_serial_number"] == device_serial_number
        assert result["device_manufacture_date"] == device_manufacture_date
        assert result["device_expiry_date"] == device_expiry_date
        assert result["software_version_number"] == software_version_number
