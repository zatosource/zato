from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestMFKM01Cardinality:

    def test_mfk_m01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["MFI"] = 1
        result = validate_cardinality("MFK_M01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfk_m01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["MFI"] = 1
        result = validate_cardinality("MFK_M01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfk_m01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["MFI"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFK_M01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM02Cardinality:

    def test_mfn_m02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M02.MF_STAFF"] = 1
        segment_counts["MFE"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("MFN_M02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M02.MF_STAFF"] = 1
        segment_counts["MFE"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("MFN_M02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M02.MF_STAFF"] = 1
        segment_counts["MFE"] = 1
        segment_counts["STF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM04Cardinality:

    def test_mfn_m04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M04.MF_CDM"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CDM"] = 1
        result = validate_cardinality("MFN_M04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M04.MF_CDM"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CDM"] = 1
        result = validate_cardinality("MFN_M04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M04.MF_CDM"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CDM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM05Cardinality:

    def test_mfn_m05_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M05.MF_LOCATION"] = 1
        segment_counts["MFE"] = 1
        segment_counts["LOC"] = 1
        group_counts["MFN_M05.MF_LOC_DEPT"] = 1
        segment_counts["LDP"] = 1
        result = validate_cardinality("MFN_M05", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m05_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M05.MF_LOCATION"] = 1
        segment_counts["MFE"] = 1
        segment_counts["LOC"] = 1
        group_counts["MFN_M05.MF_LOC_DEPT"] = 1
        segment_counts["LDP"] = 1
        result = validate_cardinality("MFN_M05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m05_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M05.MF_LOCATION"] = 1
        segment_counts["MFE"] = 1
        segment_counts["LOC"] = 1
        group_counts["MFN_M05.MF_LOC_DEPT"] = 1
        segment_counts["LDP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM06Cardinality:

    def test_mfn_m06_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M06.MF_CLIN_STUDY"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CM0"] = 1
        segment_counts["CM1"] = 1
        result = validate_cardinality("MFN_M06", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m06_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M06.MF_CLIN_STUDY"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CM0"] = 1
        segment_counts["CM1"] = 1
        result = validate_cardinality("MFN_M06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m06_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M06.MF_CLIN_STUDY"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CM0"] = 1
        segment_counts["CM1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM07Cardinality:

    def test_mfn_m07_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M07.MF_CLIN_STUDY_SCHED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CM0"] = 1
        result = validate_cardinality("MFN_M07", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m07_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M07.MF_CLIN_STUDY_SCHED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CM0"] = 1
        result = validate_cardinality("MFN_M07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m07_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M07.MF_CLIN_STUDY_SCHED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CM0"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM08Cardinality:

    def test_mfn_m08_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M08.MF_TEST_NUMERIC"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        result = validate_cardinality("MFN_M08", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m08_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M08.MF_TEST_NUMERIC"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        result = validate_cardinality("MFN_M08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m08_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M08.MF_TEST_NUMERIC"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM09Cardinality:

    def test_mfn_m09_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M09.MF_TEST_CATEGORICAL"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM3"] = 1
        result = validate_cardinality("MFN_M09", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m09_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M09.MF_TEST_CATEGORICAL"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM3"] = 1
        result = validate_cardinality("MFN_M09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m09_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M09.MF_TEST_CATEGORICAL"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM3"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM10Cardinality:

    def test_mfn_m10_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M10.MF_TEST_BATTERIES"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM5"] = 1
        result = validate_cardinality("MFN_M10", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m10_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M10.MF_TEST_BATTERIES"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM5"] = 1
        result = validate_cardinality("MFN_M10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m10_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M10.MF_TEST_BATTERIES"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM5"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM11Cardinality:

    def test_mfn_m11_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M11.MF_TEST_CALCULATED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM6"] = 1
        segment_counts["OM2"] = 1
        result = validate_cardinality("MFN_M11", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m11_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M11.MF_TEST_CALCULATED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM6"] = 1
        segment_counts["OM2"] = 1
        result = validate_cardinality("MFN_M11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m11_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M11.MF_TEST_CALCULATED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM6"] = 1
        segment_counts["OM2"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM12Cardinality:

    def test_mfn_m12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M12.MF_OBS_ATTRIBUTES"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM7"] = 1
        result = validate_cardinality("MFN_M12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M12.MF_OBS_ATTRIBUTES"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM7"] = 1
        result = validate_cardinality("MFN_M12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M12.MF_OBS_ATTRIBUTES"] = 1
        segment_counts["MFE"] = 1
        segment_counts["OM1"] = 1
        segment_counts["OM7"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM13Cardinality:

    def test_mfn_m13_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        segment_counts["MFE"] = 1
        result = validate_cardinality("MFN_M13", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m13_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        segment_counts["MFE"] = 1
        result = validate_cardinality("MFN_M13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m13_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        segment_counts["MFE"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM15Cardinality:

    def test_mfn_m15_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M15.MF_INV_ITEM"] = 1
        segment_counts["MFE"] = 1
        segment_counts["IIM"] = 1
        result = validate_cardinality("MFN_M15", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m15_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M15.MF_INV_ITEM"] = 1
        segment_counts["MFE"] = 1
        segment_counts["IIM"] = 1
        result = validate_cardinality("MFN_M15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m15_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M15.MF_INV_ITEM"] = 1
        segment_counts["MFE"] = 1
        segment_counts["IIM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM16Cardinality:

    def test_mfn_m16_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M16.MATERIAL_ITEM_RECORD"] = 1
        segment_counts["MFE"] = 1
        segment_counts["ITM"] = 1
        segment_counts["STZ"] = 1
        segment_counts["VND"] = 1
        segment_counts["PKG"] = 1
        segment_counts["IVT"] = 1
        result = validate_cardinality("MFN_M16", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m16_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M16.MATERIAL_ITEM_RECORD"] = 1
        segment_counts["MFE"] = 1
        segment_counts["ITM"] = 1
        segment_counts["STZ"] = 1
        segment_counts["VND"] = 1
        segment_counts["PKG"] = 1
        segment_counts["IVT"] = 1
        result = validate_cardinality("MFN_M16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m16_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M16.MATERIAL_ITEM_RECORD"] = 1
        segment_counts["MFE"] = 1
        segment_counts["ITM"] = 1
        segment_counts["STZ"] = 1
        segment_counts["VND"] = 1
        segment_counts["PKG"] = 1
        segment_counts["IVT"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM17Cardinality:

    def test_mfn_m17_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M17.MF_DRG"] = 1
        segment_counts["MFE"] = 1
        segment_counts["DMI"] = 1
        result = validate_cardinality("MFN_M17", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m17_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M17.MF_DRG"] = 1
        segment_counts["MFE"] = 1
        segment_counts["DMI"] = 1
        result = validate_cardinality("MFN_M17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m17_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M17.MF_DRG"] = 1
        segment_counts["MFE"] = 1
        segment_counts["DMI"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM18Cardinality:

    def test_mfn_m18_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M18.MF_PAYER"] = 1
        segment_counts["MFE"] = 1
        group_counts["MFN_M18.PAYER_MF_ENTRY"] = 1
        segment_counts["PM1"] = 1
        group_counts["MFN_M18.PAYER_MF_COVERAGE"] = 1
        segment_counts["MCP"] = 1
        result = validate_cardinality("MFN_M18", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m18_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M18.MF_PAYER"] = 1
        segment_counts["MFE"] = 1
        group_counts["MFN_M18.PAYER_MF_ENTRY"] = 1
        segment_counts["PM1"] = 1
        group_counts["MFN_M18.PAYER_MF_COVERAGE"] = 1
        segment_counts["MCP"] = 1
        result = validate_cardinality("MFN_M18", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m18_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M18.MF_PAYER"] = 1
        segment_counts["MFE"] = 1
        group_counts["MFN_M18.PAYER_MF_ENTRY"] = 1
        segment_counts["PM1"] = 1
        group_counts["MFN_M18.PAYER_MF_COVERAGE"] = 1
        segment_counts["MCP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M18", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNM19Cardinality:

    def test_mfn_m19_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M19.CONTRACT_RECORD"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CTR"] = 1
        group_counts["MFN_M19.MATERIAL_ITEM_RECORD"] = 1
        segment_counts["ITM"] = 1
        group_counts["MFN_M19.PURCHASING_VENDOR"] = 1
        segment_counts["VND"] = 1
        segment_counts["PKG"] = 1
        result = validate_cardinality("MFN_M19", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_m19_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_M19.CONTRACT_RECORD"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CTR"] = 1
        group_counts["MFN_M19.MATERIAL_ITEM_RECORD"] = 1
        segment_counts["ITM"] = 1
        group_counts["MFN_M19.PURCHASING_VENDOR"] = 1
        segment_counts["VND"] = 1
        segment_counts["PKG"] = 1
        result = validate_cardinality("MFN_M19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_m19_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_M19.CONTRACT_RECORD"] = 1
        segment_counts["MFE"] = 1
        segment_counts["CTR"] = 1
        group_counts["MFN_M19.MATERIAL_ITEM_RECORD"] = 1
        segment_counts["ITM"] = 1
        group_counts["MFN_M19.PURCHASING_VENDOR"] = 1
        segment_counts["VND"] = 1
        segment_counts["PKG"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_M19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMFNZnnCardinality:

    def test_mfn_znn_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_Znn.MF_SITE_DEFINED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["anyHL7Segment"] = 1
        result = validate_cardinality("MFN_Znn", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mfn_znn_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MFI"] = 1
        group_counts["MFN_Znn.MF_SITE_DEFINED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["anyHL7Segment"] = 1
        result = validate_cardinality("MFN_Znn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mfn_znn_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MFI"] = 1
        group_counts["MFN_Znn.MF_SITE_DEFINED"] = 1
        segment_counts["MFE"] = 1
        segment_counts["anyHL7Segment"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MFN_Znn", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
