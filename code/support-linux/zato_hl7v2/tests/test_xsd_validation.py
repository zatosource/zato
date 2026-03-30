from __future__ import annotations

import pytest
import xmlschema
from pathlib import Path
from typing import Any
from lxml import etree
from faker import Faker

fake = Faker()

XSD_DIR = Path(__file__).parent.parent.parent.parent / "spec" / "hl7v2" / "xsd" / "v2.9"
HL7_NS = "urn:hl7-org:v2xml"
NSMAP = {None: HL7_NS}
XSD_NS = "{http://www.w3.org/2001/XMLSchema}"

BASE_SCHEMA: xmlschema.XMLSchema | None = None


def get_message_xsd_files() -> list[Path]:
    return sorted([
        f for f in XSD_DIR.glob("*.xsd")
        if f.name not in ("segments.xsd", "fields.xsd", "datatypes.xsd")
    ])


def get_base_schema() -> xmlschema.XMLSchema:
    global BASE_SCHEMA
    if BASE_SCHEMA is None:
        BASE_SCHEMA = xmlschema.XMLSchema(str(XSD_DIR / "segments.xsd"), validation='lax')
    return BASE_SCHEMA


def parse_segments_from_xsd(xsd_path: Path) -> list[str]:
    tree = etree.parse(str(xsd_path))
    root = tree.getroot()
    segments = []
    for elem in root.iter(f"{XSD_NS}element"):
        ref = elem.get("ref")
        if ref and not ref.endswith(".CONTENT") and "_" not in ref and "." not in ref:
            segments.append(ref)
    return segments


def parse_all_segment_definitions() -> dict[str, list[str]]:
    segments_xsd = XSD_DIR / "segments.xsd"
    tree = etree.parse(str(segments_xsd))
    root = tree.getroot()

    segment_fields: dict[str, list[str]] = {}

    for complex_type in root.iter(f"{XSD_NS}complexType"):
        name = complex_type.get("name", "")
        if name.endswith(".CONTENT") and "." not in name.replace(".CONTENT", ""):
            seg_name = name.replace(".CONTENT", "")
            fields = []
            for elem in complex_type.iter(f"{XSD_NS}element"):
                ref = elem.get("ref")
                if ref and "." in ref:
                    fields.append(ref)
            segment_fields[seg_name] = fields

    return segment_fields


def parse_all_field_definitions() -> dict[str, list[str]]:
    fields_xsd = XSD_DIR / "fields.xsd"
    tree = etree.parse(str(fields_xsd))
    root = tree.getroot()

    field_components: dict[str, list[str]] = {}

    for complex_type in root.iter(f"{XSD_NS}complexType"):
        name = complex_type.get("name", "")
        if name.endswith(".CONTENT") and name.count(".") == 2:
            field_name = name.replace(".CONTENT", "")
            components = []
            for ext in complex_type.iter(f"{XSD_NS}extension"):
                base = ext.get("base")
                if base:
                    components.append(base)
            field_components[field_name] = components

    return field_components


class TestXsdValidation:

    def test_base_schema_loads(self):
        schema = get_base_schema()
        assert schema is not None
        assert len(schema.elements) > 0

    def test_all_segments_in_base_schema(self):
        schema = get_base_schema()
        expected_segments = ["MSH", "PID", "PV1", "EVN", "OBR", "OBX", "IN1", "NK1", "AL1", "DG1"]
        for seg in expected_segments:
            assert seg in schema.elements, f"Segment {seg} not in schema"

    def test_message_xsd_files_exist(self):
        xsd_files = get_message_xsd_files()
        assert len(xsd_files) == 216, f"Expected 216 message XSD files, got {len(xsd_files)}"

    def test_all_message_structures_have_segments(self):
        schema = get_base_schema()
        xsd_files = get_message_xsd_files()
        failed = []
        total_segments = 0

        for xsd_file in xsd_files:
            structure_id = xsd_file.stem
            try:
                segments = parse_segments_from_xsd(xsd_file)
                for seg_name in segments:
                    if seg_name in schema.elements:
                        total_segments += 1
            except Exception as e:
                failed.append(f"{structure_id}: {str(e)[:100]}")

        assert total_segments > 1000, f"Expected >1000 segment refs, got {total_segments}"
        assert not failed, f"Failed ({len(failed)}):\n" + "\n".join(failed[:20])

    def test_all_segment_definitions_parsed(self):
        seg_fields = parse_all_segment_definitions()
        assert len(seg_fields) > 100, f"Expected >100 segments, got {len(seg_fields)}"

        total_fields = sum(len(fields) for fields in seg_fields.values())
        assert total_fields > 1000, f"Expected >1000 fields, got {total_fields}"

    def test_all_field_definitions_parsed(self):
        field_comps = parse_all_field_definitions()
        assert len(field_comps) > 500, f"Expected >500 fields, got {len(field_comps)}"

    def test_faker_data_for_key_segments(self):
        seg_fields = parse_all_segment_definitions()
        schema = get_base_schema()

        test_segments = ["MSH", "PID", "PV1", "EVN", "OBR", "OBX", "IN1", "NK1"]
        for seg_name in test_segments:
            assert seg_name in seg_fields, f"Segment {seg_name} not parsed"
            assert seg_name in schema.elements, f"Segment {seg_name} not in schema"
            fields = seg_fields[seg_name]
            assert len(fields) > 0, f"Segment {seg_name} has no fields"


class TestDictToXmlConversion:

    def test_adt_a01_dict_to_xml(self):
        from zato_hl7v2 import parse_message

        adt_a01 = (
            "MSH|^~\\&|SEND|FAC|RECV|FAC|20240101120000||ADT^A01^ADT_A01|MSG001|P|2.9\r"
            "EVN|A01|20240101120000\r"
            "PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800101|M\r"
            "PV1|1|I|WARD^101^A\r"
        )

        msg = parse_message(adt_a01)
        d = msg.to_dict()

        assert d["_structure_id"] == "ADT_A01"
        assert "msh" in d
        assert "pid" in d

        xml = dict_to_xml(d)
        assert xml is not None
        assert xml.tag == "ADT_A01"

    def test_oru_r01_dict_to_xml(self):
        from zato_hl7v2 import parse_message

        oru_r01 = (
            "MSH|^~\\&|LAB|FAC|EHR|FAC|20240101130000||ORU^R01^ORU_R01|MSG003|P|2.9\r"
            "PID|1||67890^^^FAC^MR||JONES^MARY\r"
            "OBR|1|||CBC^Complete Blood Count\r"
            "OBX|1|NM|WBC^White Blood Cell||7.5|10*3/uL|4.0-11.0|N|||F\r"
        )

        msg = parse_message(oru_r01)
        d = msg.to_dict()

        assert d["_structure_id"] == "ORU_R01"

        xml = dict_to_xml(d)
        assert xml is not None
        assert xml.tag == "ORU_R01"

    def test_dict_to_xml_roundtrip(self):
        from zato_hl7v2 import parse_message

        adt_a01 = (
            "MSH|^~\\&|SEND|FAC|RECV|FAC|20240101120000||ADT^A01^ADT_A01|MSG001|P|2.9\r"
            "EVN|A01|20240101120000\r"
            "PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800101|M\r"
            "PV1|1|I|WARD^101^A\r"
        )

        msg = parse_message(adt_a01)
        d = msg.to_dict()
        xml = dict_to_xml(d)
        xml_str = etree.tostring(xml, pretty_print=True, encoding="unicode")

        assert "ADT_A01" in xml_str
        assert "MSH" in xml_str
        assert "PID" in xml_str


class TestFakerGeneratedData:

    def test_fake_segment_to_dict(self):
        from zato_hl7v2 import parse_message

        sending_app = fake.company()[:20]
        sending_fac = fake.company()[:20]
        recv_app = fake.company()[:20]
        recv_fac = fake.company()[:20]
        msg_time = fake.date_time().strftime("%Y%m%d%H%M%S")
        msg_id = fake.uuid4()[:20]
        patient_id = fake.ssn().replace("-", "")
        last_name = fake.last_name()
        first_name = fake.first_name()
        dob = fake.date_of_birth().strftime("%Y%m%d")
        sex = fake.random_element(["M", "F"])

        adt_a01 = (
            f"MSH|^~\\&|{sending_app}|{sending_fac}|{recv_app}|{recv_fac}|{msg_time}||ADT^A01^ADT_A01|{msg_id}|P|2.9\r"
            f"EVN|A01|{msg_time}\r"
            f"PID|1||{patient_id}^^^FAC^MR||{last_name}^{first_name}||{dob}|{sex}\r"
            f"PV1|1|I|WARD^101^A\r"
        )

        msg = parse_message(adt_a01)
        d = msg.to_dict()

        assert d["_structure_id"] == "ADT_A01"
        assert "msh" in d
        assert "pid" in d
        assert "evn" in d
        assert "pv1" in d

    def test_fake_multiple_messages(self):
        from zato_hl7v2 import parse_message

        for _ in range(10):
            msg_time = fake.date_time().strftime("%Y%m%d%H%M%S")
            msg_id = fake.uuid4()[:20]
            patient_id = fake.ssn().replace("-", "")
            last_name = fake.last_name()
            first_name = fake.first_name()

            adt_a01 = (
                f"MSH|^~\\&|APP|FAC|APP|FAC|{msg_time}||ADT^A01^ADT_A01|{msg_id}|P|2.9\r"
                f"EVN|A01|{msg_time}\r"
                f"PID|1||{patient_id}^^^FAC^MR||{last_name}^{first_name}||19800101|M\r"
                f"PV1|1|I|WARD^101^A\r"
            )

            msg = parse_message(adt_a01)
            d = msg.to_dict()
            j = msg.to_json()

            assert d["_structure_id"] == "ADT_A01"
            assert isinstance(j, str)
            assert "ADT_A01" in j


def dict_to_xml(d: dict[str, Any], parent: etree._Element | None = None) -> etree._Element:
    structure_id = d.get("_structure_id", "MESSAGE")
    if parent is None:
        root = etree.Element(structure_id, nsmap=NSMAP)
    else:
        root = parent

    for key, value in d.items():
        if key.startswith("_"):
            continue

        if isinstance(value, dict):
            segment_id = value.get("_segment_id", key.upper())
            seg_elem = etree.SubElement(root, segment_id)
            for field_name, field_value in value.items():
                if field_name.startswith("_"):
                    continue
                if field_value is not None:
                    field_elem = etree.SubElement(seg_elem, f"{segment_id}.{field_name}")
                    if isinstance(field_value, dict):
                        for comp_name, comp_value in field_value.items():
                            if comp_value is not None:
                                comp_elem = etree.SubElement(field_elem, comp_name)
                                comp_elem.text = str(comp_value)
                    else:
                        field_elem.text = str(field_value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    dict_to_xml(item, root)

    return root
