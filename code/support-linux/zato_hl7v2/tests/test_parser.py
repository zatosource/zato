import pytest

from zato_hl7v2 import parse_message

ADT_A01 = (
    "MSH|^~\\&|SEND|FAC|RECV|FAC|20240101120000||ADT^A01^ADT_A01|MSG001|P|2.9\r"
    "EVN|A01|20240101120000\r"
    "PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800101|M\r"
    "PV1|1|I|WARD^101^A\r"
)

MDM_T01 = (
    "MSH|^~\\&|SEND|FAC|RECV|FAC|20240101120000||MDM^T01^MDM_T01|MSG002|P|2.9\r"
    "EVN|T01|20240101120000\r"
    "PID|1||67890^^^FAC^MR||JONES^MARY\r"
    "PV1|1|O\r"
    "TXA|1|CN|||20240101||||||||||1||\r"
)

ORU_R01 = (
    "MSH|^~\\&|LAB|FAC|EHR|FAC|20240101130000||ORU^R01^ORU_R01|MSG003|P|2.9\r"
    "PID|1||67890^^^FAC^MR||JONES^MARY\r"
    "OBR|1|||CBC^Complete Blood Count\r"
    "OBX|1|NM|WBC^White Blood Cell||7.5|10*3/uL|4.0-11.0|N|||F\r"
)


def test_parse_adt_a01():
    msg = parse_message(ADT_A01)
    assert msg._structure_id == "ADT_A01"
    assert msg.pid is not None
    assert msg.evn is not None
    assert msg.pv1 is not None


def test_parse_oru_r01():
    msg = parse_message(ORU_R01)
    assert msg._structure_id == "ORU_R01"


def test_parse_mdm_t01():
    msg = parse_message(MDM_T01)
    assert msg._structure_id == "MDM_T01"
    assert msg.txa is not None


def test_delimiter_discovery():
    alt = ADT_A01.replace("^", "!")
    msg = parse_message(alt)
    assert msg._structure_id == "ADT_A01"
    assert msg.pid is not None


def test_optional_segment_absent():
    msg = parse_message(ADT_A01)
    assert msg.pd1 is None


def test_repeating_group():
    with_insurance = (
        ADT_A01
        + "IN1|1|PLAN1|INS001\r"
        + "IN1|2|PLAN2|INS002\r"
    )
    msg = parse_message(with_insurance)
    assert len(msg.insurance) == 2


def test_invalid_message_type():
    bad = ADT_A01.replace("ADT^A01^ADT_A01", "ZZZ^Z99^ZZZ_Z99")
    with pytest.raises(Exception):
        parse_message(bad)


def test_message_to_dict():
    msg = parse_message(ADT_A01)
    d = msg.to_dict()
    assert d["_structure_id"] == "ADT_A01"
    assert "msh" in d
    assert "pid" in d
    assert "evn" in d
    assert "pv1" in d
    assert d["msh"]["_segment_id"] == "MSH"
    assert d["pid"]["_segment_id"] == "PID"


def test_message_to_json():
    msg = parse_message(ADT_A01)
    j = msg.to_json()
    assert isinstance(j, str)
    import json
    parsed = json.loads(j)
    assert parsed["_structure_id"] == "ADT_A01"
    assert "msh" in parsed
    assert "pid" in parsed


def test_message_to_json_indent():
    msg = parse_message(ADT_A01)
    j = msg.to_json(indent=2)
    assert isinstance(j, str)
    assert "\n" in j


def test_segment_to_dict():
    msg = parse_message(ADT_A01)
    d = msg.pid.to_dict()
    assert d["_segment_id"] == "PID"
    assert "set_id_pid" in d


def test_segment_to_json():
    msg = parse_message(ADT_A01)
    j = msg.pid.to_json()
    assert isinstance(j, str)
    import json
    parsed = json.loads(j)
    assert parsed["_segment_id"] == "PID"
