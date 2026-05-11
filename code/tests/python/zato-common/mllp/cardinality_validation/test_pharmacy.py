from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestRASO17Cardinality:

    def test_ras_o17_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RAS_O17.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RAS_O17.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RAS_O17.ADMINISTRATION"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RAS_O17", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ras_o17_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RAS_O17.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RAS_O17.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RAS_O17.ADMINISTRATION"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RAS_O17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ras_o17_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RAS_O17.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RAS_O17.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RAS_O17.ADMINISTRATION"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RAS_O17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRDEO11Cardinality:

    def test_rde_o11_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["RDE_O11.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDE_O11.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXV"] = 1
        group_counts["RDE_O11.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RDE_O11", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rde_o11_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["RDE_O11.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDE_O11.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXV"] = 1
        group_counts["RDE_O11.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RDE_O11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rde_o11_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["RDE_O11.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDE_O11.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXV"] = 1
        group_counts["RDE_O11.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RDE_O11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRDEO49Cardinality:

    def test_rde_o49_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["RDE_O49.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDE_O49.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RDE_O49", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rde_o49_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["RDE_O49.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDE_O49.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RDE_O49", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rde_o49_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["RDE_O49.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDE_O49.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RDE_O49", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRDSO13Cardinality:

    def test_rds_o13_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RDS_O13.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDS_O13.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RDS_O13", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rds_o13_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RDS_O13.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDS_O13.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RDS_O13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rds_o13_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        group_counts["RDS_O13.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RDS_O13.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RDS_O13", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRGVO15Cardinality:

    def test_rgv_o15_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RGV_O15.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RGV_O15.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RGV_O15.GIVE"] = 1
        segment_counts["RXG"] = 1
        group_counts["RGV_O15.TIMING_GIVE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RGV_O15", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rgv_o15_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RGV_O15.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RGV_O15.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RGV_O15.GIVE"] = 1
        segment_counts["RXG"] = 1
        group_counts["RGV_O15.TIMING_GIVE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("RGV_O15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rgv_o15_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["RGV_O15.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["NTE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["RXE"] = 1
        group_counts["RGV_O15.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        group_counts["RGV_O15.GIVE"] = 1
        segment_counts["RXG"] = 1
        group_counts["RGV_O15.TIMING_GIVE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RGV_O15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRRAO18Cardinality:

    def test_rra_o18_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRA_O18.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["RRA_O18.TREATMENT"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRA_O18", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rra_o18_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRA_O18.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["RRA_O18.TREATMENT"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRA_O18", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rra_o18_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRA_O18.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["RRA_O18.TREATMENT"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RRA_O18", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRRDO14Cardinality:

    def test_rrd_o14_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRD_O14.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRD_O14", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rrd_o14_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRD_O14.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRD_O14", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rrd_o14_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRD_O14.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXD"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RRD_O14", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRREO12Cardinality:

    def test_rre_o12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRE_O12.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        group_counts["RRE_O12.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRE_O12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rre_o12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRE_O12.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        group_counts["RRE_O12.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRE_O12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rre_o12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRE_O12.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        group_counts["RRE_O12.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RRE_O12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRREO50Cardinality:

    def test_rre_o50_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRE_O50.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        group_counts["RRE_O50.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRE_O50", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rre_o50_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRE_O50.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        group_counts["RRE_O50.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRE_O50", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rre_o50_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRE_O50.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXE"] = 1
        group_counts["RRE_O50.TIMING_ENCODED"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RRE_O50", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRRGO16Cardinality:

    def test_rrg_o16_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRG_O16.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXG"] = 1
        group_counts["RRG_O16.TIMING_GIVE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRG_O16", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rrg_o16_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRG_O16.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXG"] = 1
        group_counts["RRG_O16.TIMING_GIVE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("RRG_O16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rrg_o16_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["RRG_O16.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXG"] = 1
        group_counts["RRG_O16.TIMING_GIVE"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RRG_O16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
