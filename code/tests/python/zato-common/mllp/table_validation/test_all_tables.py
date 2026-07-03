from __future__ import annotations

from zato.hl7v2_rs import is_valid_table_value, validate_table_value, get_table_codes


class TestTable0001:
    """Tests for table 0001: AdministrativeSex"""

    def test_get_table_codes_0001(self):
        codes = get_table_codes(1)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0001_f(self):
        assert is_valid_table_value(1, 'F') is True

    def test_valid_code_0001_m(self):
        assert is_valid_table_value(1, 'M') is True

    def test_valid_code_0001_o(self):
        assert is_valid_table_value(1, 'O') is True

    def test_valid_code_0001_u(self):
        assert is_valid_table_value(1, 'U') is True

    def test_valid_code_0001_a(self):
        assert is_valid_table_value(1, 'A') is True

    def test_invalid_code_0001(self):
        assert is_valid_table_value(1, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0001(self):
        result = validate_table_value(1, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0001(self):
        result = validate_table_value(1, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0002:
    """Tests for table 0002: MaritalStatus"""

    def test_get_table_codes_0002(self):
        codes = get_table_codes(2)
        assert codes is not None
        assert len(codes) == 16

    def test_valid_code_0002_a(self):
        assert is_valid_table_value(2, 'A') is True

    def test_valid_code_0002_d(self):
        assert is_valid_table_value(2, 'D') is True

    def test_valid_code_0002_m(self):
        assert is_valid_table_value(2, 'M') is True

    def test_valid_code_0002_s(self):
        assert is_valid_table_value(2, 'S') is True

    def test_valid_code_0002_w(self):
        assert is_valid_table_value(2, 'W') is True

    def test_invalid_code_0002(self):
        assert is_valid_table_value(2, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0002(self):
        result = validate_table_value(2, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0002(self):
        result = validate_table_value(2, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0003:
    """Tests for table 0003: Event"""

    def test_get_table_codes_0003(self):
        codes = get_table_codes(3)
        assert codes is not None
        assert len(codes) == 384

    def test_valid_code_0003_x01(self):
        assert is_valid_table_value(3, 'X01') is True

    def test_valid_code_0003_a01(self):
        assert is_valid_table_value(3, 'A01') is True

    def test_valid_code_0003_a02(self):
        assert is_valid_table_value(3, 'A02') is True

    def test_valid_code_0003_a03(self):
        assert is_valid_table_value(3, 'A03') is True

    def test_valid_code_0003_a04(self):
        assert is_valid_table_value(3, 'A04') is True

    def test_invalid_code_0003(self):
        assert is_valid_table_value(3, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0003(self):
        result = validate_table_value(3, 'X01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0003(self):
        result = validate_table_value(3, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0004:
    """Tests for table 0004: PatientClass"""

    def test_get_table_codes_0004(self):
        codes = get_table_codes(4)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0004_e(self):
        assert is_valid_table_value(4, 'E') is True

    def test_valid_code_0004_i(self):
        assert is_valid_table_value(4, 'I') is True

    def test_valid_code_0004_o(self):
        assert is_valid_table_value(4, 'O') is True

    def test_valid_code_0004_p(self):
        assert is_valid_table_value(4, 'P') is True

    def test_valid_code_0004_r(self):
        assert is_valid_table_value(4, 'R') is True

    def test_invalid_code_0004(self):
        assert is_valid_table_value(4, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0004(self):
        result = validate_table_value(4, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0004(self):
        result = validate_table_value(4, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0006:
    """Tests for table 0006: Religion2"""

    def test_get_table_codes_0006(self):
        codes = get_table_codes(6)
        assert codes is not None
        assert len(codes) == 95

    def test_valid_code_0006_a(self):
        assert is_valid_table_value(6, 'A') is True

    def test_valid_code_0006_b(self):
        assert is_valid_table_value(6, 'B') is True

    def test_valid_code_0006_c(self):
        assert is_valid_table_value(6, 'C') is True

    def test_valid_code_0006_e(self):
        assert is_valid_table_value(6, 'E') is True

    def test_valid_code_0006_j(self):
        assert is_valid_table_value(6, 'J') is True

    def test_invalid_code_0006(self):
        assert is_valid_table_value(6, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0006(self):
        result = validate_table_value(6, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0006(self):
        result = validate_table_value(6, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0007:
    """Tests for table 0007: AdmissionType"""

    def test_get_table_codes_0007(self):
        codes = get_table_codes(7)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0007_a(self):
        assert is_valid_table_value(7, 'A') is True

    def test_valid_code_0007_e(self):
        assert is_valid_table_value(7, 'E') is True

    def test_valid_code_0007_l(self):
        assert is_valid_table_value(7, 'L') is True

    def test_valid_code_0007_r(self):
        assert is_valid_table_value(7, 'R') is True

    def test_valid_code_0007_n(self):
        assert is_valid_table_value(7, 'N') is True

    def test_invalid_code_0007(self):
        assert is_valid_table_value(7, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0007(self):
        result = validate_table_value(7, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0007(self):
        result = validate_table_value(7, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0008:
    """Tests for table 0008: AcknowledgmentCodes"""

    def test_get_table_codes_0008(self):
        codes = get_table_codes(8)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0008_aa(self):
        assert is_valid_table_value(8, 'AA') is True

    def test_valid_code_0008_ae(self):
        assert is_valid_table_value(8, 'AE') is True

    def test_valid_code_0008_ar(self):
        assert is_valid_table_value(8, 'AR') is True

    def test_valid_code_0008_ca(self):
        assert is_valid_table_value(8, 'CA') is True

    def test_valid_code_0008_ce(self):
        assert is_valid_table_value(8, 'CE') is True

    def test_invalid_code_0008(self):
        assert is_valid_table_value(8, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0008(self):
        result = validate_table_value(8, 'AA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0008(self):
        result = validate_table_value(8, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0009:
    """Tests for table 0009: AmbulatoryStatus"""

    def test_get_table_codes_0009(self):
        codes = get_table_codes(9)
        assert codes is not None
        assert len(codes) == 16

    def test_valid_code_0009_a0(self):
        assert is_valid_table_value(9, 'A0') is True

    def test_valid_code_0009_a1(self):
        assert is_valid_table_value(9, 'A1') is True

    def test_valid_code_0009_a2(self):
        assert is_valid_table_value(9, 'A2') is True

    def test_valid_code_0009_a3(self):
        assert is_valid_table_value(9, 'A3') is True

    def test_valid_code_0009_a4(self):
        assert is_valid_table_value(9, 'A4') is True

    def test_invalid_code_0009(self):
        assert is_valid_table_value(9, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0009(self):
        result = validate_table_value(9, 'A0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0009(self):
        result = validate_table_value(9, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0012:
    """Tests for table 0012: StockLocation"""

    def test_get_table_codes_0012(self):
        codes = get_table_codes(12)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0012_an(self):
        assert is_valid_table_value(12, 'AN') is True

    def test_valid_code_0012_fl(self):
        assert is_valid_table_value(12, 'FL') is True

    def test_invalid_code_0012(self):
        assert is_valid_table_value(12, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0012(self):
        result = validate_table_value(12, 'AN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0012(self):
        result = validate_table_value(12, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0017:
    """Tests for table 0017: TransactionType"""

    def test_get_table_codes_0017(self):
        codes = get_table_codes(17)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0017_cg(self):
        assert is_valid_table_value(17, 'CG') is True

    def test_valid_code_0017_cd(self):
        assert is_valid_table_value(17, 'CD') is True

    def test_valid_code_0017_py(self):
        assert is_valid_table_value(17, 'PY') is True

    def test_valid_code_0017_aj(self):
        assert is_valid_table_value(17, 'AJ') is True

    def test_valid_code_0017_co(self):
        assert is_valid_table_value(17, 'CO') is True

    def test_invalid_code_0017(self):
        assert is_valid_table_value(17, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0017(self):
        result = validate_table_value(17, 'CG', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0017(self):
        result = validate_table_value(17, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0027:
    """Tests for table 0027: Priority"""

    def test_get_table_codes_0027(self):
        codes = get_table_codes(27)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0027_s(self):
        assert is_valid_table_value(27, 'S') is True

    def test_valid_code_0027_a(self):
        assert is_valid_table_value(27, 'A') is True

    def test_valid_code_0027_r(self):
        assert is_valid_table_value(27, 'R') is True

    def test_valid_code_0027_p(self):
        assert is_valid_table_value(27, 'P') is True

    def test_valid_code_0027_t(self):
        assert is_valid_table_value(27, 'T') is True

    def test_invalid_code_0027(self):
        assert is_valid_table_value(27, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0027(self):
        result = validate_table_value(27, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0027(self):
        result = validate_table_value(27, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0033:
    """Tests for table 0033: Route"""

    def test_get_table_codes_0033(self):
        codes = get_table_codes(33)
        assert codes is not None
        assert len(codes) == 28

    def test_valid_code_0033_ap(self):
        assert is_valid_table_value(33, 'AP') is True

    def test_valid_code_0033_ch(self):
        assert is_valid_table_value(33, 'CH') is True

    def test_valid_code_0033_du(self):
        assert is_valid_table_value(33, 'DU') is True

    def test_valid_code_0033_ea(self):
        assert is_valid_table_value(33, 'EA') is True

    def test_valid_code_0033_ey(self):
        assert is_valid_table_value(33, 'EY') is True

    def test_invalid_code_0033(self):
        assert is_valid_table_value(33, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0033(self):
        result = validate_table_value(33, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0033(self):
        result = validate_table_value(33, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0034:
    """Tests for table 0034: SiteAdministered"""

    def test_get_table_codes_0034(self):
        codes = get_table_codes(34)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0034_b(self):
        assert is_valid_table_value(34, 'B') is True

    def test_valid_code_0034_l(self):
        assert is_valid_table_value(34, 'L') is True

    def test_invalid_code_0034(self):
        assert is_valid_table_value(34, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0034(self):
        result = validate_table_value(34, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0034(self):
        result = validate_table_value(34, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0038:
    """Tests for table 0038: OrderStatus"""

    def test_get_table_codes_0038(self):
        codes = get_table_codes(38)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0038_a(self):
        assert is_valid_table_value(38, 'A') is True

    def test_valid_code_0038_ca(self):
        assert is_valid_table_value(38, 'CA') is True

    def test_valid_code_0038_cm(self):
        assert is_valid_table_value(38, 'CM') is True

    def test_valid_code_0038_dc(self):
        assert is_valid_table_value(38, 'DC') is True

    def test_valid_code_0038_er(self):
        assert is_valid_table_value(38, 'ER') is True

    def test_invalid_code_0038(self):
        assert is_valid_table_value(38, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0038(self):
        result = validate_table_value(38, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0038(self):
        result = validate_table_value(38, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0048:
    """Tests for table 0048: WhatSubjectFilter"""

    def test_get_table_codes_0048(self):
        codes = get_table_codes(48)
        assert codes is not None
        assert len(codes) == 38

    def test_valid_code_0048_adv(self):
        assert is_valid_table_value(48, 'ADV') is True

    def test_valid_code_0048_anu(self):
        assert is_valid_table_value(48, 'ANU') is True

    def test_valid_code_0048_apn(self):
        assert is_valid_table_value(48, 'APN') is True

    def test_valid_code_0048_app(self):
        assert is_valid_table_value(48, 'APP') is True

    def test_valid_code_0048_arn(self):
        assert is_valid_table_value(48, 'ARN') is True

    def test_invalid_code_0048(self):
        assert is_valid_table_value(48, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0048(self):
        result = validate_table_value(48, 'ADV', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0048(self):
        result = validate_table_value(48, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0052:
    """Tests for table 0052: DiagnosisType"""

    def test_get_table_codes_0052(self):
        codes = get_table_codes(52)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0052_a(self):
        assert is_valid_table_value(52, 'A') is True

    def test_valid_code_0052_w(self):
        assert is_valid_table_value(52, 'W') is True

    def test_valid_code_0052_f(self):
        assert is_valid_table_value(52, 'F') is True

    def test_invalid_code_0052(self):
        assert is_valid_table_value(52, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0052(self):
        result = validate_table_value(52, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0052(self):
        result = validate_table_value(52, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0061:
    """Tests for table 0061: CheckDigitScheme"""

    def test_get_table_codes_0061(self):
        codes = get_table_codes(61)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0061_bcv(self):
        assert is_valid_table_value(61, 'BCV') is True

    def test_valid_code_0061_npi(self):
        assert is_valid_table_value(61, 'NPI') is True

    def test_valid_code_0061_iso(self):
        assert is_valid_table_value(61, 'ISO') is True

    def test_valid_code_0061_m10(self):
        assert is_valid_table_value(61, 'M10') is True

    def test_valid_code_0061_m11(self):
        assert is_valid_table_value(61, 'M11') is True

    def test_invalid_code_0061(self):
        assert is_valid_table_value(61, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0061(self):
        result = validate_table_value(61, 'BCV', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0061(self):
        result = validate_table_value(61, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0062:
    """Tests for table 0062: EventReason"""

    def test_get_table_codes_0062(self):
        codes = get_table_codes(62)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0062_c_01(self):
        assert is_valid_table_value(62, '01') is True

    def test_valid_code_0062_c_02(self):
        assert is_valid_table_value(62, '02') is True

    def test_valid_code_0062_c_03(self):
        assert is_valid_table_value(62, '03') is True

    def test_valid_code_0062_o(self):
        assert is_valid_table_value(62, 'O') is True

    def test_valid_code_0062_u(self):
        assert is_valid_table_value(62, 'U') is True

    def test_invalid_code_0062(self):
        assert is_valid_table_value(62, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0062(self):
        result = validate_table_value(62, '01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0062(self):
        result = validate_table_value(62, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0063:
    """Tests for table 0063: Relationship"""

    def test_get_table_codes_0063(self):
        codes = get_table_codes(63)
        assert codes is not None
        assert len(codes) == 32

    def test_valid_code_0063_sel(self):
        assert is_valid_table_value(63, 'SEL') is True

    def test_valid_code_0063_spo(self):
        assert is_valid_table_value(63, 'SPO') is True

    def test_valid_code_0063_dom(self):
        assert is_valid_table_value(63, 'DOM') is True

    def test_valid_code_0063_chd(self):
        assert is_valid_table_value(63, 'CHD') is True

    def test_valid_code_0063_gch(self):
        assert is_valid_table_value(63, 'GCH') is True

    def test_invalid_code_0063(self):
        assert is_valid_table_value(63, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0063(self):
        result = validate_table_value(63, 'SEL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0063(self):
        result = validate_table_value(63, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0065:
    """Tests for table 0065: SpecimenAction"""

    def test_get_table_codes_0065(self):
        codes = get_table_codes(65)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0065_c(self):
        assert is_valid_table_value(65, 'C') is True

    def test_valid_code_0065_a(self):
        assert is_valid_table_value(65, 'A') is True

    def test_valid_code_0065_g(self):
        assert is_valid_table_value(65, 'G') is True

    def test_valid_code_0065_l(self):
        assert is_valid_table_value(65, 'L') is True

    def test_valid_code_0065_o(self):
        assert is_valid_table_value(65, 'O') is True

    def test_invalid_code_0065(self):
        assert is_valid_table_value(65, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0065(self):
        result = validate_table_value(65, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0065(self):
        result = validate_table_value(65, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0066:
    """Tests for table 0066: EmploymentStatus"""

    def test_get_table_codes_0066(self):
        codes = get_table_codes(66)
        assert codes is not None
        assert len(codes) == 15

    def test_valid_code_0066_c_1(self):
        assert is_valid_table_value(66, '1') is True

    def test_valid_code_0066_f(self):
        assert is_valid_table_value(66, 'F') is True

    def test_valid_code_0066_empty(self):
        assert is_valid_table_value(66, '...') is True

    def test_valid_code_0066_c_2(self):
        assert is_valid_table_value(66, '2') is True

    def test_valid_code_0066_p(self):
        assert is_valid_table_value(66, 'P') is True

    def test_invalid_code_0066(self):
        assert is_valid_table_value(66, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0066(self):
        result = validate_table_value(66, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0066(self):
        result = validate_table_value(66, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0069:
    """Tests for table 0069: HospitalService"""

    def test_get_table_codes_0069(self):
        codes = get_table_codes(69)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0069_med(self):
        assert is_valid_table_value(69, 'MED') is True

    def test_valid_code_0069_sur(self):
        assert is_valid_table_value(69, 'SUR') is True

    def test_valid_code_0069_uro(self):
        assert is_valid_table_value(69, 'URO') is True

    def test_valid_code_0069_pul(self):
        assert is_valid_table_value(69, 'PUL') is True

    def test_valid_code_0069_car(self):
        assert is_valid_table_value(69, 'CAR') is True

    def test_invalid_code_0069(self):
        assert is_valid_table_value(69, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0069(self):
        result = validate_table_value(69, 'MED', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0069(self):
        result = validate_table_value(69, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0070:
    """Tests for table 0070: SpecimenSourceCodes"""

    def test_get_table_codes_0070(self):
        codes = get_table_codes(70)
        assert codes is not None
        assert len(codes) == 137

    def test_valid_code_0070_mn(self):
        assert is_valid_table_value(70, 'MN') is True

    def test_valid_code_0070_oth(self):
        assert is_valid_table_value(70, 'OTH') is True

    def test_valid_code_0070_tis(self):
        assert is_valid_table_value(70, 'TIS') is True

    def test_valid_code_0070_abs(self):
        assert is_valid_table_value(70, 'ABS') is True

    def test_valid_code_0070_amn(self):
        assert is_valid_table_value(70, 'AMN') is True

    def test_invalid_code_0070(self):
        assert is_valid_table_value(70, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0070(self):
        result = validate_table_value(70, 'MN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0070(self):
        result = validate_table_value(70, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0074:
    """Tests for table 0074: DiagnosticServiceSectionId"""

    def test_get_table_codes_0074(self):
        codes = get_table_codes(74)
        assert codes is not None
        assert len(codes) == 45

    def test_valid_code_0074_au(self):
        assert is_valid_table_value(74, 'AU') is True

    def test_valid_code_0074_bg(self):
        assert is_valid_table_value(74, 'BG') is True

    def test_valid_code_0074_blb(self):
        assert is_valid_table_value(74, 'BLB') is True

    def test_valid_code_0074_cg(self):
        assert is_valid_table_value(74, 'CG') is True

    def test_valid_code_0074_cus(self):
        assert is_valid_table_value(74, 'CUS') is True

    def test_invalid_code_0074(self):
        assert is_valid_table_value(74, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0074(self):
        result = validate_table_value(74, 'AU', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0074(self):
        result = validate_table_value(74, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0076:
    """Tests for table 0076: MessageType"""

    def test_get_table_codes_0076(self):
        codes = get_table_codes(76)
        assert codes is not None
        assert len(codes) == 159

    def test_valid_code_0076_ack(self):
        assert is_valid_table_value(76, 'ACK') is True

    def test_valid_code_0076_adr(self):
        assert is_valid_table_value(76, 'ADR') is True

    def test_valid_code_0076_ard(self):
        assert is_valid_table_value(76, 'ARD') is True

    def test_valid_code_0076_adt(self):
        assert is_valid_table_value(76, 'ADT') is True

    def test_valid_code_0076_bar(self):
        assert is_valid_table_value(76, 'BAR') is True

    def test_invalid_code_0076(self):
        assert is_valid_table_value(76, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0076(self):
        result = validate_table_value(76, 'ACK', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0076(self):
        result = validate_table_value(76, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0080:
    """Tests for table 0080: NatureOfAbnormalTesting"""

    def test_get_table_codes_0080(self):
        codes = get_table_codes(80)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0080_a(self):
        assert is_valid_table_value(80, 'A') is True

    def test_valid_code_0080_n(self):
        assert is_valid_table_value(80, 'N') is True

    def test_valid_code_0080_r(self):
        assert is_valid_table_value(80, 'R') is True

    def test_valid_code_0080_s(self):
        assert is_valid_table_value(80, 'S') is True

    def test_valid_code_0080_sp(self):
        assert is_valid_table_value(80, 'SP') is True

    def test_invalid_code_0080(self):
        assert is_valid_table_value(80, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0080(self):
        result = validate_table_value(80, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0080(self):
        result = validate_table_value(80, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0083:
    """Tests for table 0083: OutlierType"""

    def test_get_table_codes_0083(self):
        codes = get_table_codes(83)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0083_d(self):
        assert is_valid_table_value(83, 'D') is True

    def test_valid_code_0083_c(self):
        assert is_valid_table_value(83, 'C') is True

    def test_invalid_code_0083(self):
        assert is_valid_table_value(83, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0083(self):
        result = validate_table_value(83, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0083(self):
        result = validate_table_value(83, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0085:
    """Tests for table 0085: ObservationResultStatusCodesInterpretation"""

    def test_get_table_codes_0085(self):
        codes = get_table_codes(85)
        assert codes is not None
        assert len(codes) == 15

    def test_valid_code_0085_a(self):
        assert is_valid_table_value(85, 'A') is True

    def test_valid_code_0085_b(self):
        assert is_valid_table_value(85, 'B') is True

    def test_valid_code_0085_c(self):
        assert is_valid_table_value(85, 'C') is True

    def test_valid_code_0085_d(self):
        assert is_valid_table_value(85, 'D') is True

    def test_valid_code_0085_f(self):
        assert is_valid_table_value(85, 'F') is True

    def test_invalid_code_0085(self):
        assert is_valid_table_value(85, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0085(self):
        result = validate_table_value(85, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0085(self):
        result = validate_table_value(85, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0091:
    """Tests for table 0091: QueryPriority"""

    def test_get_table_codes_0091(self):
        codes = get_table_codes(91)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0091_d(self):
        assert is_valid_table_value(91, 'D') is True

    def test_valid_code_0091_i(self):
        assert is_valid_table_value(91, 'I') is True

    def test_invalid_code_0091(self):
        assert is_valid_table_value(91, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0091(self):
        result = validate_table_value(91, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0091(self):
        result = validate_table_value(91, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0092:
    """Tests for table 0092: ReAdmissionIndicator"""

    def test_get_table_codes_0092(self):
        codes = get_table_codes(92)
        assert codes is not None
        assert len(codes) == 1

    def test_valid_code_0092_r(self):
        assert is_valid_table_value(92, 'R') is True

    def test_invalid_code_0092(self):
        assert is_valid_table_value(92, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0092(self):
        result = validate_table_value(92, 'R', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0092(self):
        result = validate_table_value(92, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0098:
    """Tests for table 0098: TypeOfAgreement"""

    def test_get_table_codes_0098(self):
        codes = get_table_codes(98)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0098_s(self):
        assert is_valid_table_value(98, 'S') is True

    def test_valid_code_0098_u(self):
        assert is_valid_table_value(98, 'U') is True

    def test_valid_code_0098_m(self):
        assert is_valid_table_value(98, 'M') is True

    def test_invalid_code_0098(self):
        assert is_valid_table_value(98, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0098(self):
        result = validate_table_value(98, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0098(self):
        result = validate_table_value(98, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0100:
    """Tests for table 0100: InvocationEvent"""

    def test_get_table_codes_0100(self):
        codes = get_table_codes(100)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0100_d(self):
        assert is_valid_table_value(100, 'D') is True

    def test_valid_code_0100_o(self):
        assert is_valid_table_value(100, 'O') is True

    def test_valid_code_0100_r(self):
        assert is_valid_table_value(100, 'R') is True

    def test_valid_code_0100_s(self):
        assert is_valid_table_value(100, 'S') is True

    def test_valid_code_0100_t(self):
        assert is_valid_table_value(100, 'T') is True

    def test_invalid_code_0100(self):
        assert is_valid_table_value(100, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0100(self):
        result = validate_table_value(100, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0100(self):
        result = validate_table_value(100, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0102:
    """Tests for table 0102: DelayedAcknowledgmentType"""

    def test_get_table_codes_0102(self):
        codes = get_table_codes(102)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0102_d(self):
        assert is_valid_table_value(102, 'D') is True

    def test_valid_code_0102_f(self):
        assert is_valid_table_value(102, 'F') is True

    def test_invalid_code_0102(self):
        assert is_valid_table_value(102, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0102(self):
        result = validate_table_value(102, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0102(self):
        result = validate_table_value(102, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0103:
    """Tests for table 0103: ProcessingId"""

    def test_get_table_codes_0103(self):
        codes = get_table_codes(103)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0103_d(self):
        assert is_valid_table_value(103, 'D') is True

    def test_valid_code_0103_p(self):
        assert is_valid_table_value(103, 'P') is True

    def test_valid_code_0103_t(self):
        assert is_valid_table_value(103, 'T') is True

    def test_valid_code_0103_n(self):
        assert is_valid_table_value(103, 'N') is True

    def test_valid_code_0103_v(self):
        assert is_valid_table_value(103, 'V') is True

    def test_invalid_code_0103(self):
        assert is_valid_table_value(103, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0103(self):
        result = validate_table_value(103, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0103(self):
        result = validate_table_value(103, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0104:
    """Tests for table 0104: VersionId"""

    def test_get_table_codes_0104(self):
        codes = get_table_codes(104)
        assert codes is not None
        assert len(codes) == 17

    def test_valid_code_0104_c_2_0(self):
        assert is_valid_table_value(104, '2.0') is True

    def test_valid_code_0104_c_2_0d(self):
        assert is_valid_table_value(104, '2.0D') is True

    def test_valid_code_0104_c_2_1(self):
        assert is_valid_table_value(104, '2.1') is True

    def test_valid_code_0104_c_2_2(self):
        assert is_valid_table_value(104, '2.2') is True

    def test_valid_code_0104_c_2_3(self):
        assert is_valid_table_value(104, '2.3') is True

    def test_invalid_code_0104(self):
        assert is_valid_table_value(104, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0104(self):
        result = validate_table_value(104, '2.0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0104(self):
        result = validate_table_value(104, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0105:
    """Tests for table 0105: SourceOfComment"""

    def test_get_table_codes_0105(self):
        codes = get_table_codes(105)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0105_l(self):
        assert is_valid_table_value(105, 'L') is True

    def test_valid_code_0105_p(self):
        assert is_valid_table_value(105, 'P') is True

    def test_valid_code_0105_o(self):
        assert is_valid_table_value(105, 'O') is True

    def test_invalid_code_0105(self):
        assert is_valid_table_value(105, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0105(self):
        result = validate_table_value(105, 'L', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0105(self):
        result = validate_table_value(105, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0106:
    """Tests for table 0106: QueryResponseFormat"""

    def test_get_table_codes_0106(self):
        codes = get_table_codes(106)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0106_d(self):
        assert is_valid_table_value(106, 'D') is True

    def test_valid_code_0106_r(self):
        assert is_valid_table_value(106, 'R') is True

    def test_valid_code_0106_t(self):
        assert is_valid_table_value(106, 'T') is True

    def test_invalid_code_0106(self):
        assert is_valid_table_value(106, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0106(self):
        result = validate_table_value(106, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0106(self):
        result = validate_table_value(106, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0107:
    """Tests for table 0107: DeferredResponseType"""

    def test_get_table_codes_0107(self):
        codes = get_table_codes(107)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0107_b(self):
        assert is_valid_table_value(107, 'B') is True

    def test_valid_code_0107_l(self):
        assert is_valid_table_value(107, 'L') is True

    def test_invalid_code_0107(self):
        assert is_valid_table_value(107, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0107(self):
        result = validate_table_value(107, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0107(self):
        result = validate_table_value(107, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0108:
    """Tests for table 0108: QueryResultsLevel"""

    def test_get_table_codes_0108(self):
        codes = get_table_codes(108)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0108_o(self):
        assert is_valid_table_value(108, 'O') is True

    def test_valid_code_0108_r(self):
        assert is_valid_table_value(108, 'R') is True

    def test_valid_code_0108_s(self):
        assert is_valid_table_value(108, 'S') is True

    def test_valid_code_0108_t(self):
        assert is_valid_table_value(108, 'T') is True

    def test_invalid_code_0108(self):
        assert is_valid_table_value(108, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0108(self):
        result = validate_table_value(108, 'O', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0108(self):
        result = validate_table_value(108, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0109:
    """Tests for table 0109: ReportPriority"""

    def test_get_table_codes_0109(self):
        codes = get_table_codes(109)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0109_r(self):
        assert is_valid_table_value(109, 'R') is True

    def test_valid_code_0109_s(self):
        assert is_valid_table_value(109, 'S') is True

    def test_invalid_code_0109(self):
        assert is_valid_table_value(109, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0109(self):
        result = validate_table_value(109, 'R', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0109(self):
        result = validate_table_value(109, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0116:
    """Tests for table 0116: BedStatus"""

    def test_get_table_codes_0116(self):
        codes = get_table_codes(116)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0116_c(self):
        assert is_valid_table_value(116, 'C') is True

    def test_valid_code_0116_h(self):
        assert is_valid_table_value(116, 'H') is True

    def test_valid_code_0116_o(self):
        assert is_valid_table_value(116, 'O') is True

    def test_valid_code_0116_u(self):
        assert is_valid_table_value(116, 'U') is True

    def test_valid_code_0116_k(self):
        assert is_valid_table_value(116, 'K') is True

    def test_invalid_code_0116(self):
        assert is_valid_table_value(116, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0116(self):
        result = validate_table_value(116, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0116(self):
        result = validate_table_value(116, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0119:
    """Tests for table 0119: OrderControlCodes"""

    def test_get_table_codes_0119(self):
        codes = get_table_codes(119)
        assert codes is not None
        assert len(codes) == 58

    def test_valid_code_0119_af(self):
        assert is_valid_table_value(119, 'AF') is True

    def test_valid_code_0119_ca(self):
        assert is_valid_table_value(119, 'CA') is True

    def test_valid_code_0119_ch(self):
        assert is_valid_table_value(119, 'CH') is True

    def test_valid_code_0119_cn(self):
        assert is_valid_table_value(119, 'CN') is True

    def test_valid_code_0119_cp(self):
        assert is_valid_table_value(119, 'CP') is True

    def test_invalid_code_0119(self):
        assert is_valid_table_value(119, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0119(self):
        result = validate_table_value(119, 'AF', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0119(self):
        result = validate_table_value(119, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0121:
    """Tests for table 0121: ResponseFlag"""

    def test_get_table_codes_0121(self):
        codes = get_table_codes(121)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0121_e(self):
        assert is_valid_table_value(121, 'E') is True

    def test_valid_code_0121_r(self):
        assert is_valid_table_value(121, 'R') is True

    def test_valid_code_0121_d(self):
        assert is_valid_table_value(121, 'D') is True

    def test_valid_code_0121_f(self):
        assert is_valid_table_value(121, 'F') is True

    def test_valid_code_0121_n(self):
        assert is_valid_table_value(121, 'N') is True

    def test_invalid_code_0121(self):
        assert is_valid_table_value(121, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0121(self):
        result = validate_table_value(121, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0121(self):
        result = validate_table_value(121, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0122:
    """Tests for table 0122: ChargeType"""

    def test_get_table_codes_0122(self):
        codes = get_table_codes(122)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0122_ch(self):
        assert is_valid_table_value(122, 'CH') is True

    def test_valid_code_0122_co(self):
        assert is_valid_table_value(122, 'CO') is True

    def test_valid_code_0122_cr(self):
        assert is_valid_table_value(122, 'CR') is True

    def test_valid_code_0122_dp(self):
        assert is_valid_table_value(122, 'DP') is True

    def test_valid_code_0122_gr(self):
        assert is_valid_table_value(122, 'GR') is True

    def test_invalid_code_0122(self):
        assert is_valid_table_value(122, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0122(self):
        result = validate_table_value(122, 'CH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0122(self):
        result = validate_table_value(122, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0123:
    """Tests for table 0123: ResultStatus"""

    def test_get_table_codes_0123(self):
        codes = get_table_codes(123)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0123_o(self):
        assert is_valid_table_value(123, 'O') is True

    def test_valid_code_0123_i(self):
        assert is_valid_table_value(123, 'I') is True

    def test_valid_code_0123_s(self):
        assert is_valid_table_value(123, 'S') is True

    def test_valid_code_0123_a(self):
        assert is_valid_table_value(123, 'A') is True

    def test_valid_code_0123_p(self):
        assert is_valid_table_value(123, 'P') is True

    def test_invalid_code_0123(self):
        assert is_valid_table_value(123, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0123(self):
        result = validate_table_value(123, 'O', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0123(self):
        result = validate_table_value(123, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0124:
    """Tests for table 0124: TransportationMode"""

    def test_get_table_codes_0124(self):
        codes = get_table_codes(124)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0124_cart(self):
        assert is_valid_table_value(124, 'CART') is True

    def test_valid_code_0124_port(self):
        assert is_valid_table_value(124, 'PORT') is True

    def test_valid_code_0124_walk(self):
        assert is_valid_table_value(124, 'WALK') is True

    def test_valid_code_0124_whlc(self):
        assert is_valid_table_value(124, 'WHLC') is True

    def test_invalid_code_0124(self):
        assert is_valid_table_value(124, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0124(self):
        result = validate_table_value(124, 'CART', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0124(self):
        result = validate_table_value(124, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0126:
    """Tests for table 0126: QuantityLimitedRequest"""

    def test_get_table_codes_0126(self):
        codes = get_table_codes(126)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0126_ch(self):
        assert is_valid_table_value(126, 'CH') is True

    def test_valid_code_0126_li(self):
        assert is_valid_table_value(126, 'LI') is True

    def test_valid_code_0126_pg(self):
        assert is_valid_table_value(126, 'PG') is True

    def test_valid_code_0126_rd(self):
        assert is_valid_table_value(126, 'RD') is True

    def test_valid_code_0126_zo(self):
        assert is_valid_table_value(126, 'ZO') is True

    def test_invalid_code_0126(self):
        assert is_valid_table_value(126, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0126(self):
        result = validate_table_value(126, 'CH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0126(self):
        result = validate_table_value(126, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0127:
    """Tests for table 0127: AllergenType"""

    def test_get_table_codes_0127(self):
        codes = get_table_codes(127)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0127_da(self):
        assert is_valid_table_value(127, 'DA') is True

    def test_valid_code_0127_fa(self):
        assert is_valid_table_value(127, 'FA') is True

    def test_valid_code_0127_ma(self):
        assert is_valid_table_value(127, 'MA') is True

    def test_valid_code_0127_mc(self):
        assert is_valid_table_value(127, 'MC') is True

    def test_valid_code_0127_ea(self):
        assert is_valid_table_value(127, 'EA') is True

    def test_invalid_code_0127(self):
        assert is_valid_table_value(127, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0127(self):
        result = validate_table_value(127, 'DA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0127(self):
        result = validate_table_value(127, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0128:
    """Tests for table 0128: AllergySeverity"""

    def test_get_table_codes_0128(self):
        codes = get_table_codes(128)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0128_sv(self):
        assert is_valid_table_value(128, 'SV') is True

    def test_valid_code_0128_mo(self):
        assert is_valid_table_value(128, 'MO') is True

    def test_valid_code_0128_mi(self):
        assert is_valid_table_value(128, 'MI') is True

    def test_valid_code_0128_u(self):
        assert is_valid_table_value(128, 'U') is True

    def test_invalid_code_0128(self):
        assert is_valid_table_value(128, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0128(self):
        result = validate_table_value(128, 'SV', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0128(self):
        result = validate_table_value(128, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0130:
    """Tests for table 0130: VisitUserCodes"""

    def test_get_table_codes_0130(self):
        codes = get_table_codes(130)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0130_te(self):
        assert is_valid_table_value(130, 'TE') is True

    def test_valid_code_0130_ho(self):
        assert is_valid_table_value(130, 'HO') is True

    def test_valid_code_0130_mo(self):
        assert is_valid_table_value(130, 'MO') is True

    def test_valid_code_0130_ph(self):
        assert is_valid_table_value(130, 'PH') is True

    def test_invalid_code_0130(self):
        assert is_valid_table_value(130, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0130(self):
        result = validate_table_value(130, 'TE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0130(self):
        result = validate_table_value(130, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0131:
    """Tests for table 0131: ContactRole2"""

    def test_get_table_codes_0131(self):
        codes = get_table_codes(131)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0131_bp(self):
        assert is_valid_table_value(131, 'BP') is True

    def test_valid_code_0131_cp(self):
        assert is_valid_table_value(131, 'CP') is True

    def test_valid_code_0131_ep(self):
        assert is_valid_table_value(131, 'EP') is True

    def test_valid_code_0131_pr(self):
        assert is_valid_table_value(131, 'PR') is True

    def test_valid_code_0131_e(self):
        assert is_valid_table_value(131, 'E') is True

    def test_invalid_code_0131(self):
        assert is_valid_table_value(131, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0131(self):
        result = validate_table_value(131, 'BP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0131(self):
        result = validate_table_value(131, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0133:
    """Tests for table 0133: ProcedurePractitionerIdentifierCodeType"""

    def test_get_table_codes_0133(self):
        codes = get_table_codes(133)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0133_an(self):
        assert is_valid_table_value(133, 'AN') is True

    def test_valid_code_0133_pr(self):
        assert is_valid_table_value(133, 'PR') is True

    def test_valid_code_0133_rd(self):
        assert is_valid_table_value(133, 'RD') is True

    def test_valid_code_0133_rs(self):
        assert is_valid_table_value(133, 'RS') is True

    def test_valid_code_0133_np(self):
        assert is_valid_table_value(133, 'NP') is True

    def test_invalid_code_0133(self):
        assert is_valid_table_value(133, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0133(self):
        result = validate_table_value(133, 'AN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0133(self):
        result = validate_table_value(133, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0135:
    """Tests for table 0135: AssignmentOfBenefits"""

    def test_get_table_codes_0135(self):
        codes = get_table_codes(135)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0135_y(self):
        assert is_valid_table_value(135, 'Y') is True

    def test_valid_code_0135_n(self):
        assert is_valid_table_value(135, 'N') is True

    def test_valid_code_0135_m(self):
        assert is_valid_table_value(135, 'M') is True

    def test_invalid_code_0135(self):
        assert is_valid_table_value(135, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0135(self):
        result = validate_table_value(135, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0135(self):
        result = validate_table_value(135, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0137:
    """Tests for table 0137: MailClaimParty"""

    def test_get_table_codes_0137(self):
        codes = get_table_codes(137)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0137_e(self):
        assert is_valid_table_value(137, 'E') is True

    def test_valid_code_0137_g(self):
        assert is_valid_table_value(137, 'G') is True

    def test_valid_code_0137_i(self):
        assert is_valid_table_value(137, 'I') is True

    def test_valid_code_0137_o(self):
        assert is_valid_table_value(137, 'O') is True

    def test_valid_code_0137_p(self):
        assert is_valid_table_value(137, 'P') is True

    def test_invalid_code_0137(self):
        assert is_valid_table_value(137, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0137(self):
        result = validate_table_value(137, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0137(self):
        result = validate_table_value(137, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0140:
    """Tests for table 0140: MilitaryService"""

    def test_get_table_codes_0140(self):
        codes = get_table_codes(140)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0140_usa(self):
        assert is_valid_table_value(140, 'USA') is True

    def test_valid_code_0140_usn(self):
        assert is_valid_table_value(140, 'USN') is True

    def test_valid_code_0140_usaf(self):
        assert is_valid_table_value(140, 'USAF') is True

    def test_valid_code_0140_usmc(self):
        assert is_valid_table_value(140, 'USMC') is True

    def test_valid_code_0140_uscg(self):
        assert is_valid_table_value(140, 'USCG') is True

    def test_invalid_code_0140(self):
        assert is_valid_table_value(140, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0140(self):
        result = validate_table_value(140, 'USA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0140(self):
        result = validate_table_value(140, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0142:
    """Tests for table 0142: MilitaryStatus"""

    def test_get_table_codes_0142(self):
        codes = get_table_codes(142)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0142_act(self):
        assert is_valid_table_value(142, 'ACT') is True

    def test_valid_code_0142_ret(self):
        assert is_valid_table_value(142, 'RET') is True

    def test_valid_code_0142_dec(self):
        assert is_valid_table_value(142, 'DEC') is True

    def test_invalid_code_0142(self):
        assert is_valid_table_value(142, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0142(self):
        result = validate_table_value(142, 'ACT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0142(self):
        result = validate_table_value(142, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0144:
    """Tests for table 0144: EligibilitySource"""

    def test_get_table_codes_0144(self):
        codes = get_table_codes(144)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0144_c_1(self):
        assert is_valid_table_value(144, '1') is True

    def test_valid_code_0144_c_2(self):
        assert is_valid_table_value(144, '2') is True

    def test_valid_code_0144_c_3(self):
        assert is_valid_table_value(144, '3') is True

    def test_valid_code_0144_c_4(self):
        assert is_valid_table_value(144, '4') is True

    def test_valid_code_0144_c_5(self):
        assert is_valid_table_value(144, '5') is True

    def test_invalid_code_0144(self):
        assert is_valid_table_value(144, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0144(self):
        result = validate_table_value(144, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0144(self):
        result = validate_table_value(144, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0145:
    """Tests for table 0145: RoomType"""

    def test_get_table_codes_0145(self):
        codes = get_table_codes(145)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0145_pri(self):
        assert is_valid_table_value(145, 'PRI') is True

    def test_valid_code_0145_c_2pri(self):
        assert is_valid_table_value(145, '2PRI') is True

    def test_valid_code_0145_spr(self):
        assert is_valid_table_value(145, 'SPR') is True

    def test_valid_code_0145_c_2spr(self):
        assert is_valid_table_value(145, '2SPR') is True

    def test_valid_code_0145_icu(self):
        assert is_valid_table_value(145, 'ICU') is True

    def test_invalid_code_0145(self):
        assert is_valid_table_value(145, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0145(self):
        result = validate_table_value(145, 'PRI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0145(self):
        result = validate_table_value(145, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0146:
    """Tests for table 0146: AmountType"""

    def test_get_table_codes_0146(self):
        codes = get_table_codes(146)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0146_df(self):
        assert is_valid_table_value(146, 'DF') is True

    def test_valid_code_0146_lm(self):
        assert is_valid_table_value(146, 'LM') is True

    def test_valid_code_0146_pc(self):
        assert is_valid_table_value(146, 'PC') is True

    def test_valid_code_0146_rt(self):
        assert is_valid_table_value(146, 'RT') is True

    def test_valid_code_0146_ul(self):
        assert is_valid_table_value(146, 'UL') is True

    def test_invalid_code_0146(self):
        assert is_valid_table_value(146, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0146(self):
        result = validate_table_value(146, 'DF', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0146(self):
        result = validate_table_value(146, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0147:
    """Tests for table 0147: PolicyType"""

    def test_get_table_codes_0147(self):
        codes = get_table_codes(147)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0147_anc(self):
        assert is_valid_table_value(147, 'ANC') is True

    def test_valid_code_0147_c_2anc(self):
        assert is_valid_table_value(147, '2ANC') is True

    def test_valid_code_0147_mmd(self):
        assert is_valid_table_value(147, 'MMD') is True

    def test_valid_code_0147_c_2mmd(self):
        assert is_valid_table_value(147, '2MMD') is True

    def test_valid_code_0147_c_3mmd(self):
        assert is_valid_table_value(147, '3MMD') is True

    def test_invalid_code_0147(self):
        assert is_valid_table_value(147, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0147(self):
        result = validate_table_value(147, 'ANC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0147(self):
        result = validate_table_value(147, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0148:
    """Tests for table 0148: MoneyOrPercentageIndicator"""

    def test_get_table_codes_0148(self):
        codes = get_table_codes(148)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0148_at(self):
        assert is_valid_table_value(148, 'AT') is True

    def test_valid_code_0148_pc(self):
        assert is_valid_table_value(148, 'PC') is True

    def test_invalid_code_0148(self):
        assert is_valid_table_value(148, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0148(self):
        result = validate_table_value(148, 'AT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0148(self):
        result = validate_table_value(148, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0149:
    """Tests for table 0149: DayType"""

    def test_get_table_codes_0149(self):
        codes = get_table_codes(149)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0149_ap(self):
        assert is_valid_table_value(149, 'AP') is True

    def test_valid_code_0149_de(self):
        assert is_valid_table_value(149, 'DE') is True

    def test_valid_code_0149_pe(self):
        assert is_valid_table_value(149, 'PE') is True

    def test_invalid_code_0149(self):
        assert is_valid_table_value(149, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0149(self):
        result = validate_table_value(149, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0149(self):
        result = validate_table_value(149, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0150:
    """Tests for table 0150: CertificationPatientType"""

    def test_get_table_codes_0150(self):
        codes = get_table_codes(150)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0150_er(self):
        assert is_valid_table_value(150, 'ER') is True

    def test_valid_code_0150_ipe(self):
        assert is_valid_table_value(150, 'IPE') is True

    def test_valid_code_0150_ope(self):
        assert is_valid_table_value(150, 'OPE') is True

    def test_valid_code_0150_ur(self):
        assert is_valid_table_value(150, 'UR') is True

    def test_invalid_code_0150(self):
        assert is_valid_table_value(150, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0150(self):
        result = validate_table_value(150, 'ER', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0150(self):
        result = validate_table_value(150, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0155:
    """Tests for table 0155: AcceptApplicationAcknowledgmentConditions"""

    def test_get_table_codes_0155(self):
        codes = get_table_codes(155)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0155_al(self):
        assert is_valid_table_value(155, 'AL') is True

    def test_valid_code_0155_ne(self):
        assert is_valid_table_value(155, 'NE') is True

    def test_valid_code_0155_er(self):
        assert is_valid_table_value(155, 'ER') is True

    def test_valid_code_0155_su(self):
        assert is_valid_table_value(155, 'SU') is True

    def test_invalid_code_0155(self):
        assert is_valid_table_value(155, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0155(self):
        result = validate_table_value(155, 'AL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0155(self):
        result = validate_table_value(155, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0156:
    """Tests for table 0156: WhichDateTimeQualifier"""

    def test_get_table_codes_0156(self):
        codes = get_table_codes(156)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0156_can(self):
        assert is_valid_table_value(156, 'CAN') is True

    def test_valid_code_0156_any(self):
        assert is_valid_table_value(156, 'ANY') is True

    def test_valid_code_0156_col(self):
        assert is_valid_table_value(156, 'COL') is True

    def test_valid_code_0156_ord(self):
        assert is_valid_table_value(156, 'ORD') is True

    def test_valid_code_0156_rct(self):
        assert is_valid_table_value(156, 'RCT') is True

    def test_invalid_code_0156(self):
        assert is_valid_table_value(156, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0156(self):
        result = validate_table_value(156, 'CAN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0156(self):
        result = validate_table_value(156, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0157:
    """Tests for table 0157: WhichDateTimeStatusQualifier"""

    def test_get_table_codes_0157(self):
        codes = get_table_codes(157)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0157_any(self):
        assert is_valid_table_value(157, 'ANY') is True

    def test_valid_code_0157_cfn(self):
        assert is_valid_table_value(157, 'CFN') is True

    def test_valid_code_0157_cor(self):
        assert is_valid_table_value(157, 'COR') is True

    def test_valid_code_0157_fin(self):
        assert is_valid_table_value(157, 'FIN') is True

    def test_valid_code_0157_pre(self):
        assert is_valid_table_value(157, 'PRE') is True

    def test_invalid_code_0157(self):
        assert is_valid_table_value(157, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0157(self):
        result = validate_table_value(157, 'ANY', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0157(self):
        result = validate_table_value(157, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0158:
    """Tests for table 0158: DateTimeSelectionQualifier"""

    def test_get_table_codes_0158(self):
        codes = get_table_codes(158)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0158_c_1st(self):
        assert is_valid_table_value(158, '1ST') is True

    def test_valid_code_0158_all(self):
        assert is_valid_table_value(158, 'ALL') is True

    def test_valid_code_0158_lst(self):
        assert is_valid_table_value(158, 'LST') is True

    def test_valid_code_0158_rev(self):
        assert is_valid_table_value(158, 'REV') is True

    def test_invalid_code_0158(self):
        assert is_valid_table_value(158, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0158(self):
        result = validate_table_value(158, '1ST', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0158(self):
        result = validate_table_value(158, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0159:
    """Tests for table 0159: DietCodeSpecificationType"""

    def test_get_table_codes_0159(self):
        codes = get_table_codes(159)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0159_d(self):
        assert is_valid_table_value(159, 'D') is True

    def test_valid_code_0159_s(self):
        assert is_valid_table_value(159, 'S') is True

    def test_valid_code_0159_p(self):
        assert is_valid_table_value(159, 'P') is True

    def test_invalid_code_0159(self):
        assert is_valid_table_value(159, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0159(self):
        result = validate_table_value(159, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0159(self):
        result = validate_table_value(159, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0160:
    """Tests for table 0160: TrayType"""

    def test_get_table_codes_0160(self):
        codes = get_table_codes(160)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0160_early(self):
        assert is_valid_table_value(160, 'EARLY') is True

    def test_valid_code_0160_late(self):
        assert is_valid_table_value(160, 'LATE') is True

    def test_valid_code_0160_guest(self):
        assert is_valid_table_value(160, 'GUEST') is True

    def test_valid_code_0160_no(self):
        assert is_valid_table_value(160, 'NO') is True

    def test_valid_code_0160_msg(self):
        assert is_valid_table_value(160, 'MSG') is True

    def test_invalid_code_0160(self):
        assert is_valid_table_value(160, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0160(self):
        result = validate_table_value(160, 'EARLY', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0160(self):
        result = validate_table_value(160, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0161:
    """Tests for table 0161: AllowSubstitution"""

    def test_get_table_codes_0161(self):
        codes = get_table_codes(161)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0161_n(self):
        assert is_valid_table_value(161, 'N') is True

    def test_valid_code_0161_g(self):
        assert is_valid_table_value(161, 'G') is True

    def test_valid_code_0161_t(self):
        assert is_valid_table_value(161, 'T') is True

    def test_invalid_code_0161(self):
        assert is_valid_table_value(161, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0161(self):
        result = validate_table_value(161, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0161(self):
        result = validate_table_value(161, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0162:
    """Tests for table 0162: RouteOfAdministration"""

    def test_get_table_codes_0162(self):
        codes = get_table_codes(162)
        assert codes is not None
        assert len(codes) == 47

    def test_valid_code_0162_ap(self):
        assert is_valid_table_value(162, 'AP') is True

    def test_valid_code_0162_b(self):
        assert is_valid_table_value(162, 'B') is True

    def test_valid_code_0162_dt(self):
        assert is_valid_table_value(162, 'DT') is True

    def test_valid_code_0162_ep(self):
        assert is_valid_table_value(162, 'EP') is True

    def test_valid_code_0162_et(self):
        assert is_valid_table_value(162, 'ET') is True

    def test_invalid_code_0162(self):
        assert is_valid_table_value(162, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0162(self):
        result = validate_table_value(162, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0162(self):
        result = validate_table_value(162, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0163:
    """Tests for table 0163: BodySite"""

    def test_get_table_codes_0163(self):
        codes = get_table_codes(163)
        assert codes is not None
        assert len(codes) == 56

    def test_valid_code_0163_lnb(self):
        assert is_valid_table_value(163, 'LNB') is True

    def test_valid_code_0163_lv(self):
        assert is_valid_table_value(163, 'LV') is True

    def test_valid_code_0163_be(self):
        assert is_valid_table_value(163, 'BE') is True

    def test_valid_code_0163_ou(self):
        assert is_valid_table_value(163, 'OU') is True

    def test_valid_code_0163_bn(self):
        assert is_valid_table_value(163, 'BN') is True

    def test_invalid_code_0163(self):
        assert is_valid_table_value(163, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0163(self):
        result = validate_table_value(163, 'LNB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0163(self):
        result = validate_table_value(163, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0164:
    """Tests for table 0164: AdministrationDevice"""

    def test_get_table_codes_0164(self):
        codes = get_table_codes(164)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0164_ap(self):
        assert is_valid_table_value(164, 'AP') is True

    def test_valid_code_0164_bt(self):
        assert is_valid_table_value(164, 'BT') is True

    def test_valid_code_0164_hl(self):
        assert is_valid_table_value(164, 'HL') is True

    def test_valid_code_0164_ippb(self):
        assert is_valid_table_value(164, 'IPPB') is True

    def test_valid_code_0164_ivp(self):
        assert is_valid_table_value(164, 'IVP') is True

    def test_invalid_code_0164(self):
        assert is_valid_table_value(164, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0164(self):
        result = validate_table_value(164, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0164(self):
        result = validate_table_value(164, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0165:
    """Tests for table 0165: AdministrationMethod"""

    def test_get_table_codes_0165(self):
        codes = get_table_codes(165)
        assert codes is not None
        assert len(codes) == 15

    def test_valid_code_0165_ch(self):
        assert is_valid_table_value(165, 'CH') is True

    def test_valid_code_0165_di(self):
        assert is_valid_table_value(165, 'DI') is True

    def test_valid_code_0165_du(self):
        assert is_valid_table_value(165, 'DU') is True

    def test_valid_code_0165_if(self):
        assert is_valid_table_value(165, 'IF') is True

    def test_valid_code_0165_is(self):
        assert is_valid_table_value(165, 'IS') is True

    def test_invalid_code_0165(self):
        assert is_valid_table_value(165, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0165(self):
        result = validate_table_value(165, 'CH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0165(self):
        result = validate_table_value(165, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0166:
    """Tests for table 0166: RxComponentType"""

    def test_get_table_codes_0166(self):
        codes = get_table_codes(166)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0166_b(self):
        assert is_valid_table_value(166, 'B') is True

    def test_valid_code_0166_a(self):
        assert is_valid_table_value(166, 'A') is True

    def test_invalid_code_0166(self):
        assert is_valid_table_value(166, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0166(self):
        result = validate_table_value(166, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0166(self):
        result = validate_table_value(166, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0167:
    """Tests for table 0167: SubstitutionStatus"""

    def test_get_table_codes_0167(self):
        codes = get_table_codes(167)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0167_n(self):
        assert is_valid_table_value(167, 'N') is True

    def test_valid_code_0167_g(self):
        assert is_valid_table_value(167, 'G') is True

    def test_valid_code_0167_t(self):
        assert is_valid_table_value(167, 'T') is True

    def test_valid_code_0167_c_0(self):
        assert is_valid_table_value(167, '0') is True

    def test_valid_code_0167_c_1(self):
        assert is_valid_table_value(167, '1') is True

    def test_invalid_code_0167(self):
        assert is_valid_table_value(167, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0167(self):
        result = validate_table_value(167, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0167(self):
        result = validate_table_value(167, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0168:
    """Tests for table 0168: ProcessingPriority"""

    def test_get_table_codes_0168(self):
        codes = get_table_codes(168)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0168_s(self):
        assert is_valid_table_value(168, 'S') is True

    def test_valid_code_0168_a(self):
        assert is_valid_table_value(168, 'A') is True

    def test_valid_code_0168_r(self):
        assert is_valid_table_value(168, 'R') is True

    def test_valid_code_0168_p(self):
        assert is_valid_table_value(168, 'P') is True

    def test_valid_code_0168_t(self):
        assert is_valid_table_value(168, 'T') is True

    def test_invalid_code_0168(self):
        assert is_valid_table_value(168, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0168(self):
        result = validate_table_value(168, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0168(self):
        result = validate_table_value(168, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0169:
    """Tests for table 0169: ReportingPriority"""

    def test_get_table_codes_0169(self):
        codes = get_table_codes(169)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0169_c(self):
        assert is_valid_table_value(169, 'C') is True

    def test_valid_code_0169_r(self):
        assert is_valid_table_value(169, 'R') is True

    def test_invalid_code_0169(self):
        assert is_valid_table_value(169, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0169(self):
        result = validate_table_value(169, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0169(self):
        result = validate_table_value(169, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0170:
    """Tests for table 0170: DerivedSpecimen"""

    def test_get_table_codes_0170(self):
        codes = get_table_codes(170)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0170_p(self):
        assert is_valid_table_value(170, 'P') is True

    def test_valid_code_0170_c(self):
        assert is_valid_table_value(170, 'C') is True

    def test_valid_code_0170_n(self):
        assert is_valid_table_value(170, 'N') is True

    def test_invalid_code_0170(self):
        assert is_valid_table_value(170, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0170(self):
        result = validate_table_value(170, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0170(self):
        result = validate_table_value(170, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0173:
    """Tests for table 0173: CoordinationOfBenefits"""

    def test_get_table_codes_0173(self):
        codes = get_table_codes(173)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0173_co(self):
        assert is_valid_table_value(173, 'CO') is True

    def test_valid_code_0173_in(self):
        assert is_valid_table_value(173, 'IN') is True

    def test_invalid_code_0173(self):
        assert is_valid_table_value(173, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0173(self):
        result = validate_table_value(173, 'CO', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0173(self):
        result = validate_table_value(173, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0174:
    """Tests for table 0174: NatureOfServiceTestObservation"""

    def test_get_table_codes_0174(self):
        codes = get_table_codes(174)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0174_p(self):
        assert is_valid_table_value(174, 'P') is True

    def test_valid_code_0174_f(self):
        assert is_valid_table_value(174, 'F') is True

    def test_valid_code_0174_a(self):
        assert is_valid_table_value(174, 'A') is True

    def test_valid_code_0174_s(self):
        assert is_valid_table_value(174, 'S') is True

    def test_valid_code_0174_c(self):
        assert is_valid_table_value(174, 'C') is True

    def test_invalid_code_0174(self):
        assert is_valid_table_value(174, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0174(self):
        result = validate_table_value(174, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0174(self):
        result = validate_table_value(174, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0175:
    """Tests for table 0175: MasterFileIdentifierCodes"""

    def test_get_table_codes_0175(self):
        codes = get_table_codes(175)
        assert codes is not None
        assert len(codes) == 26

    def test_valid_code_0175_om1(self):
        assert is_valid_table_value(175, 'OM1') is True

    def test_valid_code_0175_om2(self):
        assert is_valid_table_value(175, 'OM2') is True

    def test_valid_code_0175_om3(self):
        assert is_valid_table_value(175, 'OM3') is True

    def test_valid_code_0175_om4(self):
        assert is_valid_table_value(175, 'OM4') is True

    def test_valid_code_0175_om5(self):
        assert is_valid_table_value(175, 'OM5') is True

    def test_invalid_code_0175(self):
        assert is_valid_table_value(175, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0175(self):
        result = validate_table_value(175, 'OM1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0175(self):
        result = validate_table_value(175, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0177:
    """Tests for table 0177: ConfidentialityCodes"""

    def test_get_table_codes_0177(self):
        codes = get_table_codes(177)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0177_v(self):
        assert is_valid_table_value(177, 'V') is True

    def test_valid_code_0177_r(self):
        assert is_valid_table_value(177, 'R') is True

    def test_valid_code_0177_u(self):
        assert is_valid_table_value(177, 'U') is True

    def test_valid_code_0177_emp(self):
        assert is_valid_table_value(177, 'EMP') is True

    def test_valid_code_0177_uwm(self):
        assert is_valid_table_value(177, 'UWM') is True

    def test_invalid_code_0177(self):
        assert is_valid_table_value(177, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0177(self):
        result = validate_table_value(177, 'V', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0177(self):
        result = validate_table_value(177, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0178:
    """Tests for table 0178: FileLevelEvent"""

    def test_get_table_codes_0178(self):
        codes = get_table_codes(178)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0178_rep(self):
        assert is_valid_table_value(178, 'REP') is True

    def test_valid_code_0178_upd(self):
        assert is_valid_table_value(178, 'UPD') is True

    def test_invalid_code_0178(self):
        assert is_valid_table_value(178, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0178(self):
        result = validate_table_value(178, 'REP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0178(self):
        result = validate_table_value(178, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0179:
    """Tests for table 0179: ResponseLevel"""

    def test_get_table_codes_0179(self):
        codes = get_table_codes(179)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0179_ne(self):
        assert is_valid_table_value(179, 'NE') is True

    def test_valid_code_0179_er(self):
        assert is_valid_table_value(179, 'ER') is True

    def test_valid_code_0179_al(self):
        assert is_valid_table_value(179, 'AL') is True

    def test_valid_code_0179_su(self):
        assert is_valid_table_value(179, 'SU') is True

    def test_invalid_code_0179(self):
        assert is_valid_table_value(179, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0179(self):
        result = validate_table_value(179, 'NE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0179(self):
        result = validate_table_value(179, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0180:
    """Tests for table 0180: MasterfileActionCode"""

    def test_get_table_codes_0180(self):
        codes = get_table_codes(180)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0180_mad(self):
        assert is_valid_table_value(180, 'MAD') is True

    def test_valid_code_0180_mdl(self):
        assert is_valid_table_value(180, 'MDL') is True

    def test_valid_code_0180_mup(self):
        assert is_valid_table_value(180, 'MUP') is True

    def test_valid_code_0180_mdc(self):
        assert is_valid_table_value(180, 'MDC') is True

    def test_valid_code_0180_mac(self):
        assert is_valid_table_value(180, 'MAC') is True

    def test_invalid_code_0180(self):
        assert is_valid_table_value(180, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0180(self):
        result = validate_table_value(180, 'MAD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0180(self):
        result = validate_table_value(180, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0181:
    """Tests for table 0181: MfnRecordLevelErrorReturn"""

    def test_get_table_codes_0181(self):
        codes = get_table_codes(181)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0181_s(self):
        assert is_valid_table_value(181, 'S') is True

    def test_valid_code_0181_u(self):
        assert is_valid_table_value(181, 'U') is True

    def test_invalid_code_0181(self):
        assert is_valid_table_value(181, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0181(self):
        result = validate_table_value(181, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0181(self):
        result = validate_table_value(181, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0183:
    """Tests for table 0183: ActiveInactive"""

    def test_get_table_codes_0183(self):
        codes = get_table_codes(183)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0183_a(self):
        assert is_valid_table_value(183, 'A') is True

    def test_valid_code_0183_i(self):
        assert is_valid_table_value(183, 'I') is True

    def test_invalid_code_0183(self):
        assert is_valid_table_value(183, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0183(self):
        result = validate_table_value(183, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0183(self):
        result = validate_table_value(183, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0185:
    """Tests for table 0185: PreferredMethodOfContact"""

    def test_get_table_codes_0185(self):
        codes = get_table_codes(185)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0185_b(self):
        assert is_valid_table_value(185, 'B') is True

    def test_valid_code_0185_c(self):
        assert is_valid_table_value(185, 'C') is True

    def test_valid_code_0185_e(self):
        assert is_valid_table_value(185, 'E') is True

    def test_valid_code_0185_f(self):
        assert is_valid_table_value(185, 'F') is True

    def test_valid_code_0185_h(self):
        assert is_valid_table_value(185, 'H') is True

    def test_invalid_code_0185(self):
        assert is_valid_table_value(185, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0185(self):
        result = validate_table_value(185, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0185(self):
        result = validate_table_value(185, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0187:
    """Tests for table 0187: ProviderBilling"""

    def test_get_table_codes_0187(self):
        codes = get_table_codes(187)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0187_i(self):
        assert is_valid_table_value(187, 'I') is True

    def test_valid_code_0187_p(self):
        assert is_valid_table_value(187, 'P') is True

    def test_invalid_code_0187(self):
        assert is_valid_table_value(187, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0187(self):
        result = validate_table_value(187, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0187(self):
        result = validate_table_value(187, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0189:
    """Tests for table 0189: EthnicGroup"""

    def test_get_table_codes_0189(self):
        codes = get_table_codes(189)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0189_h(self):
        assert is_valid_table_value(189, 'H') is True

    def test_valid_code_0189_n(self):
        assert is_valid_table_value(189, 'N') is True

    def test_valid_code_0189_u(self):
        assert is_valid_table_value(189, 'U') is True

    def test_invalid_code_0189(self):
        assert is_valid_table_value(189, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0189(self):
        result = validate_table_value(189, 'H', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0189(self):
        result = validate_table_value(189, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0190:
    """Tests for table 0190: AddressType"""

    def test_get_table_codes_0190(self):
        codes = get_table_codes(190)
        assert codes is not None
        assert len(codes) == 18

    def test_valid_code_0190_ba(self):
        assert is_valid_table_value(190, 'BA') is True

    def test_valid_code_0190_bi(self):
        assert is_valid_table_value(190, 'BI') is True

    def test_valid_code_0190_n(self):
        assert is_valid_table_value(190, 'N') is True

    def test_valid_code_0190_bdl(self):
        assert is_valid_table_value(190, 'BDL') is True

    def test_valid_code_0190_f(self):
        assert is_valid_table_value(190, 'F') is True

    def test_invalid_code_0190(self):
        assert is_valid_table_value(190, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0190(self):
        result = validate_table_value(190, 'BA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0190(self):
        result = validate_table_value(190, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0191:
    """Tests for table 0191: TypeOfReferencedData"""

    def test_get_table_codes_0191(self):
        codes = get_table_codes(191)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0191_ap(self):
        assert is_valid_table_value(191, 'AP') is True

    def test_valid_code_0191_au(self):
        assert is_valid_table_value(191, 'AU') is True

    def test_valid_code_0191_ft(self):
        assert is_valid_table_value(191, 'FT') is True

    def test_valid_code_0191_im(self):
        assert is_valid_table_value(191, 'IM') is True

    def test_valid_code_0191_multipart(self):
        assert is_valid_table_value(191, 'multipart') is True

    def test_invalid_code_0191(self):
        assert is_valid_table_value(191, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0191(self):
        result = validate_table_value(191, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0191(self):
        result = validate_table_value(191, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0193:
    """Tests for table 0193: AmountClass"""

    def test_get_table_codes_0193(self):
        codes = get_table_codes(193)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0193_at(self):
        assert is_valid_table_value(193, 'AT') is True

    def test_valid_code_0193_lm(self):
        assert is_valid_table_value(193, 'LM') is True

    def test_valid_code_0193_pc(self):
        assert is_valid_table_value(193, 'PC') is True

    def test_valid_code_0193_ul(self):
        assert is_valid_table_value(193, 'UL') is True

    def test_invalid_code_0193(self):
        assert is_valid_table_value(193, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0193(self):
        result = validate_table_value(193, 'AT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0193(self):
        result = validate_table_value(193, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0200:
    """Tests for table 0200: NameType2"""

    def test_get_table_codes_0200(self):
        codes = get_table_codes(200)
        assert codes is not None
        assert len(codes) == 24

    def test_valid_code_0200_o(self):
        assert is_valid_table_value(200, 'O') is True

    def test_valid_code_0200_a(self):
        assert is_valid_table_value(200, 'A') is True

    def test_valid_code_0200_b(self):
        assert is_valid_table_value(200, 'B') is True

    def test_valid_code_0200_bad(self):
        assert is_valid_table_value(200, 'BAD') is True

    def test_valid_code_0200_c(self):
        assert is_valid_table_value(200, 'C') is True

    def test_invalid_code_0200(self):
        assert is_valid_table_value(200, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0200(self):
        result = validate_table_value(200, 'O', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0200(self):
        result = validate_table_value(200, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0201:
    """Tests for table 0201: TelecommunicationUse"""

    def test_get_table_codes_0201(self):
        codes = get_table_codes(201)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0201_prn(self):
        assert is_valid_table_value(201, 'PRN') is True

    def test_valid_code_0201_orn(self):
        assert is_valid_table_value(201, 'ORN') is True

    def test_valid_code_0201_wpn(self):
        assert is_valid_table_value(201, 'WPN') is True

    def test_valid_code_0201_vhn(self):
        assert is_valid_table_value(201, 'VHN') is True

    def test_valid_code_0201_asn(self):
        assert is_valid_table_value(201, 'ASN') is True

    def test_invalid_code_0201(self):
        assert is_valid_table_value(201, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0201(self):
        result = validate_table_value(201, 'PRN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0201(self):
        result = validate_table_value(201, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0202:
    """Tests for table 0202: TelecommunicationEquipmentType"""

    def test_get_table_codes_0202(self):
        codes = get_table_codes(202)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0202_ph(self):
        assert is_valid_table_value(202, 'PH') is True

    def test_valid_code_0202_fx(self):
        assert is_valid_table_value(202, 'FX') is True

    def test_valid_code_0202_md(self):
        assert is_valid_table_value(202, 'MD') is True

    def test_valid_code_0202_cp(self):
        assert is_valid_table_value(202, 'CP') is True

    def test_valid_code_0202_sat(self):
        assert is_valid_table_value(202, 'SAT') is True

    def test_invalid_code_0202(self):
        assert is_valid_table_value(202, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0202(self):
        result = validate_table_value(202, 'PH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0202(self):
        result = validate_table_value(202, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0203:
    """Tests for table 0203: IdentifierType"""

    def test_get_table_codes_0203(self):
        codes = get_table_codes(203)
        assert codes is not None
        assert len(codes) == 147

    def test_valid_code_0203_ac(self):
        assert is_valid_table_value(203, 'AC') is True

    def test_valid_code_0203_acsn(self):
        assert is_valid_table_value(203, 'ACSN') is True

    def test_valid_code_0203_ain(self):
        assert is_valid_table_value(203, 'AIN') is True

    def test_valid_code_0203_am(self):
        assert is_valid_table_value(203, 'AM') is True

    def test_valid_code_0203_ama(self):
        assert is_valid_table_value(203, 'AMA') is True

    def test_invalid_code_0203(self):
        assert is_valid_table_value(203, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0203(self):
        result = validate_table_value(203, 'AC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0203(self):
        result = validate_table_value(203, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0204:
    """Tests for table 0204: OrganizationalNameType"""

    def test_get_table_codes_0204(self):
        codes = get_table_codes(204)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0204_a(self):
        assert is_valid_table_value(204, 'A') is True

    def test_valid_code_0204_l(self):
        assert is_valid_table_value(204, 'L') is True

    def test_valid_code_0204_d(self):
        assert is_valid_table_value(204, 'D') is True

    def test_valid_code_0204_sl(self):
        assert is_valid_table_value(204, 'SL') is True

    def test_invalid_code_0204(self):
        assert is_valid_table_value(204, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0204(self):
        result = validate_table_value(204, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0204(self):
        result = validate_table_value(204, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0205:
    """Tests for table 0205: PriceType"""

    def test_get_table_codes_0205(self):
        codes = get_table_codes(205)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0205_ap(self):
        assert is_valid_table_value(205, 'AP') is True

    def test_valid_code_0205_dc(self):
        assert is_valid_table_value(205, 'DC') is True

    def test_valid_code_0205_ic(self):
        assert is_valid_table_value(205, 'IC') is True

    def test_valid_code_0205_pf(self):
        assert is_valid_table_value(205, 'PF') is True

    def test_valid_code_0205_tf(self):
        assert is_valid_table_value(205, 'TF') is True

    def test_invalid_code_0205(self):
        assert is_valid_table_value(205, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0205(self):
        result = validate_table_value(205, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0205(self):
        result = validate_table_value(205, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0206:
    """Tests for table 0206: SegmentAction"""

    def test_get_table_codes_0206(self):
        codes = get_table_codes(206)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0206_a(self):
        assert is_valid_table_value(206, 'A') is True

    def test_valid_code_0206_d(self):
        assert is_valid_table_value(206, 'D') is True

    def test_valid_code_0206_s(self):
        assert is_valid_table_value(206, 'S') is True

    def test_valid_code_0206_u(self):
        assert is_valid_table_value(206, 'U') is True

    def test_valid_code_0206_x(self):
        assert is_valid_table_value(206, 'X') is True

    def test_invalid_code_0206(self):
        assert is_valid_table_value(206, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0206(self):
        result = validate_table_value(206, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0206(self):
        result = validate_table_value(206, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0207:
    """Tests for table 0207: ProcessingMode"""

    def test_get_table_codes_0207(self):
        codes = get_table_codes(207)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0207_a(self):
        assert is_valid_table_value(207, 'A') is True

    def test_valid_code_0207_r(self):
        assert is_valid_table_value(207, 'R') is True

    def test_valid_code_0207_i(self):
        assert is_valid_table_value(207, 'I') is True

    def test_valid_code_0207_t(self):
        assert is_valid_table_value(207, 'T') is True

    def test_valid_code_0207_not_present(self):
        assert is_valid_table_value(207, 'Not present') is True

    def test_invalid_code_0207(self):
        assert is_valid_table_value(207, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0207(self):
        result = validate_table_value(207, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0207(self):
        result = validate_table_value(207, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0208:
    """Tests for table 0208: QueryResponseStatus"""

    def test_get_table_codes_0208(self):
        codes = get_table_codes(208)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0208_ok(self):
        assert is_valid_table_value(208, 'OK') is True

    def test_valid_code_0208_nf(self):
        assert is_valid_table_value(208, 'NF') is True

    def test_valid_code_0208_ae(self):
        assert is_valid_table_value(208, 'AE') is True

    def test_valid_code_0208_ar(self):
        assert is_valid_table_value(208, 'AR') is True

    def test_valid_code_0208_tm(self):
        assert is_valid_table_value(208, 'TM') is True

    def test_invalid_code_0208(self):
        assert is_valid_table_value(208, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0208(self):
        result = validate_table_value(208, 'OK', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0208(self):
        result = validate_table_value(208, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0209:
    """Tests for table 0209: RelationalOperator"""

    def test_get_table_codes_0209(self):
        codes = get_table_codes(209)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0209_eq(self):
        assert is_valid_table_value(209, 'EQ') is True

    def test_valid_code_0209_ne(self):
        assert is_valid_table_value(209, 'NE') is True

    def test_valid_code_0209_lt(self):
        assert is_valid_table_value(209, 'LT') is True

    def test_valid_code_0209_gt(self):
        assert is_valid_table_value(209, 'GT') is True

    def test_valid_code_0209_le(self):
        assert is_valid_table_value(209, 'LE') is True

    def test_invalid_code_0209(self):
        assert is_valid_table_value(209, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0209(self):
        result = validate_table_value(209, 'EQ', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0209(self):
        result = validate_table_value(209, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0210:
    """Tests for table 0210: RelationalConjunction"""

    def test_get_table_codes_0210(self):
        codes = get_table_codes(210)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0210_and(self):
        assert is_valid_table_value(210, 'AND') is True

    def test_valid_code_0210_or(self):
        assert is_valid_table_value(210, 'OR') is True

    def test_invalid_code_0210(self):
        assert is_valid_table_value(210, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0210(self):
        result = validate_table_value(210, 'AND', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0210(self):
        result = validate_table_value(210, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0211:
    """Tests for table 0211: AlternateCharacterSets"""

    def test_get_table_codes_0211(self):
        codes = get_table_codes(211)
        assert codes is not None
        assert len(codes) == 25

    def test_valid_code_0211_jas2020(self):
        assert is_valid_table_value(211, 'JAS2020') is True

    def test_valid_code_0211_jis_x_0202(self):
        assert is_valid_table_value(211, 'JIS X 0202') is True

    def test_valid_code_0211_ascii(self):
        assert is_valid_table_value(211, 'ASCII') is True

    def test_valid_code_0211_c_8859_1(self):
        assert is_valid_table_value(211, '8859/1') is True

    def test_valid_code_0211_c_8859_2(self):
        assert is_valid_table_value(211, '8859/2') is True

    def test_invalid_code_0211(self):
        assert is_valid_table_value(211, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0211(self):
        result = validate_table_value(211, 'JAS2020', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0211(self):
        result = validate_table_value(211, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0213:
    """Tests for table 0213: PurgeStatus"""

    def test_get_table_codes_0213(self):
        codes = get_table_codes(213)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0213_p(self):
        assert is_valid_table_value(213, 'P') is True

    def test_valid_code_0213_d(self):
        assert is_valid_table_value(213, 'D') is True

    def test_valid_code_0213_i(self):
        assert is_valid_table_value(213, 'I') is True

    def test_invalid_code_0213(self):
        assert is_valid_table_value(213, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0213(self):
        result = validate_table_value(213, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0213(self):
        result = validate_table_value(213, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0214:
    """Tests for table 0214: SpecialProgram"""

    def test_get_table_codes_0214(self):
        codes = get_table_codes(214)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0214_ch(self):
        assert is_valid_table_value(214, 'CH') is True

    def test_valid_code_0214_es(self):
        assert is_valid_table_value(214, 'ES') is True

    def test_valid_code_0214_fp(self):
        assert is_valid_table_value(214, 'FP') is True

    def test_valid_code_0214_o(self):
        assert is_valid_table_value(214, 'O') is True

    def test_valid_code_0214_u(self):
        assert is_valid_table_value(214, 'U') is True

    def test_invalid_code_0214(self):
        assert is_valid_table_value(214, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0214(self):
        result = validate_table_value(214, 'CH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0214(self):
        result = validate_table_value(214, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0215:
    """Tests for table 0215: Publicity"""

    def test_get_table_codes_0215(self):
        codes = get_table_codes(215)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0215_f(self):
        assert is_valid_table_value(215, 'F') is True

    def test_valid_code_0215_n(self):
        assert is_valid_table_value(215, 'N') is True

    def test_valid_code_0215_o(self):
        assert is_valid_table_value(215, 'O') is True

    def test_valid_code_0215_u(self):
        assert is_valid_table_value(215, 'U') is True

    def test_invalid_code_0215(self):
        assert is_valid_table_value(215, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0215(self):
        result = validate_table_value(215, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0215(self):
        result = validate_table_value(215, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0216:
    """Tests for table 0216: PatientStatus"""

    def test_get_table_codes_0216(self):
        codes = get_table_codes(216)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0216_ai(self):
        assert is_valid_table_value(216, 'AI') is True

    def test_valid_code_0216_di(self):
        assert is_valid_table_value(216, 'DI') is True

    def test_invalid_code_0216(self):
        assert is_valid_table_value(216, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0216(self):
        result = validate_table_value(216, 'AI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0216(self):
        result = validate_table_value(216, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0217:
    """Tests for table 0217: VisitPriority"""

    def test_get_table_codes_0217(self):
        codes = get_table_codes(217)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0217_c_1(self):
        assert is_valid_table_value(217, '1') is True

    def test_valid_code_0217_c_2(self):
        assert is_valid_table_value(217, '2') is True

    def test_valid_code_0217_c_3(self):
        assert is_valid_table_value(217, '3') is True

    def test_invalid_code_0217(self):
        assert is_valid_table_value(217, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0217(self):
        result = validate_table_value(217, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0217(self):
        result = validate_table_value(217, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0220:
    """Tests for table 0220: LivingArrangement"""

    def test_get_table_codes_0220(self):
        codes = get_table_codes(220)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0220_a(self):
        assert is_valid_table_value(220, 'A') is True

    def test_valid_code_0220_f(self):
        assert is_valid_table_value(220, 'F') is True

    def test_valid_code_0220_i(self):
        assert is_valid_table_value(220, 'I') is True

    def test_valid_code_0220_r(self):
        assert is_valid_table_value(220, 'R') is True

    def test_valid_code_0220_u(self):
        assert is_valid_table_value(220, 'U') is True

    def test_invalid_code_0220(self):
        assert is_valid_table_value(220, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0220(self):
        result = validate_table_value(220, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0220(self):
        result = validate_table_value(220, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0223:
    """Tests for table 0223: LivingDependency2"""

    def test_get_table_codes_0223(self):
        codes = get_table_codes(223)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0223_d(self):
        assert is_valid_table_value(223, 'D') is True

    def test_valid_code_0223_s(self):
        assert is_valid_table_value(223, 'S') is True

    def test_valid_code_0223_m(self):
        assert is_valid_table_value(223, 'M') is True

    def test_valid_code_0223_c(self):
        assert is_valid_table_value(223, 'C') is True

    def test_valid_code_0223_wu(self):
        assert is_valid_table_value(223, 'WU') is True

    def test_invalid_code_0223(self):
        assert is_valid_table_value(223, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0223(self):
        result = validate_table_value(223, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0223(self):
        result = validate_table_value(223, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0224:
    """Tests for table 0224: TransportArranged"""

    def test_get_table_codes_0224(self):
        codes = get_table_codes(224)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0224_a(self):
        assert is_valid_table_value(224, 'A') is True

    def test_valid_code_0224_n(self):
        assert is_valid_table_value(224, 'N') is True

    def test_valid_code_0224_u(self):
        assert is_valid_table_value(224, 'U') is True

    def test_invalid_code_0224(self):
        assert is_valid_table_value(224, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0224(self):
        result = validate_table_value(224, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0224(self):
        result = validate_table_value(224, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0225:
    """Tests for table 0225: EscortRequired"""

    def test_get_table_codes_0225(self):
        codes = get_table_codes(225)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0225_r(self):
        assert is_valid_table_value(225, 'R') is True

    def test_valid_code_0225_n(self):
        assert is_valid_table_value(225, 'N') is True

    def test_valid_code_0225_u(self):
        assert is_valid_table_value(225, 'U') is True

    def test_invalid_code_0225(self):
        assert is_valid_table_value(225, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0225(self):
        result = validate_table_value(225, 'R', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0225(self):
        result = validate_table_value(225, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0228:
    """Tests for table 0228: DiagnosisClassification"""

    def test_get_table_codes_0228(self):
        codes = get_table_codes(228)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0228_c(self):
        assert is_valid_table_value(228, 'C') is True

    def test_valid_code_0228_d(self):
        assert is_valid_table_value(228, 'D') is True

    def test_valid_code_0228_m(self):
        assert is_valid_table_value(228, 'M') is True

    def test_valid_code_0228_o(self):
        assert is_valid_table_value(228, 'O') is True

    def test_valid_code_0228_r(self):
        assert is_valid_table_value(228, 'R') is True

    def test_invalid_code_0228(self):
        assert is_valid_table_value(228, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0228(self):
        result = validate_table_value(228, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0228(self):
        result = validate_table_value(228, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0230:
    """Tests for table 0230: ProcedureFunctionalType"""

    def test_get_table_codes_0230(self):
        codes = get_table_codes(230)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0230_a(self):
        assert is_valid_table_value(230, 'A') is True

    def test_valid_code_0230_p(self):
        assert is_valid_table_value(230, 'P') is True

    def test_valid_code_0230_i(self):
        assert is_valid_table_value(230, 'I') is True

    def test_valid_code_0230_d(self):
        assert is_valid_table_value(230, 'D') is True

    def test_invalid_code_0230(self):
        assert is_valid_table_value(230, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0230(self):
        result = validate_table_value(230, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0230(self):
        result = validate_table_value(230, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0231:
    """Tests for table 0231: StudentStatus"""

    def test_get_table_codes_0231(self):
        codes = get_table_codes(231)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0231_f(self):
        assert is_valid_table_value(231, 'F') is True

    def test_valid_code_0231_p(self):
        assert is_valid_table_value(231, 'P') is True

    def test_valid_code_0231_n(self):
        assert is_valid_table_value(231, 'N') is True

    def test_invalid_code_0231(self):
        assert is_valid_table_value(231, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0231(self):
        result = validate_table_value(231, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0231(self):
        result = validate_table_value(231, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0232:
    """Tests for table 0232: InsuranceCompanyContactReason"""

    def test_get_table_codes_0232(self):
        codes = get_table_codes(232)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0232_c_01(self):
        assert is_valid_table_value(232, '01') is True

    def test_valid_code_0232_c_02(self):
        assert is_valid_table_value(232, '02') is True

    def test_valid_code_0232_c_03(self):
        assert is_valid_table_value(232, '03') is True

    def test_invalid_code_0232(self):
        assert is_valid_table_value(232, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0232(self):
        result = validate_table_value(232, '01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0232(self):
        result = validate_table_value(232, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0234:
    """Tests for table 0234: ReportTiming"""

    def test_get_table_codes_0234(self):
        codes = get_table_codes(234)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0234_co(self):
        assert is_valid_table_value(234, 'CO') is True

    def test_valid_code_0234_ad(self):
        assert is_valid_table_value(234, 'AD') is True

    def test_valid_code_0234_rq(self):
        assert is_valid_table_value(234, 'RQ') is True

    def test_valid_code_0234_de(self):
        assert is_valid_table_value(234, 'DE') is True

    def test_valid_code_0234_pd(self):
        assert is_valid_table_value(234, 'PD') is True

    def test_invalid_code_0234(self):
        assert is_valid_table_value(234, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0234(self):
        result = validate_table_value(234, 'CO', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0234(self):
        result = validate_table_value(234, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0235:
    """Tests for table 0235: ReportSource"""

    def test_get_table_codes_0235(self):
        codes = get_table_codes(235)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0235_c(self):
        assert is_valid_table_value(235, 'C') is True

    def test_valid_code_0235_l(self):
        assert is_valid_table_value(235, 'L') is True

    def test_valid_code_0235_h(self):
        assert is_valid_table_value(235, 'H') is True

    def test_valid_code_0235_r(self):
        assert is_valid_table_value(235, 'R') is True

    def test_valid_code_0235_d(self):
        assert is_valid_table_value(235, 'D') is True

    def test_invalid_code_0235(self):
        assert is_valid_table_value(235, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0235(self):
        result = validate_table_value(235, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0235(self):
        result = validate_table_value(235, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0236:
    """Tests for table 0236: EventReportedTo"""

    def test_get_table_codes_0236(self):
        codes = get_table_codes(236)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0236_m(self):
        assert is_valid_table_value(236, 'M') is True

    def test_valid_code_0236_l(self):
        assert is_valid_table_value(236, 'L') is True

    def test_valid_code_0236_r(self):
        assert is_valid_table_value(236, 'R') is True

    def test_valid_code_0236_d(self):
        assert is_valid_table_value(236, 'D') is True

    def test_invalid_code_0236(self):
        assert is_valid_table_value(236, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0236(self):
        result = validate_table_value(236, 'M', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0236(self):
        result = validate_table_value(236, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0237:
    """Tests for table 0237: EventQualification"""

    def test_get_table_codes_0237(self):
        codes = get_table_codes(237)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0237_i(self):
        assert is_valid_table_value(237, 'I') is True

    def test_valid_code_0237_o(self):
        assert is_valid_table_value(237, 'O') is True

    def test_valid_code_0237_a(self):
        assert is_valid_table_value(237, 'A') is True

    def test_valid_code_0237_m(self):
        assert is_valid_table_value(237, 'M') is True

    def test_valid_code_0237_d(self):
        assert is_valid_table_value(237, 'D') is True

    def test_invalid_code_0237(self):
        assert is_valid_table_value(237, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0237(self):
        result = validate_table_value(237, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0237(self):
        result = validate_table_value(237, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0238:
    """Tests for table 0238: EventSeriousness"""

    def test_get_table_codes_0238(self):
        codes = get_table_codes(238)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0238_y(self):
        assert is_valid_table_value(238, 'Y') is True

    def test_valid_code_0238_s(self):
        assert is_valid_table_value(238, 'S') is True

    def test_valid_code_0238_n(self):
        assert is_valid_table_value(238, 'N') is True

    def test_invalid_code_0238(self):
        assert is_valid_table_value(238, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0238(self):
        result = validate_table_value(238, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0238(self):
        result = validate_table_value(238, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0239:
    """Tests for table 0239: EventExpected"""

    def test_get_table_codes_0239(self):
        codes = get_table_codes(239)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0239_y(self):
        assert is_valid_table_value(239, 'Y') is True

    def test_valid_code_0239_n(self):
        assert is_valid_table_value(239, 'N') is True

    def test_valid_code_0239_u(self):
        assert is_valid_table_value(239, 'U') is True

    def test_invalid_code_0239(self):
        assert is_valid_table_value(239, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0239(self):
        result = validate_table_value(239, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0239(self):
        result = validate_table_value(239, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0240:
    """Tests for table 0240: EventConsequence"""

    def test_get_table_codes_0240(self):
        codes = get_table_codes(240)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0240_d(self):
        assert is_valid_table_value(240, 'D') is True

    def test_valid_code_0240_l(self):
        assert is_valid_table_value(240, 'L') is True

    def test_valid_code_0240_h(self):
        assert is_valid_table_value(240, 'H') is True

    def test_valid_code_0240_p(self):
        assert is_valid_table_value(240, 'P') is True

    def test_valid_code_0240_c(self):
        assert is_valid_table_value(240, 'C') is True

    def test_invalid_code_0240(self):
        assert is_valid_table_value(240, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0240(self):
        result = validate_table_value(240, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0240(self):
        result = validate_table_value(240, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0241:
    """Tests for table 0241: PatientOutcome"""

    def test_get_table_codes_0241(self):
        codes = get_table_codes(241)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0241_d(self):
        assert is_valid_table_value(241, 'D') is True

    def test_valid_code_0241_r(self):
        assert is_valid_table_value(241, 'R') is True

    def test_valid_code_0241_n(self):
        assert is_valid_table_value(241, 'N') is True

    def test_valid_code_0241_w(self):
        assert is_valid_table_value(241, 'W') is True

    def test_valid_code_0241_s(self):
        assert is_valid_table_value(241, 'S') is True

    def test_invalid_code_0241(self):
        assert is_valid_table_value(241, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0241(self):
        result = validate_table_value(241, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0241(self):
        result = validate_table_value(241, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0242:
    """Tests for table 0242: PrimaryObserverQualification"""

    def test_get_table_codes_0242(self):
        codes = get_table_codes(242)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0242_p(self):
        assert is_valid_table_value(242, 'P') is True

    def test_valid_code_0242_r(self):
        assert is_valid_table_value(242, 'R') is True

    def test_valid_code_0242_m(self):
        assert is_valid_table_value(242, 'M') is True

    def test_valid_code_0242_h(self):
        assert is_valid_table_value(242, 'H') is True

    def test_valid_code_0242_c(self):
        assert is_valid_table_value(242, 'C') is True

    def test_invalid_code_0242(self):
        assert is_valid_table_value(242, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0242(self):
        result = validate_table_value(242, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0242(self):
        result = validate_table_value(242, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0243:
    """Tests for table 0243: IdentityMayBeDivulged"""

    def test_get_table_codes_0243(self):
        codes = get_table_codes(243)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0243_y(self):
        assert is_valid_table_value(243, 'Y') is True

    def test_valid_code_0243_n(self):
        assert is_valid_table_value(243, 'N') is True

    def test_valid_code_0243_na(self):
        assert is_valid_table_value(243, 'NA') is True

    def test_invalid_code_0243(self):
        assert is_valid_table_value(243, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0243(self):
        result = validate_table_value(243, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0243(self):
        result = validate_table_value(243, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0247:
    """Tests for table 0247: StatusOfEvaluation"""

    def test_get_table_codes_0247(self):
        codes = get_table_codes(247)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0247_y(self):
        assert is_valid_table_value(247, 'Y') is True

    def test_valid_code_0247_p(self):
        assert is_valid_table_value(247, 'P') is True

    def test_valid_code_0247_k(self):
        assert is_valid_table_value(247, 'K') is True

    def test_valid_code_0247_x(self):
        assert is_valid_table_value(247, 'X') is True

    def test_valid_code_0247_a(self):
        assert is_valid_table_value(247, 'A') is True

    def test_invalid_code_0247(self):
        assert is_valid_table_value(247, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0247(self):
        result = validate_table_value(247, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0247(self):
        result = validate_table_value(247, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0248:
    """Tests for table 0248: ProductSource"""

    def test_get_table_codes_0248(self):
        codes = get_table_codes(248)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0248_a(self):
        assert is_valid_table_value(248, 'A') is True

    def test_valid_code_0248_l(self):
        assert is_valid_table_value(248, 'L') is True

    def test_valid_code_0248_r(self):
        assert is_valid_table_value(248, 'R') is True

    def test_valid_code_0248_n(self):
        assert is_valid_table_value(248, 'N') is True

    def test_invalid_code_0248(self):
        assert is_valid_table_value(248, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0248(self):
        result = validate_table_value(248, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0248(self):
        result = validate_table_value(248, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0250:
    """Tests for table 0250: RelatednessAssessment"""

    def test_get_table_codes_0250(self):
        codes = get_table_codes(250)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0250_h(self):
        assert is_valid_table_value(250, 'H') is True

    def test_valid_code_0250_m(self):
        assert is_valid_table_value(250, 'M') is True

    def test_valid_code_0250_s(self):
        assert is_valid_table_value(250, 'S') is True

    def test_valid_code_0250_i(self):
        assert is_valid_table_value(250, 'I') is True

    def test_valid_code_0250_n(self):
        assert is_valid_table_value(250, 'N') is True

    def test_invalid_code_0250(self):
        assert is_valid_table_value(250, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0250(self):
        result = validate_table_value(250, 'H', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0250(self):
        result = validate_table_value(250, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0251:
    """Tests for table 0251: ActionTakenInResponseToTheEvent"""

    def test_get_table_codes_0251(self):
        codes = get_table_codes(251)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0251_wp(self):
        assert is_valid_table_value(251, 'WP') is True

    def test_valid_code_0251_wt(self):
        assert is_valid_table_value(251, 'WT') is True

    def test_valid_code_0251_dr(self):
        assert is_valid_table_value(251, 'DR') is True

    def test_valid_code_0251_di(self):
        assert is_valid_table_value(251, 'DI') is True

    def test_valid_code_0251_ot(self):
        assert is_valid_table_value(251, 'OT') is True

    def test_invalid_code_0251(self):
        assert is_valid_table_value(251, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0251(self):
        result = validate_table_value(251, 'WP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0251(self):
        result = validate_table_value(251, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0252:
    """Tests for table 0252: CausalityObservations"""

    def test_get_table_codes_0252(self):
        codes = get_table_codes(252)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0252_aw(self):
        assert is_valid_table_value(252, 'AW') is True

    def test_valid_code_0252_be(self):
        assert is_valid_table_value(252, 'BE') is True

    def test_valid_code_0252_li(self):
        assert is_valid_table_value(252, 'LI') is True

    def test_valid_code_0252_in(self):
        assert is_valid_table_value(252, 'IN') is True

    def test_valid_code_0252_ex(self):
        assert is_valid_table_value(252, 'EX') is True

    def test_invalid_code_0252(self):
        assert is_valid_table_value(252, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0252(self):
        result = validate_table_value(252, 'AW', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0252(self):
        result = validate_table_value(252, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0253:
    """Tests for table 0253: IndirectExposureMechanism"""

    def test_get_table_codes_0253(self):
        codes = get_table_codes(253)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0253_b(self):
        assert is_valid_table_value(253, 'B') is True

    def test_valid_code_0253_p(self):
        assert is_valid_table_value(253, 'P') is True

    def test_valid_code_0253_f(self):
        assert is_valid_table_value(253, 'F') is True

    def test_valid_code_0253_x(self):
        assert is_valid_table_value(253, 'X') is True

    def test_valid_code_0253_o(self):
        assert is_valid_table_value(253, 'O') is True

    def test_invalid_code_0253(self):
        assert is_valid_table_value(253, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0253(self):
        result = validate_table_value(253, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0253(self):
        result = validate_table_value(253, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0254:
    """Tests for table 0254: KindOfQuantity"""

    def test_get_table_codes_0254(self):
        codes = get_table_codes(254)
        assert codes is not None
        assert len(codes) == 102

    def test_valid_code_0254_cact(self):
        assert is_valid_table_value(254, 'CACT') is True

    def test_valid_code_0254_cnc(self):
        assert is_valid_table_value(254, 'CNC') is True

    def test_valid_code_0254_ccrto(self):
        assert is_valid_table_value(254, 'CCRTO') is True

    def test_valid_code_0254_ccnt(self):
        assert is_valid_table_value(254, 'CCNT') is True

    def test_valid_code_0254_cfr(self):
        assert is_valid_table_value(254, 'CFR') is True

    def test_invalid_code_0254(self):
        assert is_valid_table_value(254, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0254(self):
        result = validate_table_value(254, 'CACT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0254(self):
        result = validate_table_value(254, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0255:
    """Tests for table 0255: DurationCategories"""

    def test_get_table_codes_0255(self):
        codes = get_table_codes(255)
        assert codes is not None
        assert len(codes) == 27

    def test_valid_code_0255_empty(self):
        assert is_valid_table_value(255, '*') is True

    def test_valid_code_0255_c_30m(self):
        assert is_valid_table_value(255, '30M') is True

    def test_valid_code_0255_c_1h(self):
        assert is_valid_table_value(255, '1H') is True

    def test_valid_code_0255_c_2h(self):
        assert is_valid_table_value(255, '2H') is True

    def test_valid_code_0255_c_2_5h(self):
        assert is_valid_table_value(255, '2.5H') is True

    def test_invalid_code_0255(self):
        assert is_valid_table_value(255, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0255(self):
        result = validate_table_value(255, '*', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0255(self):
        result = validate_table_value(255, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0256:
    """Tests for table 0256: TimeDelayPostChallenge"""

    def test_get_table_codes_0256(self):
        codes = get_table_codes(256)
        assert codes is not None
        assert len(codes) == 44

    def test_valid_code_0256_bs(self):
        assert is_valid_table_value(256, 'BS') is True

    def test_valid_code_0256_peak(self):
        assert is_valid_table_value(256, 'PEAK') is True

    def test_valid_code_0256_trough(self):
        assert is_valid_table_value(256, 'TROUGH') is True

    def test_valid_code_0256_random(self):
        assert is_valid_table_value(256, 'RANDOM') is True

    def test_valid_code_0256_c_1m(self):
        assert is_valid_table_value(256, '1M') is True

    def test_invalid_code_0256(self):
        assert is_valid_table_value(256, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0256(self):
        result = validate_table_value(256, 'BS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0256(self):
        result = validate_table_value(256, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0257:
    """Tests for table 0257: NatureOfChallenge"""

    def test_get_table_codes_0257(self):
        codes = get_table_codes(257)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0257_cfst(self):
        assert is_valid_table_value(257, 'CFST') is True

    def test_valid_code_0257_excz(self):
        assert is_valid_table_value(257, 'EXCZ') is True

    def test_valid_code_0257_ffst(self):
        assert is_valid_table_value(257, 'FFST') is True

    def test_invalid_code_0257(self):
        assert is_valid_table_value(257, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0257(self):
        result = validate_table_value(257, 'CFST', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0257(self):
        result = validate_table_value(257, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0258:
    """Tests for table 0258: RelationshipModifier"""

    def test_get_table_codes_0258(self):
        codes = get_table_codes(258)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0258_control(self):
        assert is_valid_table_value(258, 'CONTROL') is True

    def test_valid_code_0258_patient(self):
        assert is_valid_table_value(258, 'PATIENT') is True

    def test_valid_code_0258_donor(self):
        assert is_valid_table_value(258, 'DONOR') is True

    def test_valid_code_0258_bpu(self):
        assert is_valid_table_value(258, 'BPU') is True

    def test_invalid_code_0258(self):
        assert is_valid_table_value(258, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0258(self):
        result = validate_table_value(258, 'CONTROL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0258(self):
        result = validate_table_value(258, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0260:
    """Tests for table 0260: PatientLocationType"""

    def test_get_table_codes_0260(self):
        codes = get_table_codes(260)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0260_n(self):
        assert is_valid_table_value(260, 'N') is True

    def test_valid_code_0260_r(self):
        assert is_valid_table_value(260, 'R') is True

    def test_valid_code_0260_b(self):
        assert is_valid_table_value(260, 'B') is True

    def test_valid_code_0260_e(self):
        assert is_valid_table_value(260, 'E') is True

    def test_valid_code_0260_o(self):
        assert is_valid_table_value(260, 'O') is True

    def test_invalid_code_0260(self):
        assert is_valid_table_value(260, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0260(self):
        result = validate_table_value(260, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0260(self):
        result = validate_table_value(260, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0261:
    """Tests for table 0261: LocationEquipment"""

    def test_get_table_codes_0261(self):
        codes = get_table_codes(261)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0261_oxy(self):
        assert is_valid_table_value(261, 'OXY') is True

    def test_valid_code_0261_suc(self):
        assert is_valid_table_value(261, 'SUC') is True

    def test_valid_code_0261_vit(self):
        assert is_valid_table_value(261, 'VIT') is True

    def test_valid_code_0261_inf(self):
        assert is_valid_table_value(261, 'INF') is True

    def test_valid_code_0261_ivp(self):
        assert is_valid_table_value(261, 'IVP') is True

    def test_invalid_code_0261(self):
        assert is_valid_table_value(261, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0261(self):
        result = validate_table_value(261, 'OXY', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0261(self):
        result = validate_table_value(261, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0262:
    """Tests for table 0262: PrivacyLevel"""

    def test_get_table_codes_0262(self):
        codes = get_table_codes(262)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0262_f(self):
        assert is_valid_table_value(262, 'F') is True

    def test_valid_code_0262_p(self):
        assert is_valid_table_value(262, 'P') is True

    def test_valid_code_0262_j(self):
        assert is_valid_table_value(262, 'J') is True

    def test_valid_code_0262_q(self):
        assert is_valid_table_value(262, 'Q') is True

    def test_valid_code_0262_s(self):
        assert is_valid_table_value(262, 'S') is True

    def test_invalid_code_0262(self):
        assert is_valid_table_value(262, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0262(self):
        result = validate_table_value(262, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0262(self):
        result = validate_table_value(262, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0263:
    """Tests for table 0263: LevelOfCare"""

    def test_get_table_codes_0263(self):
        codes = get_table_codes(263)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0263_a(self):
        assert is_valid_table_value(263, 'A') is True

    def test_valid_code_0263_e(self):
        assert is_valid_table_value(263, 'E') is True

    def test_valid_code_0263_f(self):
        assert is_valid_table_value(263, 'F') is True

    def test_valid_code_0263_n(self):
        assert is_valid_table_value(263, 'N') is True

    def test_valid_code_0263_c(self):
        assert is_valid_table_value(263, 'C') is True

    def test_invalid_code_0263(self):
        assert is_valid_table_value(263, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0263(self):
        result = validate_table_value(263, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0263(self):
        result = validate_table_value(263, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0265:
    """Tests for table 0265: SpecialtyType"""

    def test_get_table_codes_0265(self):
        codes = get_table_codes(265)
        assert codes is not None
        assert len(codes) == 26

    def test_valid_code_0265_amb(self):
        assert is_valid_table_value(265, 'AMB') is True

    def test_valid_code_0265_psy(self):
        assert is_valid_table_value(265, 'PSY') is True

    def test_valid_code_0265_pps(self):
        assert is_valid_table_value(265, 'PPS') is True

    def test_valid_code_0265_reh(self):
        assert is_valid_table_value(265, 'REH') is True

    def test_valid_code_0265_pre(self):
        assert is_valid_table_value(265, 'PRE') is True

    def test_invalid_code_0265(self):
        assert is_valid_table_value(265, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0265(self):
        result = validate_table_value(265, 'AMB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0265(self):
        result = validate_table_value(265, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0267:
    """Tests for table 0267: DaysOfTheWeek"""

    def test_get_table_codes_0267(self):
        codes = get_table_codes(267)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0267_sat(self):
        assert is_valid_table_value(267, 'SAT') is True

    def test_valid_code_0267_sun(self):
        assert is_valid_table_value(267, 'SUN') is True

    def test_valid_code_0267_mon(self):
        assert is_valid_table_value(267, 'MON') is True

    def test_valid_code_0267_tue(self):
        assert is_valid_table_value(267, 'TUE') is True

    def test_valid_code_0267_wed(self):
        assert is_valid_table_value(267, 'WED') is True

    def test_invalid_code_0267(self):
        assert is_valid_table_value(267, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0267(self):
        result = validate_table_value(267, 'SAT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0267(self):
        result = validate_table_value(267, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0268:
    """Tests for table 0268: Override"""

    def test_get_table_codes_0268(self):
        codes = get_table_codes(268)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0268_x(self):
        assert is_valid_table_value(268, 'X') is True

    def test_valid_code_0268_a(self):
        assert is_valid_table_value(268, 'A') is True

    def test_valid_code_0268_r(self):
        assert is_valid_table_value(268, 'R') is True

    def test_invalid_code_0268(self):
        assert is_valid_table_value(268, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0268(self):
        result = validate_table_value(268, 'X', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0268(self):
        result = validate_table_value(268, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0269:
    """Tests for table 0269: ChargeOnIndicator"""

    def test_get_table_codes_0269(self):
        codes = get_table_codes(269)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0269_o(self):
        assert is_valid_table_value(269, 'O') is True

    def test_valid_code_0269_r(self):
        assert is_valid_table_value(269, 'R') is True

    def test_invalid_code_0269(self):
        assert is_valid_table_value(269, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0269(self):
        result = validate_table_value(269, 'O', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0269(self):
        result = validate_table_value(269, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0270:
    """Tests for table 0270: DocumentType"""

    def test_get_table_codes_0270(self):
        codes = get_table_codes(270)
        assert codes is not None
        assert len(codes) == 14

    def test_valid_code_0270_ar(self):
        assert is_valid_table_value(270, 'AR') is True

    def test_valid_code_0270_cd(self):
        assert is_valid_table_value(270, 'CD') is True

    def test_valid_code_0270_cn(self):
        assert is_valid_table_value(270, 'CN') is True

    def test_valid_code_0270_di(self):
        assert is_valid_table_value(270, 'DI') is True

    def test_valid_code_0270_ds(self):
        assert is_valid_table_value(270, 'DS') is True

    def test_invalid_code_0270(self):
        assert is_valid_table_value(270, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0270(self):
        result = validate_table_value(270, 'AR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0270(self):
        result = validate_table_value(270, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0271:
    """Tests for table 0271: DocumentCompletionStatus"""

    def test_get_table_codes_0271(self):
        codes = get_table_codes(271)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0271_di(self):
        assert is_valid_table_value(271, 'DI') is True

    def test_valid_code_0271_do(self):
        assert is_valid_table_value(271, 'DO') is True

    def test_valid_code_0271_ip(self):
        assert is_valid_table_value(271, 'IP') is True

    def test_valid_code_0271_in(self):
        assert is_valid_table_value(271, 'IN') is True

    def test_valid_code_0271_pa(self):
        assert is_valid_table_value(271, 'PA') is True

    def test_invalid_code_0271(self):
        assert is_valid_table_value(271, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0271(self):
        result = validate_table_value(271, 'DI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0271(self):
        result = validate_table_value(271, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0272:
    """Tests for table 0272: DocumentConfidentialityStatus2"""

    def test_get_table_codes_0272(self):
        codes = get_table_codes(272)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0272_c_1(self):
        assert is_valid_table_value(272, '1') is True

    def test_valid_code_0272_c_2(self):
        assert is_valid_table_value(272, '2') is True

    def test_valid_code_0272_c_3(self):
        assert is_valid_table_value(272, '3') is True

    def test_valid_code_0272_re(self):
        assert is_valid_table_value(272, 'RE') is True

    def test_valid_code_0272_uc(self):
        assert is_valid_table_value(272, 'UC') is True

    def test_invalid_code_0272(self):
        assert is_valid_table_value(272, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0272(self):
        result = validate_table_value(272, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0272(self):
        result = validate_table_value(272, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0273:
    """Tests for table 0273: DocumentAvailabilityStatus"""

    def test_get_table_codes_0273(self):
        codes = get_table_codes(273)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0273_av(self):
        assert is_valid_table_value(273, 'AV') is True

    def test_valid_code_0273_ca(self):
        assert is_valid_table_value(273, 'CA') is True

    def test_valid_code_0273_ob(self):
        assert is_valid_table_value(273, 'OB') is True

    def test_valid_code_0273_un(self):
        assert is_valid_table_value(273, 'UN') is True

    def test_invalid_code_0273(self):
        assert is_valid_table_value(273, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0273(self):
        result = validate_table_value(273, 'AV', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0273(self):
        result = validate_table_value(273, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0275:
    """Tests for table 0275: DocumentStorageStatus"""

    def test_get_table_codes_0275(self):
        codes = get_table_codes(275)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0275_ac(self):
        assert is_valid_table_value(275, 'AC') is True

    def test_valid_code_0275_aa(self):
        assert is_valid_table_value(275, 'AA') is True

    def test_valid_code_0275_ar(self):
        assert is_valid_table_value(275, 'AR') is True

    def test_valid_code_0275_pu(self):
        assert is_valid_table_value(275, 'PU') is True

    def test_invalid_code_0275(self):
        assert is_valid_table_value(275, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0275(self):
        result = validate_table_value(275, 'AC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0275(self):
        result = validate_table_value(275, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0276:
    """Tests for table 0276: AppointmentReason"""

    def test_get_table_codes_0276(self):
        codes = get_table_codes(276)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0276_routine(self):
        assert is_valid_table_value(276, 'ROUTINE') is True

    def test_valid_code_0276_walkin(self):
        assert is_valid_table_value(276, 'WALKIN') is True

    def test_valid_code_0276_checkup(self):
        assert is_valid_table_value(276, 'CHECKUP') is True

    def test_valid_code_0276_followup(self):
        assert is_valid_table_value(276, 'FOLLOWUP') is True

    def test_valid_code_0276_emergency(self):
        assert is_valid_table_value(276, 'EMERGENCY') is True

    def test_invalid_code_0276(self):
        assert is_valid_table_value(276, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0276(self):
        result = validate_table_value(276, 'ROUTINE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0276(self):
        result = validate_table_value(276, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0277:
    """Tests for table 0277: AppointmentType"""

    def test_get_table_codes_0277(self):
        codes = get_table_codes(277)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0277_complete(self):
        assert is_valid_table_value(277, 'COMPLETE') is True

    def test_valid_code_0277_normal(self):
        assert is_valid_table_value(277, 'NORMAL') is True

    def test_valid_code_0277_tentative(self):
        assert is_valid_table_value(277, 'TENTATIVE') is True

    def test_valid_code_0277_normal_2(self):
        assert is_valid_table_value(277, 'Normal') is True

    def test_valid_code_0277_tentative_2(self):
        assert is_valid_table_value(277, 'Tentative') is True

    def test_invalid_code_0277(self):
        assert is_valid_table_value(277, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0277(self):
        result = validate_table_value(277, 'COMPLETE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0277(self):
        result = validate_table_value(277, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0278:
    """Tests for table 0278: FillerStatus"""

    def test_get_table_codes_0278(self):
        codes = get_table_codes(278)
        assert codes is not None
        assert len(codes) == 21

    def test_valid_code_0278_blocked(self):
        assert is_valid_table_value(278, 'BLOCKED') is True

    def test_valid_code_0278_booked(self):
        assert is_valid_table_value(278, 'BOOKED') is True

    def test_valid_code_0278_cancelled(self):
        assert is_valid_table_value(278, 'CANCELLED') is True

    def test_valid_code_0278_complete(self):
        assert is_valid_table_value(278, 'COMPLETE') is True

    def test_valid_code_0278_deleted(self):
        assert is_valid_table_value(278, 'DELETED') is True

    def test_invalid_code_0278(self):
        assert is_valid_table_value(278, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0278(self):
        result = validate_table_value(278, 'BLOCKED', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0278(self):
        result = validate_table_value(278, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0279:
    """Tests for table 0279: AllowSubstitution"""

    def test_get_table_codes_0279(self):
        codes = get_table_codes(279)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0279_confirm(self):
        assert is_valid_table_value(279, 'CONFIRM') is True

    def test_valid_code_0279_no(self):
        assert is_valid_table_value(279, 'NO') is True

    def test_valid_code_0279_notify(self):
        assert is_valid_table_value(279, 'NOTIFY') is True

    def test_valid_code_0279_yes(self):
        assert is_valid_table_value(279, 'YES') is True

    def test_valid_code_0279_no_2(self):
        assert is_valid_table_value(279, 'No') is True

    def test_invalid_code_0279(self):
        assert is_valid_table_value(279, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0279(self):
        result = validate_table_value(279, 'CONFIRM', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0279(self):
        result = validate_table_value(279, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0280:
    """Tests for table 0280: ReferralPriority"""

    def test_get_table_codes_0280(self):
        codes = get_table_codes(280)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0280_s(self):
        assert is_valid_table_value(280, 'S') is True

    def test_valid_code_0280_a(self):
        assert is_valid_table_value(280, 'A') is True

    def test_valid_code_0280_r(self):
        assert is_valid_table_value(280, 'R') is True

    def test_invalid_code_0280(self):
        assert is_valid_table_value(280, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0280(self):
        result = validate_table_value(280, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0280(self):
        result = validate_table_value(280, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0281:
    """Tests for table 0281: ReferralType"""

    def test_get_table_codes_0281(self):
        codes = get_table_codes(281)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0281_hom(self):
        assert is_valid_table_value(281, 'HOM') is True

    def test_valid_code_0281_lab(self):
        assert is_valid_table_value(281, 'LAB') is True

    def test_valid_code_0281_med(self):
        assert is_valid_table_value(281, 'MED') is True

    def test_valid_code_0281_psy(self):
        assert is_valid_table_value(281, 'PSY') is True

    def test_valid_code_0281_rad(self):
        assert is_valid_table_value(281, 'RAD') is True

    def test_invalid_code_0281(self):
        assert is_valid_table_value(281, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0281(self):
        result = validate_table_value(281, 'HOM', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0281(self):
        result = validate_table_value(281, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0282:
    """Tests for table 0282: ReferralDisposition"""

    def test_get_table_codes_0282(self):
        codes = get_table_codes(282)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0282_wr(self):
        assert is_valid_table_value(282, 'WR') is True

    def test_valid_code_0282_rp(self):
        assert is_valid_table_value(282, 'RP') is True

    def test_valid_code_0282_am(self):
        assert is_valid_table_value(282, 'AM') is True

    def test_valid_code_0282_so(self):
        assert is_valid_table_value(282, 'SO') is True

    def test_invalid_code_0282(self):
        assert is_valid_table_value(282, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0282(self):
        result = validate_table_value(282, 'WR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0282(self):
        result = validate_table_value(282, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0283:
    """Tests for table 0283: ReferralStatus"""

    def test_get_table_codes_0283(self):
        codes = get_table_codes(283)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0283_a(self):
        assert is_valid_table_value(283, 'A') is True

    def test_valid_code_0283_p(self):
        assert is_valid_table_value(283, 'P') is True

    def test_valid_code_0283_r(self):
        assert is_valid_table_value(283, 'R') is True

    def test_valid_code_0283_e(self):
        assert is_valid_table_value(283, 'E') is True

    def test_invalid_code_0283(self):
        assert is_valid_table_value(283, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0283(self):
        result = validate_table_value(283, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0283(self):
        result = validate_table_value(283, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0284:
    """Tests for table 0284: ReferralCategory"""

    def test_get_table_codes_0284(self):
        codes = get_table_codes(284)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0284_i(self):
        assert is_valid_table_value(284, 'I') is True

    def test_valid_code_0284_o(self):
        assert is_valid_table_value(284, 'O') is True

    def test_valid_code_0284_a(self):
        assert is_valid_table_value(284, 'A') is True

    def test_valid_code_0284_e(self):
        assert is_valid_table_value(284, 'E') is True

    def test_invalid_code_0284(self):
        assert is_valid_table_value(284, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0284(self):
        result = validate_table_value(284, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0284(self):
        result = validate_table_value(284, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0286:
    """Tests for table 0286: ProviderRole"""

    def test_get_table_codes_0286(self):
        codes = get_table_codes(286)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0286_rp(self):
        assert is_valid_table_value(286, 'RP') is True

    def test_valid_code_0286_pp(self):
        assert is_valid_table_value(286, 'PP') is True

    def test_valid_code_0286_cp(self):
        assert is_valid_table_value(286, 'CP') is True

    def test_valid_code_0286_rt(self):
        assert is_valid_table_value(286, 'RT') is True

    def test_invalid_code_0286(self):
        assert is_valid_table_value(286, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0286(self):
        result = validate_table_value(286, 'RP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0286(self):
        result = validate_table_value(286, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0287:
    """Tests for table 0287: ProblemGoalAction"""

    def test_get_table_codes_0287(self):
        codes = get_table_codes(287)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0287_ad(self):
        assert is_valid_table_value(287, 'AD') is True

    def test_valid_code_0287_co(self):
        assert is_valid_table_value(287, 'CO') is True

    def test_valid_code_0287_de(self):
        assert is_valid_table_value(287, 'DE') is True

    def test_valid_code_0287_li(self):
        assert is_valid_table_value(287, 'LI') is True

    def test_valid_code_0287_sp(self):
        assert is_valid_table_value(287, 'SP') is True

    def test_invalid_code_0287(self):
        assert is_valid_table_value(287, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0287(self):
        result = validate_table_value(287, 'AD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0287(self):
        result = validate_table_value(287, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0290:
    """Tests for table 0290: MimeBase64EncodingCharacters"""

    def test_get_table_codes_0290(self):
        codes = get_table_codes(290)
        assert codes is not None
        assert len(codes) == 65

    def test_valid_code_0290_c_0(self):
        assert is_valid_table_value(290, '0') is True

    def test_valid_code_0290_c_1(self):
        assert is_valid_table_value(290, '1') is True

    def test_valid_code_0290_c_2(self):
        assert is_valid_table_value(290, '2') is True

    def test_valid_code_0290_c_3(self):
        assert is_valid_table_value(290, '3') is True

    def test_valid_code_0290_c_4(self):
        assert is_valid_table_value(290, '4') is True

    def test_invalid_code_0290(self):
        assert is_valid_table_value(290, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0290(self):
        result = validate_table_value(290, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0290(self):
        result = validate_table_value(290, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0291:
    """Tests for table 0291: SubtypeOfReferencedData"""

    def test_get_table_codes_0291(self):
        codes = get_table_codes(291)
        assert codes is not None
        assert len(codes) == 17

    def test_valid_code_0291_basic(self):
        assert is_valid_table_value(291, 'BASIC') is True

    def test_valid_code_0291_empty(self):
        assert is_valid_table_value(291, '...') is True

    def test_valid_code_0291_empty_2(self):
        assert is_valid_table_value(291, '…') is True

    def test_valid_code_0291_dicom(self):
        assert is_valid_table_value(291, 'DICOM') is True

    def test_valid_code_0291_fax(self):
        assert is_valid_table_value(291, 'FAX') is True

    def test_invalid_code_0291(self):
        assert is_valid_table_value(291, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0291(self):
        result = validate_table_value(291, 'BASIC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0291(self):
        result = validate_table_value(291, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0294:
    """Tests for table 0294: TimeSelectionCriteriaParameterClass"""

    def test_get_table_codes_0294(self):
        codes = get_table_codes(294)
        assert codes is not None
        assert len(codes) == 18

    def test_valid_code_0294_prefstart(self):
        assert is_valid_table_value(294, 'PREFSTART') is True

    def test_valid_code_0294_prefstart_2(self):
        assert is_valid_table_value(294, 'Prefstart') is True

    def test_valid_code_0294_prefend(self):
        assert is_valid_table_value(294, 'PREFEND') is True

    def test_valid_code_0294_prefend_2(self):
        assert is_valid_table_value(294, 'Prefend') is True

    def test_valid_code_0294_mon(self):
        assert is_valid_table_value(294, 'MON') is True

    def test_invalid_code_0294(self):
        assert is_valid_table_value(294, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0294(self):
        result = validate_table_value(294, 'PREFSTART', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0294(self):
        result = validate_table_value(294, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0298:
    """Tests for table 0298: CpRangeType"""

    def test_get_table_codes_0298(self):
        codes = get_table_codes(298)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0298_p(self):
        assert is_valid_table_value(298, 'P') is True

    def test_valid_code_0298_f(self):
        assert is_valid_table_value(298, 'F') is True

    def test_invalid_code_0298(self):
        assert is_valid_table_value(298, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0298(self):
        result = validate_table_value(298, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0298(self):
        result = validate_table_value(298, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0299:
    """Tests for table 0299: Encoding"""

    def test_get_table_codes_0299(self):
        codes = get_table_codes(299)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0299_a(self):
        assert is_valid_table_value(299, 'A') is True

    def test_valid_code_0299_hex(self):
        assert is_valid_table_value(299, 'Hex') is True

    def test_valid_code_0299_base64(self):
        assert is_valid_table_value(299, 'Base64') is True

    def test_invalid_code_0299(self):
        assert is_valid_table_value(299, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0299(self):
        result = validate_table_value(299, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0299(self):
        result = validate_table_value(299, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0301:
    """Tests for table 0301: UniversalIdType"""

    def test_get_table_codes_0301(self):
        codes = get_table_codes(301)
        assert codes is not None
        assert len(codes) == 19

    def test_valid_code_0301_cap(self):
        assert is_valid_table_value(301, 'CAP') is True

    def test_valid_code_0301_clia(self):
        assert is_valid_table_value(301, 'CLIA') is True

    def test_valid_code_0301_clip(self):
        assert is_valid_table_value(301, 'CLIP') is True

    def test_valid_code_0301_dns(self):
        assert is_valid_table_value(301, 'DNS') is True

    def test_valid_code_0301_eui64(self):
        assert is_valid_table_value(301, 'EUI64') is True

    def test_invalid_code_0301(self):
        assert is_valid_table_value(301, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0301(self):
        result = validate_table_value(301, 'CAP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0301(self):
        result = validate_table_value(301, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0305:
    """Tests for table 0305: PersonLocationType"""

    def test_get_table_codes_0305(self):
        codes = get_table_codes(305)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0305_c(self):
        assert is_valid_table_value(305, 'C') is True

    def test_valid_code_0305_d(self):
        assert is_valid_table_value(305, 'D') is True

    def test_valid_code_0305_h(self):
        assert is_valid_table_value(305, 'H') is True

    def test_valid_code_0305_n(self):
        assert is_valid_table_value(305, 'N') is True

    def test_valid_code_0305_o(self):
        assert is_valid_table_value(305, 'O') is True

    def test_invalid_code_0305(self):
        assert is_valid_table_value(305, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0305(self):
        result = validate_table_value(305, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0305(self):
        result = validate_table_value(305, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0309:
    """Tests for table 0309: CoverageType"""

    def test_get_table_codes_0309(self):
        codes = get_table_codes(309)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0309_h(self):
        assert is_valid_table_value(309, 'H') is True

    def test_valid_code_0309_p(self):
        assert is_valid_table_value(309, 'P') is True

    def test_valid_code_0309_b(self):
        assert is_valid_table_value(309, 'B') is True

    def test_valid_code_0309_rx(self):
        assert is_valid_table_value(309, 'RX') is True

    def test_invalid_code_0309(self):
        assert is_valid_table_value(309, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0309(self):
        result = validate_table_value(309, 'H', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0309(self):
        result = validate_table_value(309, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0311:
    """Tests for table 0311: JobStatus"""

    def test_get_table_codes_0311(self):
        codes = get_table_codes(311)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0311_p(self):
        assert is_valid_table_value(311, 'P') is True

    def test_valid_code_0311_t(self):
        assert is_valid_table_value(311, 'T') is True

    def test_valid_code_0311_o(self):
        assert is_valid_table_value(311, 'O') is True

    def test_valid_code_0311_u(self):
        assert is_valid_table_value(311, 'U') is True

    def test_invalid_code_0311(self):
        assert is_valid_table_value(311, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0311(self):
        result = validate_table_value(311, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0311(self):
        result = validate_table_value(311, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0315:
    """Tests for table 0315: LivingWillCodes"""

    def test_get_table_codes_0315(self):
        codes = get_table_codes(315)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0315_y(self):
        assert is_valid_table_value(315, 'Y') is True

    def test_valid_code_0315_f(self):
        assert is_valid_table_value(315, 'F') is True

    def test_valid_code_0315_n(self):
        assert is_valid_table_value(315, 'N') is True

    def test_valid_code_0315_i(self):
        assert is_valid_table_value(315, 'I') is True

    def test_valid_code_0315_u(self):
        assert is_valid_table_value(315, 'U') is True

    def test_invalid_code_0315(self):
        assert is_valid_table_value(315, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0315(self):
        result = validate_table_value(315, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0315(self):
        result = validate_table_value(315, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0316:
    """Tests for table 0316: OrganDonorCodes"""

    def test_get_table_codes_0316(self):
        codes = get_table_codes(316)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0316_y(self):
        assert is_valid_table_value(316, 'Y') is True

    def test_valid_code_0316_f(self):
        assert is_valid_table_value(316, 'F') is True

    def test_valid_code_0316_n(self):
        assert is_valid_table_value(316, 'N') is True

    def test_valid_code_0316_i(self):
        assert is_valid_table_value(316, 'I') is True

    def test_valid_code_0316_r(self):
        assert is_valid_table_value(316, 'R') is True

    def test_invalid_code_0316(self):
        assert is_valid_table_value(316, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0316(self):
        result = validate_table_value(316, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0316(self):
        result = validate_table_value(316, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0317:
    """Tests for table 0317: Annotations"""

    def test_get_table_codes_0317(self):
        codes = get_table_codes(317)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0317_c_9900(self):
        assert is_valid_table_value(317, '9900') is True

    def test_valid_code_0317_c_9901(self):
        assert is_valid_table_value(317, '9901') is True

    def test_valid_code_0317_c_9902(self):
        assert is_valid_table_value(317, '9902') is True

    def test_valid_code_0317_c_9903(self):
        assert is_valid_table_value(317, '9903') is True

    def test_valid_code_0317_c_9904(self):
        assert is_valid_table_value(317, '9904') is True

    def test_invalid_code_0317(self):
        assert is_valid_table_value(317, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0317(self):
        result = validate_table_value(317, '9900', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0317(self):
        result = validate_table_value(317, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0321:
    """Tests for table 0321: DispenseMethod"""

    def test_get_table_codes_0321(self):
        codes = get_table_codes(321)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0321_tr(self):
        assert is_valid_table_value(321, 'TR') is True

    def test_valid_code_0321_ud(self):
        assert is_valid_table_value(321, 'UD') is True

    def test_valid_code_0321_f(self):
        assert is_valid_table_value(321, 'F') is True

    def test_valid_code_0321_ad(self):
        assert is_valid_table_value(321, 'AD') is True

    def test_invalid_code_0321(self):
        assert is_valid_table_value(321, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0321(self):
        result = validate_table_value(321, 'TR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0321(self):
        result = validate_table_value(321, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0322:
    """Tests for table 0322: CompletionStatus"""

    def test_get_table_codes_0322(self):
        codes = get_table_codes(322)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0322_cp(self):
        assert is_valid_table_value(322, 'CP') is True

    def test_valid_code_0322_re(self):
        assert is_valid_table_value(322, 'RE') is True

    def test_valid_code_0322_na(self):
        assert is_valid_table_value(322, 'NA') is True

    def test_valid_code_0322_pa(self):
        assert is_valid_table_value(322, 'PA') is True

    def test_invalid_code_0322(self):
        assert is_valid_table_value(322, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0322(self):
        result = validate_table_value(322, 'CP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0322(self):
        result = validate_table_value(322, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0323:
    """Tests for table 0323: ActionCodes"""

    def test_get_table_codes_0323(self):
        codes = get_table_codes(323)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0323_a(self):
        assert is_valid_table_value(323, 'A') is True

    def test_valid_code_0323_d(self):
        assert is_valid_table_value(323, 'D') is True

    def test_valid_code_0323_u(self):
        assert is_valid_table_value(323, 'U') is True

    def test_valid_code_0323_x(self):
        assert is_valid_table_value(323, 'X') is True

    def test_invalid_code_0323(self):
        assert is_valid_table_value(323, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0323(self):
        result = validate_table_value(323, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0323(self):
        result = validate_table_value(323, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0324:
    """Tests for table 0324: LocationCharacteristic"""

    def test_get_table_codes_0324(self):
        codes = get_table_codes(324)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0324_smk(self):
        assert is_valid_table_value(324, 'SMK') is True

    def test_valid_code_0324_lic(self):
        assert is_valid_table_value(324, 'LIC') is True

    def test_valid_code_0324_imp(self):
        assert is_valid_table_value(324, 'IMP') is True

    def test_valid_code_0324_sha(self):
        assert is_valid_table_value(324, 'SHA') is True

    def test_valid_code_0324_inf(self):
        assert is_valid_table_value(324, 'INF') is True

    def test_invalid_code_0324(self):
        assert is_valid_table_value(324, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0324(self):
        result = validate_table_value(324, 'SMK', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0324(self):
        result = validate_table_value(324, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0325:
    """Tests for table 0325: LocationRelationship"""

    def test_get_table_codes_0325(self):
        codes = get_table_codes(325)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0325_rx(self):
        assert is_valid_table_value(325, 'RX') is True

    def test_valid_code_0325_rx2(self):
        assert is_valid_table_value(325, 'RX2') is True

    def test_valid_code_0325_lab(self):
        assert is_valid_table_value(325, 'LAB') is True

    def test_valid_code_0325_lb2(self):
        assert is_valid_table_value(325, 'LB2') is True

    def test_valid_code_0325_dty(self):
        assert is_valid_table_value(325, 'DTY') is True

    def test_invalid_code_0325(self):
        assert is_valid_table_value(325, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0325(self):
        result = validate_table_value(325, 'RX', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0325(self):
        result = validate_table_value(325, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0326:
    """Tests for table 0326: VisitIndicator"""

    def test_get_table_codes_0326(self):
        codes = get_table_codes(326)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0326_a(self):
        assert is_valid_table_value(326, 'A') is True

    def test_valid_code_0326_v(self):
        assert is_valid_table_value(326, 'V') is True

    def test_invalid_code_0326(self):
        assert is_valid_table_value(326, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0326(self):
        result = validate_table_value(326, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0326(self):
        result = validate_table_value(326, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0329:
    """Tests for table 0329: QuantityMethod"""

    def test_get_table_codes_0329(self):
        codes = get_table_codes(329)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0329_a(self):
        assert is_valid_table_value(329, 'A') is True

    def test_valid_code_0329_e(self):
        assert is_valid_table_value(329, 'E') is True

    def test_invalid_code_0329(self):
        assert is_valid_table_value(329, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0329(self):
        result = validate_table_value(329, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0329(self):
        result = validate_table_value(329, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0330:
    """Tests for table 0330: MarketingBasis"""

    def test_get_table_codes_0330(self):
        codes = get_table_codes(330)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0330_c_510k(self):
        assert is_valid_table_value(330, '510K') is True

    def test_valid_code_0330_c_510e(self):
        assert is_valid_table_value(330, '510E') is True

    def test_valid_code_0330_pma(self):
        assert is_valid_table_value(330, 'PMA') is True

    def test_valid_code_0330_pre(self):
        assert is_valid_table_value(330, 'PRE') is True

    def test_valid_code_0330_txn(self):
        assert is_valid_table_value(330, 'TXN') is True

    def test_invalid_code_0330(self):
        assert is_valid_table_value(330, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0330(self):
        result = validate_table_value(330, '510K', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0330(self):
        result = validate_table_value(330, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0331:
    """Tests for table 0331: FacilityType"""

    def test_get_table_codes_0331(self):
        codes = get_table_codes(331)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0331_u(self):
        assert is_valid_table_value(331, 'U') is True

    def test_valid_code_0331_m(self):
        assert is_valid_table_value(331, 'M') is True

    def test_valid_code_0331_d(self):
        assert is_valid_table_value(331, 'D') is True

    def test_valid_code_0331_a(self):
        assert is_valid_table_value(331, 'A') is True

    def test_invalid_code_0331(self):
        assert is_valid_table_value(331, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0331(self):
        result = validate_table_value(331, 'U', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0331(self):
        result = validate_table_value(331, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0332:
    """Tests for table 0332: SourceType"""

    def test_get_table_codes_0332(self):
        codes = get_table_codes(332)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0332_i(self):
        assert is_valid_table_value(332, 'I') is True

    def test_valid_code_0332_a(self):
        assert is_valid_table_value(332, 'A') is True

    def test_invalid_code_0332(self):
        assert is_valid_table_value(332, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0332(self):
        result = validate_table_value(332, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0332(self):
        result = validate_table_value(332, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0334:
    """Tests for table 0334: DisabilityInformationRelationship"""

    def test_get_table_codes_0334(self):
        codes = get_table_codes(334)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0334_pt(self):
        assert is_valid_table_value(334, 'PT') is True

    def test_valid_code_0334_gt(self):
        assert is_valid_table_value(334, 'GT') is True

    def test_valid_code_0334_in(self):
        assert is_valid_table_value(334, 'IN') is True

    def test_valid_code_0334_ap(self):
        assert is_valid_table_value(334, 'AP') is True

    def test_invalid_code_0334(self):
        assert is_valid_table_value(334, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0334(self):
        result = validate_table_value(334, 'PT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0334(self):
        result = validate_table_value(334, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0335:
    """Tests for table 0335: RepeatPattern"""

    def test_get_table_codes_0335(self):
        codes = get_table_codes(335)
        assert codes is not None
        assert len(codes) == 28

    def test_valid_code_0335_q_integer_s(self):
        assert is_valid_table_value(335, 'Q<integer>S') is True

    def test_valid_code_0335_q_integer_m(self):
        assert is_valid_table_value(335, 'Q<integer>M') is True

    def test_valid_code_0335_q_integer_h(self):
        assert is_valid_table_value(335, 'Q<integer>H') is True

    def test_valid_code_0335_q_integer_d(self):
        assert is_valid_table_value(335, 'Q<integer>D') is True

    def test_valid_code_0335_q_integer_w(self):
        assert is_valid_table_value(335, 'Q<integer>W') is True

    def test_invalid_code_0335(self):
        assert is_valid_table_value(335, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0335(self):
        result = validate_table_value(335, 'Q<integer>S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0335(self):
        result = validate_table_value(335, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0336:
    """Tests for table 0336: ReferralReason"""

    def test_get_table_codes_0336(self):
        codes = get_table_codes(336)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0336_s(self):
        assert is_valid_table_value(336, 'S') is True

    def test_valid_code_0336_p(self):
        assert is_valid_table_value(336, 'P') is True

    def test_valid_code_0336_o(self):
        assert is_valid_table_value(336, 'O') is True

    def test_valid_code_0336_w(self):
        assert is_valid_table_value(336, 'W') is True

    def test_invalid_code_0336(self):
        assert is_valid_table_value(336, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0336(self):
        result = validate_table_value(336, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0336(self):
        result = validate_table_value(336, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0337:
    """Tests for table 0337: CertificationStatus"""

    def test_get_table_codes_0337(self):
        codes = get_table_codes(337)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0337_c(self):
        assert is_valid_table_value(337, 'C') is True

    def test_valid_code_0337_e(self):
        assert is_valid_table_value(337, 'E') is True

    def test_invalid_code_0337(self):
        assert is_valid_table_value(337, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0337(self):
        result = validate_table_value(337, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0337(self):
        result = validate_table_value(337, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0339:
    """Tests for table 0339: AdvancedBeneficiaryNotice"""

    def test_get_table_codes_0339(self):
        codes = get_table_codes(339)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0339_c_1(self):
        assert is_valid_table_value(339, '1') is True

    def test_valid_code_0339_c_2(self):
        assert is_valid_table_value(339, '2') is True

    def test_valid_code_0339_c_3(self):
        assert is_valid_table_value(339, '3') is True

    def test_valid_code_0339_c_4(self):
        assert is_valid_table_value(339, '4') is True

    def test_invalid_code_0339(self):
        assert is_valid_table_value(339, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0339(self):
        result = validate_table_value(339, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0339(self):
        result = validate_table_value(339, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0344:
    """Tests for table 0344: PatientsRelationshipToInsured"""

    def test_get_table_codes_0344(self):
        codes = get_table_codes(344)
        assert codes is not None
        assert len(codes) == 19

    def test_valid_code_0344_c_01(self):
        assert is_valid_table_value(344, '01') is True

    def test_valid_code_0344_c_02(self):
        assert is_valid_table_value(344, '02') is True

    def test_valid_code_0344_c_03(self):
        assert is_valid_table_value(344, '03') is True

    def test_valid_code_0344_c_04(self):
        assert is_valid_table_value(344, '04') is True

    def test_valid_code_0344_c_05(self):
        assert is_valid_table_value(344, '05') is True

    def test_invalid_code_0344(self):
        assert is_valid_table_value(344, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0344(self):
        result = validate_table_value(344, '01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0344(self):
        result = validate_table_value(344, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0353:
    """Tests for table 0353: CweStatuses"""

    def test_get_table_codes_0353(self):
        codes = get_table_codes(353)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0353_u(self):
        assert is_valid_table_value(353, 'U') is True

    def test_valid_code_0353_uask(self):
        assert is_valid_table_value(353, 'UASK') is True

    def test_valid_code_0353_nav(self):
        assert is_valid_table_value(353, 'NAV') is True

    def test_valid_code_0353_na(self):
        assert is_valid_table_value(353, 'NA') is True

    def test_valid_code_0353_nask(self):
        assert is_valid_table_value(353, 'NASK') is True

    def test_invalid_code_0353(self):
        assert is_valid_table_value(353, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0353(self):
        result = validate_table_value(353, 'U', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0353(self):
        result = validate_table_value(353, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0354:
    """Tests for table 0354: MessageStructure"""

    def test_get_table_codes_0354(self):
        codes = get_table_codes(354)
        assert codes is not None
        assert len(codes) == 316

    def test_valid_code_0354_omd_o01(self):
        assert is_valid_table_value(354, 'OMD_O01') is True

    def test_valid_code_0354_omn_o01(self):
        assert is_valid_table_value(354, 'OMN_O01') is True

    def test_valid_code_0354_oms_o01(self):
        assert is_valid_table_value(354, 'OMS_O01') is True

    def test_valid_code_0354_ord_o02(self):
        assert is_valid_table_value(354, 'ORD_O02') is True

    def test_valid_code_0354_orn_o02(self):
        assert is_valid_table_value(354, 'ORN_O02') is True

    def test_invalid_code_0354(self):
        assert is_valid_table_value(354, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0354(self):
        result = validate_table_value(354, 'OMD_O01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0354(self):
        result = validate_table_value(354, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0355:
    """Tests for table 0355: PrimaryKeyValueType"""

    def test_get_table_codes_0355(self):
        codes = get_table_codes(355)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0355_pl(self):
        assert is_valid_table_value(355, 'PL') is True

    def test_valid_code_0355_ce(self):
        assert is_valid_table_value(355, 'CE') is True

    def test_valid_code_0355_cwe(self):
        assert is_valid_table_value(355, 'CWE') is True

    def test_invalid_code_0355(self):
        assert is_valid_table_value(355, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0355(self):
        result = validate_table_value(355, 'PL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0355(self):
        result = validate_table_value(355, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0356:
    """Tests for table 0356: AlternateCharacterSetHandlingScheme"""

    def test_get_table_codes_0356(self):
        codes = get_table_codes(356)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0356_iso_2022_1994(self):
        assert is_valid_table_value(356, 'ISO 2022-1994') is True

    def test_valid_code_0356_c_2_3(self):
        assert is_valid_table_value(356, '2.3') is True

    def test_valid_code_0356_null(self):
        assert is_valid_table_value(356, '<null>') is True

    def test_invalid_code_0356(self):
        assert is_valid_table_value(356, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0356(self):
        result = validate_table_value(356, 'ISO 2022-1994', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0356(self):
        result = validate_table_value(356, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0357:
    """Tests for table 0357: MessageErrorCondition"""

    def test_get_table_codes_0357(self):
        codes = get_table_codes(357)
        assert codes is not None
        assert len(codes) == 16

    def test_valid_code_0357_c_0(self):
        assert is_valid_table_value(357, '0') is True

    def test_valid_code_0357_c_100(self):
        assert is_valid_table_value(357, '100') is True

    def test_valid_code_0357_c_101(self):
        assert is_valid_table_value(357, '101') is True

    def test_valid_code_0357_c_102(self):
        assert is_valid_table_value(357, '102') is True

    def test_valid_code_0357_c_103(self):
        assert is_valid_table_value(357, '103') is True

    def test_invalid_code_0357(self):
        assert is_valid_table_value(357, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0357(self):
        result = validate_table_value(357, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0357(self):
        result = validate_table_value(357, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0359:
    """Tests for table 0359: DiagnosisPriority"""

    def test_get_table_codes_0359(self):
        codes = get_table_codes(359)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0359_c_0(self):
        assert is_valid_table_value(359, '0') is True

    def test_valid_code_0359_c_1(self):
        assert is_valid_table_value(359, '1') is True

    def test_valid_code_0359_c_2_and_higher(self):
        assert is_valid_table_value(359, '2 and higher') is True

    def test_valid_code_0359_c_2(self):
        assert is_valid_table_value(359, '2 ...') is True

    def test_valid_code_0359_c_2_2(self):
        assert is_valid_table_value(359, '2') is True

    def test_invalid_code_0359(self):
        assert is_valid_table_value(359, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0359(self):
        result = validate_table_value(359, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0359(self):
        result = validate_table_value(359, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0360:
    """Tests for table 0360: DegreeLicenseCertificate"""

    def test_get_table_codes_0360(self):
        codes = get_table_codes(360)
        assert codes is not None
        assert len(codes) == 61

    def test_valid_code_0360_pn(self):
        assert is_valid_table_value(360, 'PN') is True

    def test_valid_code_0360_aas(self):
        assert is_valid_table_value(360, 'AAS') is True

    def test_valid_code_0360_aa(self):
        assert is_valid_table_value(360, 'AA') is True

    def test_valid_code_0360_aba(self):
        assert is_valid_table_value(360, 'ABA') is True

    def test_valid_code_0360_ae(self):
        assert is_valid_table_value(360, 'AE') is True

    def test_invalid_code_0360(self):
        assert is_valid_table_value(360, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0360(self):
        result = validate_table_value(360, 'PN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0360(self):
        result = validate_table_value(360, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0364:
    """Tests for table 0364: CommentType"""

    def test_get_table_codes_0364(self):
        codes = get_table_codes(364)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0364_pi(self):
        assert is_valid_table_value(364, 'PI') is True

    def test_valid_code_0364_ai(self):
        assert is_valid_table_value(364, 'AI') is True

    def test_valid_code_0364_gi(self):
        assert is_valid_table_value(364, 'GI') is True

    def test_valid_code_0364_c_1r(self):
        assert is_valid_table_value(364, '1R') is True

    def test_valid_code_0364_c_2r(self):
        assert is_valid_table_value(364, '2R') is True

    def test_invalid_code_0364(self):
        assert is_valid_table_value(364, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0364(self):
        result = validate_table_value(364, 'PI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0364(self):
        result = validate_table_value(364, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0365:
    """Tests for table 0365: EquipmentState"""

    def test_get_table_codes_0365(self):
        codes = get_table_codes(365)
        assert codes is not None
        assert len(codes) == 20

    def test_valid_code_0365_in(self):
        assert is_valid_table_value(365, 'IN') is True

    def test_valid_code_0365_co(self):
        assert is_valid_table_value(365, 'CO') is True

    def test_valid_code_0365_pu(self):
        assert is_valid_table_value(365, 'PU') is True

    def test_valid_code_0365_rs(self):
        assert is_valid_table_value(365, 'RS') is True

    def test_valid_code_0365_id(self):
        assert is_valid_table_value(365, 'ID') is True

    def test_invalid_code_0365(self):
        assert is_valid_table_value(365, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0365(self):
        result = validate_table_value(365, 'IN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0365(self):
        result = validate_table_value(365, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0366:
    """Tests for table 0366: LocalRemoteControlState"""

    def test_get_table_codes_0366(self):
        codes = get_table_codes(366)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0366_l(self):
        assert is_valid_table_value(366, 'L') is True

    def test_valid_code_0366_r(self):
        assert is_valid_table_value(366, 'R') is True

    def test_valid_code_0366_empty(self):
        assert is_valid_table_value(366, '...') is True

    def test_valid_code_0366_empty_2(self):
        assert is_valid_table_value(366, '…') is True

    def test_invalid_code_0366(self):
        assert is_valid_table_value(366, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0366(self):
        result = validate_table_value(366, 'L', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0366(self):
        result = validate_table_value(366, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0367:
    """Tests for table 0367: AlertLevel"""

    def test_get_table_codes_0367(self):
        codes = get_table_codes(367)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0367_n(self):
        assert is_valid_table_value(367, 'N') is True

    def test_valid_code_0367_w(self):
        assert is_valid_table_value(367, 'W') is True

    def test_valid_code_0367_s(self):
        assert is_valid_table_value(367, 'S') is True

    def test_valid_code_0367_c(self):
        assert is_valid_table_value(367, 'C') is True

    def test_valid_code_0367_empty(self):
        assert is_valid_table_value(367, '...') is True

    def test_invalid_code_0367(self):
        assert is_valid_table_value(367, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0367(self):
        result = validate_table_value(367, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0367(self):
        result = validate_table_value(367, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0368:
    """Tests for table 0368: RemoteControlCommand"""

    def test_get_table_codes_0368(self):
        codes = get_table_codes(368)
        assert codes is not None
        assert len(codes) == 21

    def test_valid_code_0368_sa(self):
        assert is_valid_table_value(368, 'SA') is True

    def test_valid_code_0368_lo(self):
        assert is_valid_table_value(368, 'LO') is True

    def test_valid_code_0368_un(self):
        assert is_valid_table_value(368, 'UN') is True

    def test_valid_code_0368_lk(self):
        assert is_valid_table_value(368, 'LK') is True

    def test_valid_code_0368_uc(self):
        assert is_valid_table_value(368, 'UC') is True

    def test_invalid_code_0368(self):
        assert is_valid_table_value(368, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0368(self):
        result = validate_table_value(368, 'SA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0368(self):
        result = validate_table_value(368, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0369:
    """Tests for table 0369: SpecimenRole"""

    def test_get_table_codes_0369(self):
        codes = get_table_codes(369)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0369_b(self):
        assert is_valid_table_value(369, 'B') is True

    def test_valid_code_0369_c(self):
        assert is_valid_table_value(369, 'C') is True

    def test_valid_code_0369_e(self):
        assert is_valid_table_value(369, 'E') is True

    def test_valid_code_0369_f(self):
        assert is_valid_table_value(369, 'F') is True

    def test_valid_code_0369_g(self):
        assert is_valid_table_value(369, 'G') is True

    def test_invalid_code_0369(self):
        assert is_valid_table_value(369, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0369(self):
        result = validate_table_value(369, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0369(self):
        result = validate_table_value(369, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0370:
    """Tests for table 0370: ContainerStatus"""

    def test_get_table_codes_0370(self):
        codes = get_table_codes(370)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0370_a(self):
        assert is_valid_table_value(370, 'A') is True

    def test_valid_code_0370_i(self):
        assert is_valid_table_value(370, 'I') is True

    def test_valid_code_0370_l(self):
        assert is_valid_table_value(370, 'L') is True

    def test_valid_code_0370_m(self):
        assert is_valid_table_value(370, 'M') is True

    def test_valid_code_0370_o(self):
        assert is_valid_table_value(370, 'O') is True

    def test_invalid_code_0370(self):
        assert is_valid_table_value(370, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0370(self):
        result = validate_table_value(370, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0370(self):
        result = validate_table_value(370, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0371:
    """Tests for table 0371: AdditivePreservative"""

    def test_get_table_codes_0371(self):
        codes = get_table_codes(371)
        assert codes is not None
        assert len(codes) == 57

    def test_valid_code_0371_f10(self):
        assert is_valid_table_value(371, 'F10') is True

    def test_valid_code_0371_c32(self):
        assert is_valid_table_value(371, 'C32') is True

    def test_valid_code_0371_c38(self):
        assert is_valid_table_value(371, 'C38') is True

    def test_valid_code_0371_hcl6(self):
        assert is_valid_table_value(371, 'HCL6') is True

    def test_valid_code_0371_acda(self):
        assert is_valid_table_value(371, 'ACDA') is True

    def test_invalid_code_0371(self):
        assert is_valid_table_value(371, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0371(self):
        result = validate_table_value(371, 'F10', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0371(self):
        result = validate_table_value(371, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0372:
    """Tests for table 0372: SpecimenComponent"""

    def test_get_table_codes_0372(self):
        codes = get_table_codes(372)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0372_sup(self):
        assert is_valid_table_value(372, 'SUP') is True

    def test_valid_code_0372_sed(self):
        assert is_valid_table_value(372, 'SED') is True

    def test_valid_code_0372_bld(self):
        assert is_valid_table_value(372, 'BLD') is True

    def test_valid_code_0372_bsep(self):
        assert is_valid_table_value(372, 'BSEP') is True

    def test_valid_code_0372_prp(self):
        assert is_valid_table_value(372, 'PRP') is True

    def test_invalid_code_0372(self):
        assert is_valid_table_value(372, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0372(self):
        result = validate_table_value(372, 'SUP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0372(self):
        result = validate_table_value(372, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0373:
    """Tests for table 0373: Treatment"""

    def test_get_table_codes_0373(self):
        codes = get_table_codes(373)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0373_ldlp(self):
        assert is_valid_table_value(373, 'LDLP') is True

    def test_valid_code_0373_reca(self):
        assert is_valid_table_value(373, 'RECA') is True

    def test_valid_code_0373_defb(self):
        assert is_valid_table_value(373, 'DEFB') is True

    def test_valid_code_0373_acid(self):
        assert is_valid_table_value(373, 'ACID') is True

    def test_valid_code_0373_neut(self):
        assert is_valid_table_value(373, 'NEUT') is True

    def test_invalid_code_0373(self):
        assert is_valid_table_value(373, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0373(self):
        result = validate_table_value(373, 'LDLP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0373(self):
        result = validate_table_value(373, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0374:
    """Tests for table 0374: SystemInducedContaminants"""

    def test_get_table_codes_0374(self):
        codes = get_table_codes(374)
        assert codes is not None
        assert len(codes) == 1

    def test_valid_code_0374_cntm(self):
        assert is_valid_table_value(374, 'CNTM') is True

    def test_invalid_code_0374(self):
        assert is_valid_table_value(374, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0374(self):
        result = validate_table_value(374, 'CNTM', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0374(self):
        result = validate_table_value(374, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0375:
    """Tests for table 0375: ArtificialBlood"""

    def test_get_table_codes_0375(self):
        codes = get_table_codes(375)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0375_sfhb(self):
        assert is_valid_table_value(375, 'SFHB') is True

    def test_valid_code_0375_flur(self):
        assert is_valid_table_value(375, 'FLUR') is True

    def test_invalid_code_0375(self):
        assert is_valid_table_value(375, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0375(self):
        result = validate_table_value(375, 'SFHB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0375(self):
        result = validate_table_value(375, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0376:
    """Tests for table 0376: SpecialHandling"""

    def test_get_table_codes_0376(self):
        codes = get_table_codes(376)
        assert codes is not None
        assert len(codes) == 17

    def test_valid_code_0376_c37(self):
        assert is_valid_table_value(376, 'C37') is True

    def test_valid_code_0376_amb(self):
        assert is_valid_table_value(376, 'AMB') is True

    def test_valid_code_0376_camb(self):
        assert is_valid_table_value(376, 'CAMB') is True

    def test_valid_code_0376_ref(self):
        assert is_valid_table_value(376, 'REF') is True

    def test_valid_code_0376_cref(self):
        assert is_valid_table_value(376, 'CREF') is True

    def test_invalid_code_0376(self):
        assert is_valid_table_value(376, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0376(self):
        result = validate_table_value(376, 'C37', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0376(self):
        result = validate_table_value(376, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0377:
    """Tests for table 0377: EnvironmentalFactors"""

    def test_get_table_codes_0377(self):
        codes = get_table_codes(377)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0377_atm(self):
        assert is_valid_table_value(377, 'ATM') is True

    def test_valid_code_0377_a60(self):
        assert is_valid_table_value(377, 'A60') is True

    def test_invalid_code_0377(self):
        assert is_valid_table_value(377, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0377(self):
        result = validate_table_value(377, 'ATM', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0377(self):
        result = validate_table_value(377, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0383:
    """Tests for table 0383: SubstanceStatus"""

    def test_get_table_codes_0383(self):
        codes = get_table_codes(383)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0383_ew(self):
        assert is_valid_table_value(383, 'EW') is True

    def test_valid_code_0383_ee(self):
        assert is_valid_table_value(383, 'EE') is True

    def test_valid_code_0383_cw(self):
        assert is_valid_table_value(383, 'CW') is True

    def test_valid_code_0383_ce(self):
        assert is_valid_table_value(383, 'CE') is True

    def test_valid_code_0383_qw(self):
        assert is_valid_table_value(383, 'QW') is True

    def test_invalid_code_0383(self):
        assert is_valid_table_value(383, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0383(self):
        result = validate_table_value(383, 'EW', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0383(self):
        result = validate_table_value(383, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0384:
    """Tests for table 0384: SubstanceType"""

    def test_get_table_codes_0384(self):
        codes = get_table_codes(384)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0384_sr(self):
        assert is_valid_table_value(384, 'SR') is True

    def test_valid_code_0384_mr(self):
        assert is_valid_table_value(384, 'MR') is True

    def test_valid_code_0384_di(self):
        assert is_valid_table_value(384, 'DI') is True

    def test_valid_code_0384_pt(self):
        assert is_valid_table_value(384, 'PT') is True

    def test_valid_code_0384_rc(self):
        assert is_valid_table_value(384, 'RC') is True

    def test_invalid_code_0384(self):
        assert is_valid_table_value(384, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0384(self):
        result = validate_table_value(384, 'SR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0384(self):
        result = validate_table_value(384, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0387:
    """Tests for table 0387: CommandResponse"""

    def test_get_table_codes_0387(self):
        codes = get_table_codes(387)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0387_ok(self):
        assert is_valid_table_value(387, 'OK') is True

    def test_valid_code_0387_ti(self):
        assert is_valid_table_value(387, 'TI') is True

    def test_valid_code_0387_er(self):
        assert is_valid_table_value(387, 'ER') is True

    def test_valid_code_0387_st(self):
        assert is_valid_table_value(387, 'ST') is True

    def test_valid_code_0387_un(self):
        assert is_valid_table_value(387, 'UN') is True

    def test_invalid_code_0387(self):
        assert is_valid_table_value(387, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0387(self):
        result = validate_table_value(387, 'OK', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0387(self):
        result = validate_table_value(387, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0388:
    """Tests for table 0388: ProcessingType"""

    def test_get_table_codes_0388(self):
        codes = get_table_codes(388)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0388_p(self):
        assert is_valid_table_value(388, 'P') is True

    def test_valid_code_0388_e(self):
        assert is_valid_table_value(388, 'E') is True

    def test_invalid_code_0388(self):
        assert is_valid_table_value(388, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0388(self):
        result = validate_table_value(388, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0388(self):
        result = validate_table_value(388, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0389:
    """Tests for table 0389: AnalyteRepeatStatus"""

    def test_get_table_codes_0389(self):
        codes = get_table_codes(389)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0389_o(self):
        assert is_valid_table_value(389, 'O') is True

    def test_valid_code_0389_r(self):
        assert is_valid_table_value(389, 'R') is True

    def test_valid_code_0389_d(self):
        assert is_valid_table_value(389, 'D') is True

    def test_valid_code_0389_f(self):
        assert is_valid_table_value(389, 'F') is True

    def test_invalid_code_0389(self):
        assert is_valid_table_value(389, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0389(self):
        result = validate_table_value(389, 'O', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0389(self):
        result = validate_table_value(389, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0391:
    """Tests for table 0391: SegmentGroup"""

    def test_get_table_codes_0391(self):
        codes = get_table_codes(391)
        assert codes is not None
        assert len(codes) == 148

    def test_valid_code_0391_pidg(self):
        assert is_valid_table_value(391, 'PIDG') is True

    def test_valid_code_0391_administration(self):
        assert is_valid_table_value(391, 'ADMINISTRATION') is True

    def test_valid_code_0391_obrg(self):
        assert is_valid_table_value(391, 'OBRG') is True

    def test_valid_code_0391_allergy(self):
        assert is_valid_table_value(391, 'ALLERGY') is True

    def test_valid_code_0391_orcg(self):
        assert is_valid_table_value(391, 'ORCG') is True

    def test_invalid_code_0391(self):
        assert is_valid_table_value(391, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0391(self):
        result = validate_table_value(391, 'PIDG', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0391(self):
        result = validate_table_value(391, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0392:
    """Tests for table 0392: MatchReason"""

    def test_get_table_codes_0392(self):
        codes = get_table_codes(392)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0392_db(self):
        assert is_valid_table_value(392, 'DB') is True

    def test_valid_code_0392_na(self):
        assert is_valid_table_value(392, 'NA') is True

    def test_valid_code_0392_np(self):
        assert is_valid_table_value(392, 'NP') is True

    def test_valid_code_0392_ss(self):
        assert is_valid_table_value(392, 'SS') is True

    def test_invalid_code_0392(self):
        assert is_valid_table_value(392, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0392(self):
        result = validate_table_value(392, 'DB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0392(self):
        result = validate_table_value(392, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0393:
    """Tests for table 0393: MatchAlgorithms"""

    def test_get_table_codes_0393(self):
        codes = get_table_codes(393)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0393_linksoft_2_01(self):
        assert is_valid_table_value(393, 'LINKSOFT_2.01') is True

    def test_valid_code_0393_matchware_1_2(self):
        assert is_valid_table_value(393, 'MATCHWARE_1.2') is True

    def test_invalid_code_0393(self):
        assert is_valid_table_value(393, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0393(self):
        result = validate_table_value(393, 'LINKSOFT_2.01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0393(self):
        result = validate_table_value(393, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0394:
    """Tests for table 0394: ResponseModality"""

    def test_get_table_codes_0394(self):
        codes = get_table_codes(394)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0394_r(self):
        assert is_valid_table_value(394, 'R') is True

    def test_valid_code_0394_t(self):
        assert is_valid_table_value(394, 'T') is True

    def test_valid_code_0394_b(self):
        assert is_valid_table_value(394, 'B') is True

    def test_invalid_code_0394(self):
        assert is_valid_table_value(394, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0394(self):
        result = validate_table_value(394, 'R', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0394(self):
        result = validate_table_value(394, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0395:
    """Tests for table 0395: ModifyIndicator"""

    def test_get_table_codes_0395(self):
        codes = get_table_codes(395)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0395_n(self):
        assert is_valid_table_value(395, 'N') is True

    def test_valid_code_0395_m(self):
        assert is_valid_table_value(395, 'M') is True

    def test_invalid_code_0395(self):
        assert is_valid_table_value(395, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0395(self):
        result = validate_table_value(395, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0395(self):
        result = validate_table_value(395, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0396:
    """Tests for table 0396: CodingSystem"""

    def test_get_table_codes_0396(self):
        codes = get_table_codes(396)
        assert codes is not None
        assert len(codes) == 254

    def test_valid_code_0396_general_code(self):
        assert is_valid_table_value(396, 'General code') is True

    def test_valid_code_0396_alphaid2012(self):
        assert is_valid_table_value(396, 'ALPHAID2012') is True

    def test_valid_code_0396_alphaid2013(self):
        assert is_valid_table_value(396, 'ALPHAID2013') is True

    def test_valid_code_0396_alphaid2014(self):
        assert is_valid_table_value(396, 'ALPHAID2014') is True

    def test_valid_code_0396_alphaid2015(self):
        assert is_valid_table_value(396, 'ALPHAID2015') is True

    def test_invalid_code_0396(self):
        assert is_valid_table_value(396, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0396(self):
        result = validate_table_value(396, 'General code', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0396(self):
        result = validate_table_value(396, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0397:
    """Tests for table 0397: Sequencing"""

    def test_get_table_codes_0397(self):
        codes = get_table_codes(397)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0397_a(self):
        assert is_valid_table_value(397, 'A') is True

    def test_valid_code_0397_an(self):
        assert is_valid_table_value(397, 'AN') is True

    def test_valid_code_0397_d(self):
        assert is_valid_table_value(397, 'D') is True

    def test_valid_code_0397_dn(self):
        assert is_valid_table_value(397, 'DN') is True

    def test_valid_code_0397_n(self):
        assert is_valid_table_value(397, 'N') is True

    def test_invalid_code_0397(self):
        assert is_valid_table_value(397, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0397(self):
        result = validate_table_value(397, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0397(self):
        result = validate_table_value(397, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0398:
    """Tests for table 0398: ContinuationStyle"""

    def test_get_table_codes_0398(self):
        codes = get_table_codes(398)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0398_f(self):
        assert is_valid_table_value(398, 'F') is True

    def test_valid_code_0398_i(self):
        assert is_valid_table_value(398, 'I') is True

    def test_invalid_code_0398(self):
        assert is_valid_table_value(398, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0398(self):
        result = validate_table_value(398, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0398(self):
        result = validate_table_value(398, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0401:
    """Tests for table 0401: GovernmentReimbursementProgram"""

    def test_get_table_codes_0401(self):
        codes = get_table_codes(401)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0401_mm(self):
        assert is_valid_table_value(401, 'MM') is True

    def test_valid_code_0401_c(self):
        assert is_valid_table_value(401, 'C') is True

    def test_invalid_code_0401(self):
        assert is_valid_table_value(401, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0401(self):
        result = validate_table_value(401, 'MM', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0401(self):
        result = validate_table_value(401, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0402:
    """Tests for table 0402: SchoolType"""

    def test_get_table_codes_0402(self):
        codes = get_table_codes(402)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0402_d(self):
        assert is_valid_table_value(402, 'D') is True

    def test_valid_code_0402_g(self):
        assert is_valid_table_value(402, 'G') is True

    def test_valid_code_0402_m(self):
        assert is_valid_table_value(402, 'M') is True

    def test_valid_code_0402_u(self):
        assert is_valid_table_value(402, 'U') is True

    def test_invalid_code_0402(self):
        assert is_valid_table_value(402, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0402(self):
        result = validate_table_value(402, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0402(self):
        result = validate_table_value(402, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0403:
    """Tests for table 0403: LanguageAbility"""

    def test_get_table_codes_0403(self):
        codes = get_table_codes(403)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0403_c_1(self):
        assert is_valid_table_value(403, '1') is True

    def test_valid_code_0403_c_2(self):
        assert is_valid_table_value(403, '2') is True

    def test_valid_code_0403_c_3(self):
        assert is_valid_table_value(403, '3') is True

    def test_valid_code_0403_c_4(self):
        assert is_valid_table_value(403, '4') is True

    def test_valid_code_0403_c_5(self):
        assert is_valid_table_value(403, '5') is True

    def test_invalid_code_0403(self):
        assert is_valid_table_value(403, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0403(self):
        result = validate_table_value(403, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0403(self):
        result = validate_table_value(403, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0404:
    """Tests for table 0404: LanguageProficiency"""

    def test_get_table_codes_0404(self):
        codes = get_table_codes(404)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0404_c_1(self):
        assert is_valid_table_value(404, '1') is True

    def test_valid_code_0404_c_2(self):
        assert is_valid_table_value(404, '2') is True

    def test_valid_code_0404_c_3(self):
        assert is_valid_table_value(404, '3') is True

    def test_valid_code_0404_c_4(self):
        assert is_valid_table_value(404, '4') is True

    def test_valid_code_0404_c_5(self):
        assert is_valid_table_value(404, '5') is True

    def test_invalid_code_0404(self):
        assert is_valid_table_value(404, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0404(self):
        result = validate_table_value(404, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0404(self):
        result = validate_table_value(404, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0406:
    """Tests for table 0406: OrganizationUnitType"""

    def test_get_table_codes_0406(self):
        codes = get_table_codes(406)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0406_h(self):
        assert is_valid_table_value(406, 'H') is True

    def test_valid_code_0406_o(self):
        assert is_valid_table_value(406, 'O') is True

    def test_valid_code_0406_c_1(self):
        assert is_valid_table_value(406, '1') is True

    def test_valid_code_0406_c_2(self):
        assert is_valid_table_value(406, '2') is True

    def test_valid_code_0406_c_3(self):
        assert is_valid_table_value(406, '3') is True

    def test_invalid_code_0406(self):
        assert is_valid_table_value(406, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0406(self):
        result = validate_table_value(406, 'H', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0406(self):
        result = validate_table_value(406, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0409:
    """Tests for table 0409: ApplicationChangeType"""

    def test_get_table_codes_0409(self):
        codes = get_table_codes(409)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0409_su(self):
        assert is_valid_table_value(409, 'SU') is True

    def test_valid_code_0409_sd(self):
        assert is_valid_table_value(409, 'SD') is True

    def test_valid_code_0409_m(self):
        assert is_valid_table_value(409, 'M') is True

    def test_invalid_code_0409(self):
        assert is_valid_table_value(409, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0409(self):
        result = validate_table_value(409, 'SU', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0409(self):
        result = validate_table_value(409, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0415:
    """Tests for table 0415: DrgTransferType"""

    def test_get_table_codes_0415(self):
        codes = get_table_codes(415)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0415_n(self):
        assert is_valid_table_value(415, 'N') is True

    def test_valid_code_0415_e(self):
        assert is_valid_table_value(415, 'E') is True

    def test_invalid_code_0415(self):
        assert is_valid_table_value(415, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0415(self):
        result = validate_table_value(415, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0415(self):
        result = validate_table_value(415, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0416:
    """Tests for table 0416: ProcedureDrgType"""

    def test_get_table_codes_0416(self):
        codes = get_table_codes(416)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0416_c_1(self):
        assert is_valid_table_value(416, '1') is True

    def test_valid_code_0416_c_2(self):
        assert is_valid_table_value(416, '2') is True

    def test_valid_code_0416_c_3(self):
        assert is_valid_table_value(416, '3') is True

    def test_valid_code_0416_c_4(self):
        assert is_valid_table_value(416, '4') is True

    def test_valid_code_0416_c_5(self):
        assert is_valid_table_value(416, '5') is True

    def test_invalid_code_0416(self):
        assert is_valid_table_value(416, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0416(self):
        result = validate_table_value(416, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0416(self):
        result = validate_table_value(416, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0417:
    """Tests for table 0417: TissueType"""

    def test_get_table_codes_0417(self):
        codes = get_table_codes(417)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0417_c_1(self):
        assert is_valid_table_value(417, '1') is True

    def test_valid_code_0417_c_2(self):
        assert is_valid_table_value(417, '2') is True

    def test_valid_code_0417_c_3(self):
        assert is_valid_table_value(417, '3') is True

    def test_valid_code_0417_c_4(self):
        assert is_valid_table_value(417, '4') is True

    def test_valid_code_0417_c_5(self):
        assert is_valid_table_value(417, '5') is True

    def test_invalid_code_0417(self):
        assert is_valid_table_value(417, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0417(self):
        result = validate_table_value(417, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0417(self):
        result = validate_table_value(417, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0418:
    """Tests for table 0418: ProcedurePriority"""

    def test_get_table_codes_0418(self):
        codes = get_table_codes(418)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0418_c_0(self):
        assert is_valid_table_value(418, '0') is True

    def test_valid_code_0418_c_1(self):
        assert is_valid_table_value(418, '1') is True

    def test_valid_code_0418_c_2(self):
        assert is_valid_table_value(418, '2') is True

    def test_valid_code_0418_empty(self):
        assert is_valid_table_value(418, '…') is True

    def test_valid_code_0418_empty_2(self):
        assert is_valid_table_value(418, '...') is True

    def test_invalid_code_0418(self):
        assert is_valid_table_value(418, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0418(self):
        result = validate_table_value(418, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0418(self):
        result = validate_table_value(418, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0421:
    """Tests for table 0421: SeverityOfIllness"""

    def test_get_table_codes_0421(self):
        codes = get_table_codes(421)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0421_mi(self):
        assert is_valid_table_value(421, 'MI') is True

    def test_valid_code_0421_mo(self):
        assert is_valid_table_value(421, 'MO') is True

    def test_valid_code_0421_se(self):
        assert is_valid_table_value(421, 'SE') is True

    def test_invalid_code_0421(self):
        assert is_valid_table_value(421, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0421(self):
        result = validate_table_value(421, 'MI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0421(self):
        result = validate_table_value(421, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0422:
    """Tests for table 0422: TriageType"""

    def test_get_table_codes_0422(self):
        codes = get_table_codes(422)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0422_c_1(self):
        assert is_valid_table_value(422, '1') is True

    def test_valid_code_0422_c_2(self):
        assert is_valid_table_value(422, '2') is True

    def test_valid_code_0422_c_3(self):
        assert is_valid_table_value(422, '3') is True

    def test_valid_code_0422_c_4(self):
        assert is_valid_table_value(422, '4') is True

    def test_valid_code_0422_c_5(self):
        assert is_valid_table_value(422, '5') is True

    def test_invalid_code_0422(self):
        assert is_valid_table_value(422, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0422(self):
        result = validate_table_value(422, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0422(self):
        result = validate_table_value(422, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0423:
    """Tests for table 0423: CaseCategory"""

    def test_get_table_codes_0423(self):
        codes = get_table_codes(423)
        assert codes is not None
        assert len(codes) == 1

    def test_valid_code_0423_d(self):
        assert is_valid_table_value(423, 'D') is True

    def test_invalid_code_0423(self):
        assert is_valid_table_value(423, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0423(self):
        result = validate_table_value(423, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0423(self):
        result = validate_table_value(423, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0424:
    """Tests for table 0424: GestationCategory"""

    def test_get_table_codes_0424(self):
        codes = get_table_codes(424)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0424_c_1(self):
        assert is_valid_table_value(424, '1') is True

    def test_valid_code_0424_c_2(self):
        assert is_valid_table_value(424, '2') is True

    def test_valid_code_0424_c_3(self):
        assert is_valid_table_value(424, '3') is True

    def test_invalid_code_0424(self):
        assert is_valid_table_value(424, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0424(self):
        result = validate_table_value(424, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0424(self):
        result = validate_table_value(424, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0425:
    """Tests for table 0425: NewbornType"""

    def test_get_table_codes_0425(self):
        codes = get_table_codes(425)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0425_c_5(self):
        assert is_valid_table_value(425, '5') is True

    def test_valid_code_0425_c_3(self):
        assert is_valid_table_value(425, '3') is True

    def test_valid_code_0425_c_1(self):
        assert is_valid_table_value(425, '1') is True

    def test_valid_code_0425_c_4(self):
        assert is_valid_table_value(425, '4') is True

    def test_valid_code_0425_c_2(self):
        assert is_valid_table_value(425, '2') is True

    def test_invalid_code_0425(self):
        assert is_valid_table_value(425, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0425(self):
        result = validate_table_value(425, '5', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0425(self):
        result = validate_table_value(425, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0426:
    """Tests for table 0426: BloodProduct"""

    def test_get_table_codes_0426(self):
        codes = get_table_codes(426)
        assert codes is not None
        assert len(codes) == 15

    def test_valid_code_0426_cryo(self):
        assert is_valid_table_value(426, 'CRYO') is True

    def test_valid_code_0426_cryop(self):
        assert is_valid_table_value(426, 'CRYOP') is True

    def test_valid_code_0426_ffp(self):
        assert is_valid_table_value(426, 'FFP') is True

    def test_valid_code_0426_ffpth(self):
        assert is_valid_table_value(426, 'FFPTH') is True

    def test_valid_code_0426_pc(self):
        assert is_valid_table_value(426, 'PC') is True

    def test_invalid_code_0426(self):
        assert is_valid_table_value(426, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0426(self):
        result = validate_table_value(426, 'CRYO', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0426(self):
        result = validate_table_value(426, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0427:
    """Tests for table 0427: RiskManagementIncident"""

    def test_get_table_codes_0427(self):
        codes = get_table_codes(427)
        assert codes is not None
        assert len(codes) == 14

    def test_valid_code_0427_b(self):
        assert is_valid_table_value(427, 'B') is True

    def test_valid_code_0427_c(self):
        assert is_valid_table_value(427, 'C') is True

    def test_valid_code_0427_d(self):
        assert is_valid_table_value(427, 'D') is True

    def test_valid_code_0427_e(self):
        assert is_valid_table_value(427, 'E') is True

    def test_valid_code_0427_f(self):
        assert is_valid_table_value(427, 'F') is True

    def test_invalid_code_0427(self):
        assert is_valid_table_value(427, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0427(self):
        result = validate_table_value(427, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0427(self):
        result = validate_table_value(427, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0428:
    """Tests for table 0428: IncidentType"""

    def test_get_table_codes_0428(self):
        codes = get_table_codes(428)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0428_p(self):
        assert is_valid_table_value(428, 'P') is True

    def test_valid_code_0428_u(self):
        assert is_valid_table_value(428, 'U') is True

    def test_valid_code_0428_o(self):
        assert is_valid_table_value(428, 'O') is True

    def test_invalid_code_0428(self):
        assert is_valid_table_value(428, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0428(self):
        result = validate_table_value(428, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0428(self):
        result = validate_table_value(428, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0429:
    """Tests for table 0429: ProductionClass"""

    def test_get_table_codes_0429(self):
        codes = get_table_codes(429)
        assert codes is not None
        assert len(codes) == 12

    def test_valid_code_0429_br(self):
        assert is_valid_table_value(429, 'BR') is True

    def test_valid_code_0429_da(self):
        assert is_valid_table_value(429, 'DA') is True

    def test_valid_code_0429_dr(self):
        assert is_valid_table_value(429, 'DR') is True

    def test_valid_code_0429_du(self):
        assert is_valid_table_value(429, 'DU') is True

    def test_valid_code_0429_ly(self):
        assert is_valid_table_value(429, 'LY') is True

    def test_invalid_code_0429(self):
        assert is_valid_table_value(429, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0429(self):
        result = validate_table_value(429, 'BR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0429(self):
        result = validate_table_value(429, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0430:
    """Tests for table 0430: ArrivalMode"""

    def test_get_table_codes_0430(self):
        codes = get_table_codes(430)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0430_a(self):
        assert is_valid_table_value(430, 'A') is True

    def test_valid_code_0430_c(self):
        assert is_valid_table_value(430, 'C') is True

    def test_valid_code_0430_f(self):
        assert is_valid_table_value(430, 'F') is True

    def test_valid_code_0430_h(self):
        assert is_valid_table_value(430, 'H') is True

    def test_valid_code_0430_p(self):
        assert is_valid_table_value(430, 'P') is True

    def test_invalid_code_0430(self):
        assert is_valid_table_value(430, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0430(self):
        result = validate_table_value(430, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0430(self):
        result = validate_table_value(430, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0431:
    """Tests for table 0431: RecreationalDrugType"""

    def test_get_table_codes_0431(self):
        codes = get_table_codes(431)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0431_a(self):
        assert is_valid_table_value(431, 'A') is True

    def test_valid_code_0431_k(self):
        assert is_valid_table_value(431, 'K') is True

    def test_valid_code_0431_m(self):
        assert is_valid_table_value(431, 'M') is True

    def test_valid_code_0431_t(self):
        assert is_valid_table_value(431, 'T') is True

    def test_valid_code_0431_c(self):
        assert is_valid_table_value(431, 'C') is True

    def test_invalid_code_0431(self):
        assert is_valid_table_value(431, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0431(self):
        result = validate_table_value(431, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0431(self):
        result = validate_table_value(431, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0432:
    """Tests for table 0432: AdmissionLevelOfCare"""

    def test_get_table_codes_0432(self):
        codes = get_table_codes(432)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0432_ac(self):
        assert is_valid_table_value(432, 'AC') is True

    def test_valid_code_0432_ch(self):
        assert is_valid_table_value(432, 'CH') is True

    def test_valid_code_0432_co(self):
        assert is_valid_table_value(432, 'CO') is True

    def test_valid_code_0432_cr(self):
        assert is_valid_table_value(432, 'CR') is True

    def test_valid_code_0432_im(self):
        assert is_valid_table_value(432, 'IM') is True

    def test_invalid_code_0432(self):
        assert is_valid_table_value(432, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0432(self):
        result = validate_table_value(432, 'AC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0432(self):
        result = validate_table_value(432, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0433:
    """Tests for table 0433: Precaution"""

    def test_get_table_codes_0433(self):
        codes = get_table_codes(433)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0433_a(self):
        assert is_valid_table_value(433, 'A') is True

    def test_valid_code_0433_b(self):
        assert is_valid_table_value(433, 'B') is True

    def test_valid_code_0433_c(self):
        assert is_valid_table_value(433, 'C') is True

    def test_valid_code_0433_d(self):
        assert is_valid_table_value(433, 'D') is True

    def test_valid_code_0433_i(self):
        assert is_valid_table_value(433, 'I') is True

    def test_invalid_code_0433(self):
        assert is_valid_table_value(433, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0433(self):
        result = validate_table_value(433, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0433(self):
        result = validate_table_value(433, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0434:
    """Tests for table 0434: PatientCondition"""

    def test_get_table_codes_0434(self):
        codes = get_table_codes(434)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0434_a(self):
        assert is_valid_table_value(434, 'A') is True

    def test_valid_code_0434_c(self):
        assert is_valid_table_value(434, 'C') is True

    def test_valid_code_0434_p(self):
        assert is_valid_table_value(434, 'P') is True

    def test_valid_code_0434_s(self):
        assert is_valid_table_value(434, 'S') is True

    def test_valid_code_0434_o(self):
        assert is_valid_table_value(434, 'O') is True

    def test_invalid_code_0434(self):
        assert is_valid_table_value(434, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0434(self):
        result = validate_table_value(434, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0434(self):
        result = validate_table_value(434, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0435:
    """Tests for table 0435: AdvanceDirective"""

    def test_get_table_codes_0435(self):
        codes = get_table_codes(435)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0435_dnr(self):
        assert is_valid_table_value(435, 'DNR') is True

    def test_valid_code_0435_n(self):
        assert is_valid_table_value(435, 'N') is True

    def test_invalid_code_0435(self):
        assert is_valid_table_value(435, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0435(self):
        result = validate_table_value(435, 'DNR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0435(self):
        result = validate_table_value(435, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0436:
    """Tests for table 0436: SensitivityToCausativeAgent"""

    def test_get_table_codes_0436(self):
        codes = get_table_codes(436)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0436_ad(self):
        assert is_valid_table_value(436, 'AD') is True

    def test_valid_code_0436_al(self):
        assert is_valid_table_value(436, 'AL') is True

    def test_valid_code_0436_ct(self):
        assert is_valid_table_value(436, 'CT') is True

    def test_valid_code_0436_in(self):
        assert is_valid_table_value(436, 'IN') is True

    def test_valid_code_0436_se(self):
        assert is_valid_table_value(436, 'SE') is True

    def test_invalid_code_0436(self):
        assert is_valid_table_value(436, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0436(self):
        result = validate_table_value(436, 'AD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0436(self):
        result = validate_table_value(436, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0437:
    """Tests for table 0437: AlertDevice"""

    def test_get_table_codes_0437(self):
        codes = get_table_codes(437)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0437_b(self):
        assert is_valid_table_value(437, 'B') is True

    def test_valid_code_0437_n(self):
        assert is_valid_table_value(437, 'N') is True

    def test_valid_code_0437_w(self):
        assert is_valid_table_value(437, 'W') is True

    def test_invalid_code_0437(self):
        assert is_valid_table_value(437, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0437(self):
        result = validate_table_value(437, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0437(self):
        result = validate_table_value(437, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0438:
    """Tests for table 0438: AllergyClinicalStatus"""

    def test_get_table_codes_0438(self):
        codes = get_table_codes(438)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0438_u(self):
        assert is_valid_table_value(438, 'U') is True

    def test_valid_code_0438_p(self):
        assert is_valid_table_value(438, 'P') is True

    def test_valid_code_0438_s(self):
        assert is_valid_table_value(438, 'S') is True

    def test_valid_code_0438_c(self):
        assert is_valid_table_value(438, 'C') is True

    def test_valid_code_0438_i(self):
        assert is_valid_table_value(438, 'I') is True

    def test_invalid_code_0438(self):
        assert is_valid_table_value(438, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0438(self):
        result = validate_table_value(438, 'U', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0438(self):
        result = validate_table_value(438, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0440:
    """Tests for table 0440: DataTypes"""

    def test_get_table_codes_0440(self):
        codes = get_table_codes(440)
        assert codes is not None
        assert len(codes) == 96

    def test_valid_code_0440_ad(self):
        assert is_valid_table_value(440, 'AD') is True

    def test_valid_code_0440_aui(self):
        assert is_valid_table_value(440, 'AUI') is True

    def test_valid_code_0440_ccd(self):
        assert is_valid_table_value(440, 'CCD') is True

    def test_valid_code_0440_ccp(self):
        assert is_valid_table_value(440, 'CCP') is True

    def test_valid_code_0440_cd(self):
        assert is_valid_table_value(440, 'CD') is True

    def test_invalid_code_0440(self):
        assert is_valid_table_value(440, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0440(self):
        result = validate_table_value(440, 'AD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0440(self):
        result = validate_table_value(440, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0441:
    """Tests for table 0441: ImmunizationRegistryStatus"""

    def test_get_table_codes_0441(self):
        codes = get_table_codes(441)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0441_a(self):
        assert is_valid_table_value(441, 'A') is True

    def test_valid_code_0441_i(self):
        assert is_valid_table_value(441, 'I') is True

    def test_valid_code_0441_l(self):
        assert is_valid_table_value(441, 'L') is True

    def test_valid_code_0441_m(self):
        assert is_valid_table_value(441, 'M') is True

    def test_valid_code_0441_p(self):
        assert is_valid_table_value(441, 'P') is True

    def test_invalid_code_0441(self):
        assert is_valid_table_value(441, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0441(self):
        result = validate_table_value(441, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0441(self):
        result = validate_table_value(441, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0442:
    """Tests for table 0442: LocationServiceType"""

    def test_get_table_codes_0442(self):
        codes = get_table_codes(442)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0442_d(self):
        assert is_valid_table_value(442, 'D') is True

    def test_valid_code_0442_t(self):
        assert is_valid_table_value(442, 'T') is True

    def test_valid_code_0442_p(self):
        assert is_valid_table_value(442, 'P') is True

    def test_valid_code_0442_e(self):
        assert is_valid_table_value(442, 'E') is True

    def test_invalid_code_0442(self):
        assert is_valid_table_value(442, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0442(self):
        result = validate_table_value(442, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0442(self):
        result = validate_table_value(442, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0443:
    """Tests for table 0443: ProviderRole"""

    def test_get_table_codes_0443(self):
        codes = get_table_codes(443)
        assert codes is not None
        assert len(codes) == 23

    def test_valid_code_0443_ad(self):
        assert is_valid_table_value(443, 'AD') is True

    def test_valid_code_0443_ap(self):
        assert is_valid_table_value(443, 'AP') is True

    def test_valid_code_0443_at(self):
        assert is_valid_table_value(443, 'AT') is True

    def test_valid_code_0443_clp(self):
        assert is_valid_table_value(443, 'CLP') is True

    def test_valid_code_0443_cp(self):
        assert is_valid_table_value(443, 'CP') is True

    def test_invalid_code_0443(self):
        assert is_valid_table_value(443, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0443(self):
        result = validate_table_value(443, 'AD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0443(self):
        result = validate_table_value(443, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0444:
    """Tests for table 0444: NameAssemblyOrder"""

    def test_get_table_codes_0444(self):
        codes = get_table_codes(444)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0444_g(self):
        assert is_valid_table_value(444, 'G') is True

    def test_valid_code_0444_f(self):
        assert is_valid_table_value(444, 'F') is True

    def test_invalid_code_0444(self):
        assert is_valid_table_value(444, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0444(self):
        result = validate_table_value(444, 'G', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0444(self):
        result = validate_table_value(444, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0445:
    """Tests for table 0445: IdentityReliability"""

    def test_get_table_codes_0445(self):
        codes = get_table_codes(445)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0445_us(self):
        assert is_valid_table_value(445, 'US') is True

    def test_valid_code_0445_ud(self):
        assert is_valid_table_value(445, 'UD') is True

    def test_valid_code_0445_ua(self):
        assert is_valid_table_value(445, 'UA') is True

    def test_valid_code_0445_al(self):
        assert is_valid_table_value(445, 'AL') is True

    def test_invalid_code_0445(self):
        assert is_valid_table_value(445, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0445(self):
        result = validate_table_value(445, 'US', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0445(self):
        result = validate_table_value(445, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0450:
    """Tests for table 0450: EventType"""

    def test_get_table_codes_0450(self):
        codes = get_table_codes(450)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0450_log(self):
        assert is_valid_table_value(450, 'LOG') is True

    def test_valid_code_0450_ser(self):
        assert is_valid_table_value(450, 'SER') is True

    def test_invalid_code_0450(self):
        assert is_valid_table_value(450, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0450(self):
        result = validate_table_value(450, 'LOG', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0450(self):
        result = validate_table_value(450, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0457:
    """Tests for table 0457: OverallClaimDisposition"""

    def test_get_table_codes_0457(self):
        codes = get_table_codes(457)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0457_c_0(self):
        assert is_valid_table_value(457, '0') is True

    def test_valid_code_0457_c_1(self):
        assert is_valid_table_value(457, '1') is True

    def test_valid_code_0457_c_2(self):
        assert is_valid_table_value(457, '2') is True

    def test_valid_code_0457_c_3(self):
        assert is_valid_table_value(457, '3') is True

    def test_valid_code_0457_c_4(self):
        assert is_valid_table_value(457, '4') is True

    def test_invalid_code_0457(self):
        assert is_valid_table_value(457, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0457(self):
        result = validate_table_value(457, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0457(self):
        result = validate_table_value(457, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0465:
    """Tests for table 0465: NameAddressRepresentation"""

    def test_get_table_codes_0465(self):
        codes = get_table_codes(465)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0465_i(self):
        assert is_valid_table_value(465, 'I') is True

    def test_valid_code_0465_a(self):
        assert is_valid_table_value(465, 'A') is True

    def test_valid_code_0465_p(self):
        assert is_valid_table_value(465, 'P') is True

    def test_invalid_code_0465(self):
        assert is_valid_table_value(465, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0465(self):
        result = validate_table_value(465, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0465(self):
        result = validate_table_value(465, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0466:
    """Tests for table 0466: AmbulatoryPaymentClassification"""

    def test_get_table_codes_0466(self):
        codes = get_table_codes(466)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0466_c_031(self):
        assert is_valid_table_value(466, '031') is True

    def test_valid_code_0466_c_163(self):
        assert is_valid_table_value(466, '163') is True

    def test_valid_code_0466_c_181(self):
        assert is_valid_table_value(466, '181') is True

    def test_valid_code_0466_empty(self):
        assert is_valid_table_value(466, '...') is True

    def test_invalid_code_0466(self):
        assert is_valid_table_value(466, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0466(self):
        result = validate_table_value(466, '031', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0466(self):
        result = validate_table_value(466, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0468:
    """Tests for table 0468: PaymentAdjustmentInformation"""

    def test_get_table_codes_0468(self):
        codes = get_table_codes(468)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0468_c_1(self):
        assert is_valid_table_value(468, '1') is True

    def test_valid_code_0468_c_2(self):
        assert is_valid_table_value(468, '2') is True

    def test_valid_code_0468_c_3(self):
        assert is_valid_table_value(468, '3') is True

    def test_valid_code_0468_c_4(self):
        assert is_valid_table_value(468, '4') is True

    def test_valid_code_0468_c_5(self):
        assert is_valid_table_value(468, '5') is True

    def test_invalid_code_0468(self):
        assert is_valid_table_value(468, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0468(self):
        result = validate_table_value(468, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0468(self):
        result = validate_table_value(468, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0469:
    """Tests for table 0469: PackagingStatus"""

    def test_get_table_codes_0469(self):
        codes = get_table_codes(469)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0469_c_0(self):
        assert is_valid_table_value(469, '0') is True

    def test_valid_code_0469_c_1(self):
        assert is_valid_table_value(469, '1') is True

    def test_valid_code_0469_c_2(self):
        assert is_valid_table_value(469, '2') is True

    def test_invalid_code_0469(self):
        assert is_valid_table_value(469, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0469(self):
        result = validate_table_value(469, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0469(self):
        result = validate_table_value(469, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0470:
    """Tests for table 0470: ReimbursementType"""

    def test_get_table_codes_0470(self):
        codes = get_table_codes(470)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0470_opps(self):
        assert is_valid_table_value(470, 'OPPS') is True

    def test_valid_code_0470_pckg(self):
        assert is_valid_table_value(470, 'Pckg') is True

    def test_valid_code_0470_lab(self):
        assert is_valid_table_value(470, 'Lab') is True

    def test_valid_code_0470_thrpy(self):
        assert is_valid_table_value(470, 'Thrpy') is True

    def test_valid_code_0470_dme(self):
        assert is_valid_table_value(470, 'DME') is True

    def test_invalid_code_0470(self):
        assert is_valid_table_value(470, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0470(self):
        result = validate_table_value(470, 'OPPS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0470(self):
        result = validate_table_value(470, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0472:
    """Tests for table 0472: TqConjunctionId"""

    def test_get_table_codes_0472(self):
        codes = get_table_codes(472)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0472_s(self):
        assert is_valid_table_value(472, 'S') is True

    def test_valid_code_0472_a(self):
        assert is_valid_table_value(472, 'A') is True

    def test_valid_code_0472_c(self):
        assert is_valid_table_value(472, 'C') is True

    def test_invalid_code_0472(self):
        assert is_valid_table_value(472, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0472(self):
        result = validate_table_value(472, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0472(self):
        result = validate_table_value(472, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0473:
    """Tests for table 0473: FormularyStatus"""

    def test_get_table_codes_0473(self):
        codes = get_table_codes(473)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0473_g(self):
        assert is_valid_table_value(473, 'G') is True

    def test_valid_code_0473_n(self):
        assert is_valid_table_value(473, 'N') is True

    def test_valid_code_0473_r(self):
        assert is_valid_table_value(473, 'R') is True

    def test_valid_code_0473_y(self):
        assert is_valid_table_value(473, 'Y') is True

    def test_invalid_code_0473(self):
        assert is_valid_table_value(473, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0473(self):
        result = validate_table_value(473, 'G', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0473(self):
        result = validate_table_value(473, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0474:
    """Tests for table 0474: OrganizationUnitType"""

    def test_get_table_codes_0474(self):
        codes = get_table_codes(474)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0474_d(self):
        assert is_valid_table_value(474, 'D') is True

    def test_valid_code_0474_f(self):
        assert is_valid_table_value(474, 'F') is True

    def test_valid_code_0474_l(self):
        assert is_valid_table_value(474, 'L') is True

    def test_valid_code_0474_u(self):
        assert is_valid_table_value(474, 'U') is True

    def test_valid_code_0474_m(self):
        assert is_valid_table_value(474, 'M') is True

    def test_invalid_code_0474(self):
        assert is_valid_table_value(474, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0474(self):
        result = validate_table_value(474, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0474(self):
        result = validate_table_value(474, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0475:
    """Tests for table 0475: ChargeTypeReason"""

    def test_get_table_codes_0475(self):
        codes = get_table_codes(475)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0475_c_01(self):
        assert is_valid_table_value(475, '01') is True

    def test_valid_code_0475_c_02(self):
        assert is_valid_table_value(475, '02') is True

    def test_valid_code_0475_c_03(self):
        assert is_valid_table_value(475, '03') is True

    def test_valid_code_0475_c_04(self):
        assert is_valid_table_value(475, '04') is True

    def test_valid_code_0475_c_05(self):
        assert is_valid_table_value(475, '05') is True

    def test_invalid_code_0475(self):
        assert is_valid_table_value(475, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0475(self):
        result = validate_table_value(475, '01', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0475(self):
        result = validate_table_value(475, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0477:
    """Tests for table 0477: ControlledSubstanceSchedule"""

    def test_get_table_codes_0477(self):
        codes = get_table_codes(477)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0477_i(self):
        assert is_valid_table_value(477, 'I') is True

    def test_valid_code_0477_ii(self):
        assert is_valid_table_value(477, 'II') is True

    def test_valid_code_0477_iii(self):
        assert is_valid_table_value(477, 'III') is True

    def test_valid_code_0477_iv(self):
        assert is_valid_table_value(477, 'IV') is True

    def test_valid_code_0477_v(self):
        assert is_valid_table_value(477, 'V') is True

    def test_invalid_code_0477(self):
        assert is_valid_table_value(477, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0477(self):
        result = validate_table_value(477, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0477(self):
        result = validate_table_value(477, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0478:
    """Tests for table 0478: FormularyStatus"""

    def test_get_table_codes_0478(self):
        codes = get_table_codes(478)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0478_y(self):
        assert is_valid_table_value(478, 'Y') is True

    def test_valid_code_0478_n(self):
        assert is_valid_table_value(478, 'N') is True

    def test_valid_code_0478_r(self):
        assert is_valid_table_value(478, 'R') is True

    def test_valid_code_0478_g(self):
        assert is_valid_table_value(478, 'G') is True

    def test_invalid_code_0478(self):
        assert is_valid_table_value(478, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0478(self):
        result = validate_table_value(478, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0478(self):
        result = validate_table_value(478, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0480:
    """Tests for table 0480: PharmacyOrderTypes"""

    def test_get_table_codes_0480(self):
        codes = get_table_codes(480)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0480_m(self):
        assert is_valid_table_value(480, 'M') is True

    def test_valid_code_0480_s(self):
        assert is_valid_table_value(480, 'S') is True

    def test_valid_code_0480_o(self):
        assert is_valid_table_value(480, 'O') is True

    def test_invalid_code_0480(self):
        assert is_valid_table_value(480, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0480(self):
        result = validate_table_value(480, 'M', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0480(self):
        result = validate_table_value(480, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0482:
    """Tests for table 0482: OrderType"""

    def test_get_table_codes_0482(self):
        codes = get_table_codes(482)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0482_i(self):
        assert is_valid_table_value(482, 'I') is True

    def test_valid_code_0482_o(self):
        assert is_valid_table_value(482, 'O') is True

    def test_invalid_code_0482(self):
        assert is_valid_table_value(482, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0482(self):
        result = validate_table_value(482, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0482(self):
        result = validate_table_value(482, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0483:
    """Tests for table 0483: AuthorizationMode"""

    def test_get_table_codes_0483(self):
        codes = get_table_codes(483)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0483_el(self):
        assert is_valid_table_value(483, 'EL') is True

    def test_valid_code_0483_em(self):
        assert is_valid_table_value(483, 'EM') is True

    def test_valid_code_0483_fx(self):
        assert is_valid_table_value(483, 'FX') is True

    def test_valid_code_0483_ip(self):
        assert is_valid_table_value(483, 'IP') is True

    def test_valid_code_0483_ma(self):
        assert is_valid_table_value(483, 'MA') is True

    def test_invalid_code_0483(self):
        assert is_valid_table_value(483, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0483(self):
        result = validate_table_value(483, 'EL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0483(self):
        result = validate_table_value(483, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0484:
    """Tests for table 0484: DispenseType"""

    def test_get_table_codes_0484(self):
        codes = get_table_codes(484)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0484_b(self):
        assert is_valid_table_value(484, 'B') is True

    def test_valid_code_0484_c(self):
        assert is_valid_table_value(484, 'C') is True

    def test_valid_code_0484_n(self):
        assert is_valid_table_value(484, 'N') is True

    def test_valid_code_0484_p(self):
        assert is_valid_table_value(484, 'P') is True

    def test_valid_code_0484_q(self):
        assert is_valid_table_value(484, 'Q') is True

    def test_invalid_code_0484(self):
        assert is_valid_table_value(484, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0484(self):
        result = validate_table_value(484, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0484(self):
        result = validate_table_value(484, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0485:
    """Tests for table 0485: ExtendedPriorityCodes"""

    def test_get_table_codes_0485(self):
        codes = get_table_codes(485)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0485_s(self):
        assert is_valid_table_value(485, 'S') is True

    def test_valid_code_0485_a(self):
        assert is_valid_table_value(485, 'A') is True

    def test_valid_code_0485_r(self):
        assert is_valid_table_value(485, 'R') is True

    def test_valid_code_0485_p(self):
        assert is_valid_table_value(485, 'P') is True

    def test_valid_code_0485_c(self):
        assert is_valid_table_value(485, 'C') is True

    def test_invalid_code_0485(self):
        assert is_valid_table_value(485, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0485(self):
        result = validate_table_value(485, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0485(self):
        result = validate_table_value(485, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0487:
    """Tests for table 0487: SpecimenType"""

    def test_get_table_codes_0487(self):
        codes = get_table_codes(487)
        assert codes is not None
        assert len(codes) == 315

    def test_valid_code_0487_abs(self):
        assert is_valid_table_value(487, 'ABS') is True

    def test_valid_code_0487_empty(self):
        assert is_valid_table_value(487, '...') is True

    def test_valid_code_0487_acne(self):
        assert is_valid_table_value(487, 'ACNE') is True

    def test_valid_code_0487_acnfld(self):
        assert is_valid_table_value(487, 'ACNFLD') is True

    def test_valid_code_0487_airs(self):
        assert is_valid_table_value(487, 'AIRS') is True

    def test_invalid_code_0487(self):
        assert is_valid_table_value(487, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0487(self):
        result = validate_table_value(487, 'ABS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0487(self):
        result = validate_table_value(487, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0488:
    """Tests for table 0488: SpecimenCollectionMethod"""

    def test_get_table_codes_0488(self):
        codes = get_table_codes(488)
        assert codes is not None
        assert len(codes) == 42

    def test_valid_code_0488_fna(self):
        assert is_valid_table_value(488, 'FNA') is True

    def test_valid_code_0488_pna(self):
        assert is_valid_table_value(488, 'PNA') is True

    def test_valid_code_0488_bio(self):
        assert is_valid_table_value(488, 'BIO') is True

    def test_valid_code_0488_bcae(self):
        assert is_valid_table_value(488, 'BCAE') is True

    def test_valid_code_0488_bcan(self):
        assert is_valid_table_value(488, 'BCAN') is True

    def test_invalid_code_0488(self):
        assert is_valid_table_value(488, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0488(self):
        result = validate_table_value(488, 'FNA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0488(self):
        result = validate_table_value(488, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0489:
    """Tests for table 0489: Risks"""

    def test_get_table_codes_0489(self):
        codes = get_table_codes(489)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0489_bio(self):
        assert is_valid_table_value(489, 'BIO') is True

    def test_valid_code_0489_cor(self):
        assert is_valid_table_value(489, 'COR') is True

    def test_valid_code_0489_esc(self):
        assert is_valid_table_value(489, 'ESC') is True

    def test_valid_code_0489_agg(self):
        assert is_valid_table_value(489, 'AGG') is True

    def test_valid_code_0489_ifl(self):
        assert is_valid_table_value(489, 'IFL') is True

    def test_invalid_code_0489(self):
        assert is_valid_table_value(489, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0489(self):
        result = validate_table_value(489, 'BIO', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0489(self):
        result = validate_table_value(489, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0490:
    """Tests for table 0490: SpecimenRejectReason"""

    def test_get_table_codes_0490(self):
        codes = get_table_codes(490)
        assert codes is not None
        assert len(codes) == 14

    def test_valid_code_0490_ex(self):
        assert is_valid_table_value(490, 'EX') is True

    def test_valid_code_0490_qs(self):
        assert is_valid_table_value(490, 'QS') is True

    def test_valid_code_0490_rb(self):
        assert is_valid_table_value(490, 'RB') is True

    def test_valid_code_0490_rc(self):
        assert is_valid_table_value(490, 'RC') is True

    def test_valid_code_0490_rd(self):
        assert is_valid_table_value(490, 'RD') is True

    def test_invalid_code_0490(self):
        assert is_valid_table_value(490, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0490(self):
        result = validate_table_value(490, 'EX', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0490(self):
        result = validate_table_value(490, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0491:
    """Tests for table 0491: SpecimenQuality"""

    def test_get_table_codes_0491(self):
        codes = get_table_codes(491)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0491_e(self):
        assert is_valid_table_value(491, 'E') is True

    def test_valid_code_0491_g(self):
        assert is_valid_table_value(491, 'G') is True

    def test_valid_code_0491_f(self):
        assert is_valid_table_value(491, 'F') is True

    def test_valid_code_0491_p(self):
        assert is_valid_table_value(491, 'P') is True

    def test_invalid_code_0491(self):
        assert is_valid_table_value(491, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0491(self):
        result = validate_table_value(491, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0491(self):
        result = validate_table_value(491, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0492:
    """Tests for table 0492: SpecimenAppropriateness"""

    def test_get_table_codes_0492(self):
        codes = get_table_codes(492)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0492_p(self):
        assert is_valid_table_value(492, 'P') is True

    def test_valid_code_0492_a(self):
        assert is_valid_table_value(492, 'A') is True

    def test_valid_code_0492_i(self):
        assert is_valid_table_value(492, 'I') is True

    def test_valid_code_0492_empty(self):
        assert is_valid_table_value(492, '??') is True

    def test_invalid_code_0492(self):
        assert is_valid_table_value(492, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0492(self):
        result = validate_table_value(492, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0492(self):
        result = validate_table_value(492, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0493:
    """Tests for table 0493: SpecimenCondition"""

    def test_get_table_codes_0493(self):
        codes = get_table_codes(493)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0493_aut(self):
        assert is_valid_table_value(493, 'AUT') is True

    def test_valid_code_0493_clot(self):
        assert is_valid_table_value(493, 'CLOT') is True

    def test_valid_code_0493_con(self):
        assert is_valid_table_value(493, 'CON') is True

    def test_valid_code_0493_cool(self):
        assert is_valid_table_value(493, 'COOL') is True

    def test_valid_code_0493_froz(self):
        assert is_valid_table_value(493, 'FROZ') is True

    def test_invalid_code_0493(self):
        assert is_valid_table_value(493, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0493(self):
        result = validate_table_value(493, 'AUT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0493(self):
        result = validate_table_value(493, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0494:
    """Tests for table 0494: SpecimenChildRole"""

    def test_get_table_codes_0494(self):
        codes = get_table_codes(494)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0494_a(self):
        assert is_valid_table_value(494, 'A') is True

    def test_valid_code_0494_c(self):
        assert is_valid_table_value(494, 'C') is True

    def test_valid_code_0494_m(self):
        assert is_valid_table_value(494, 'M') is True

    def test_invalid_code_0494(self):
        assert is_valid_table_value(494, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0494(self):
        result = validate_table_value(494, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0494(self):
        result = validate_table_value(494, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0495:
    """Tests for table 0495: BodySiteModifier"""

    def test_get_table_codes_0495(self):
        codes = get_table_codes(495)
        assert codes is not None
        assert len(codes) == 16

    def test_valid_code_0495_ant(self):
        assert is_valid_table_value(495, 'ANT') is True

    def test_valid_code_0495_bil(self):
        assert is_valid_table_value(495, 'BIL') is True

    def test_valid_code_0495_dis(self):
        assert is_valid_table_value(495, 'DIS') is True

    def test_valid_code_0495_ext(self):
        assert is_valid_table_value(495, 'EXT') is True

    def test_valid_code_0495_lat(self):
        assert is_valid_table_value(495, 'LAT') is True

    def test_invalid_code_0495(self):
        assert is_valid_table_value(495, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0495(self):
        result = validate_table_value(495, 'ANT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0495(self):
        result = validate_table_value(495, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0496:
    """Tests for table 0496: ConsentType"""

    def test_get_table_codes_0496(self):
        codes = get_table_codes(496)
        assert codes is not None
        assert len(codes) == 137

    def test_valid_code_0496_c_001(self):
        assert is_valid_table_value(496, '001') is True

    def test_valid_code_0496_c_002(self):
        assert is_valid_table_value(496, '002') is True

    def test_valid_code_0496_c_003(self):
        assert is_valid_table_value(496, '003') is True

    def test_valid_code_0496_c_004(self):
        assert is_valid_table_value(496, '004') is True

    def test_valid_code_0496_c_005(self):
        assert is_valid_table_value(496, '005') is True

    def test_invalid_code_0496(self):
        assert is_valid_table_value(496, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0496(self):
        result = validate_table_value(496, '001', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0496(self):
        result = validate_table_value(496, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0497:
    """Tests for table 0497: ConsentMode"""

    def test_get_table_codes_0497(self):
        codes = get_table_codes(497)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0497_v(self):
        assert is_valid_table_value(497, 'V') is True

    def test_valid_code_0497_w(self):
        assert is_valid_table_value(497, 'W') is True

    def test_valid_code_0497_t(self):
        assert is_valid_table_value(497, 'T') is True

    def test_invalid_code_0497(self):
        assert is_valid_table_value(497, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0497(self):
        result = validate_table_value(497, 'V', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0497(self):
        result = validate_table_value(497, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0498:
    """Tests for table 0498: ConsentStatus"""

    def test_get_table_codes_0498(self):
        codes = get_table_codes(498)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0498_a(self):
        assert is_valid_table_value(498, 'A') is True

    def test_valid_code_0498_l(self):
        assert is_valid_table_value(498, 'L') is True

    def test_valid_code_0498_r(self):
        assert is_valid_table_value(498, 'R') is True

    def test_valid_code_0498_p(self):
        assert is_valid_table_value(498, 'P') is True

    def test_valid_code_0498_x(self):
        assert is_valid_table_value(498, 'X') is True

    def test_invalid_code_0498(self):
        assert is_valid_table_value(498, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0498(self):
        result = validate_table_value(498, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0498(self):
        result = validate_table_value(498, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0499:
    """Tests for table 0499: ConsentBypassReason"""

    def test_get_table_codes_0499(self):
        codes = get_table_codes(499)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0499_e(self):
        assert is_valid_table_value(499, 'E') is True

    def test_valid_code_0499_pj(self):
        assert is_valid_table_value(499, 'PJ') is True

    def test_invalid_code_0499(self):
        assert is_valid_table_value(499, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0499(self):
        result = validate_table_value(499, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0499(self):
        result = validate_table_value(499, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0500:
    """Tests for table 0500: ConsentDisclosureLevel"""

    def test_get_table_codes_0500(self):
        codes = get_table_codes(500)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0500_f(self):
        assert is_valid_table_value(500, 'F') is True

    def test_valid_code_0500_p(self):
        assert is_valid_table_value(500, 'P') is True

    def test_valid_code_0500_n(self):
        assert is_valid_table_value(500, 'N') is True

    def test_invalid_code_0500(self):
        assert is_valid_table_value(500, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0500(self):
        result = validate_table_value(500, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0500(self):
        result = validate_table_value(500, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0501:
    """Tests for table 0501: ConsentNonDisclosureReason"""

    def test_get_table_codes_0501(self):
        codes = get_table_codes(501)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0501_e(self):
        assert is_valid_table_value(501, 'E') is True

    def test_valid_code_0501_rx(self):
        assert is_valid_table_value(501, 'RX') is True

    def test_valid_code_0501_pr(self):
        assert is_valid_table_value(501, 'PR') is True

    def test_invalid_code_0501(self):
        assert is_valid_table_value(501, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0501(self):
        result = validate_table_value(501, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0501(self):
        result = validate_table_value(501, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0502:
    """Tests for table 0502: NonSubjectConsenterReason"""

    def test_get_table_codes_0502(self):
        codes = get_table_codes(502)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0502_min(self):
        assert is_valid_table_value(502, 'MIN') is True

    def test_valid_code_0502_nc(self):
        assert is_valid_table_value(502, 'NC') is True

    def test_valid_code_0502_lm(self):
        assert is_valid_table_value(502, 'LM') is True

    def test_invalid_code_0502(self):
        assert is_valid_table_value(502, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0502(self):
        result = validate_table_value(502, 'MIN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0502(self):
        result = validate_table_value(502, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0503:
    """Tests for table 0503: SequenceResultsFlag"""

    def test_get_table_codes_0503(self):
        codes = get_table_codes(503)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0503_s(self):
        assert is_valid_table_value(503, 'S') is True

    def test_valid_code_0503_c(self):
        assert is_valid_table_value(503, 'C') is True

    def test_valid_code_0503_r(self):
        assert is_valid_table_value(503, 'R') is True

    def test_invalid_code_0503(self):
        assert is_valid_table_value(503, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0503(self):
        result = validate_table_value(503, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0503(self):
        result = validate_table_value(503, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0504:
    """Tests for table 0504: SequenceCondition"""

    def test_get_table_codes_0504(self):
        codes = get_table_codes(504)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0504_ee(self):
        assert is_valid_table_value(504, 'EE') is True

    def test_valid_code_0504_es(self):
        assert is_valid_table_value(504, 'ES') is True

    def test_valid_code_0504_ss(self):
        assert is_valid_table_value(504, 'SS') is True

    def test_valid_code_0504_se(self):
        assert is_valid_table_value(504, 'SE') is True

    def test_invalid_code_0504(self):
        assert is_valid_table_value(504, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0504(self):
        result = validate_table_value(504, 'EE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0504(self):
        result = validate_table_value(504, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0505:
    """Tests for table 0505: CyclicEntryExitIndicator"""

    def test_get_table_codes_0505(self):
        codes = get_table_codes(505)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0505_f(self):
        assert is_valid_table_value(505, 'F') is True

    def test_valid_code_0505_l(self):
        assert is_valid_table_value(505, 'L') is True

    def test_valid_code_0505_empty(self):
        assert is_valid_table_value(505, '*') is True

    def test_valid_code_0505_empty_2(self):
        assert is_valid_table_value(505, '#') is True

    def test_invalid_code_0505(self):
        assert is_valid_table_value(505, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0505(self):
        result = validate_table_value(505, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0505(self):
        result = validate_table_value(505, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0506:
    """Tests for table 0506: ServiceRequestRelationship"""

    def test_get_table_codes_0506(self):
        codes = get_table_codes(506)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0506_n(self):
        assert is_valid_table_value(506, 'N') is True

    def test_valid_code_0506_c(self):
        assert is_valid_table_value(506, 'C') is True

    def test_valid_code_0506_t(self):
        assert is_valid_table_value(506, 'T') is True

    def test_valid_code_0506_e(self):
        assert is_valid_table_value(506, 'E') is True

    def test_valid_code_0506_s(self):
        assert is_valid_table_value(506, 'S') is True

    def test_invalid_code_0506(self):
        assert is_valid_table_value(506, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0506(self):
        result = validate_table_value(506, 'N', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0506(self):
        result = validate_table_value(506, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0507:
    """Tests for table 0507: ObservationResultHandling"""

    def test_get_table_codes_0507(self):
        codes = get_table_codes(507)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0507_f(self):
        assert is_valid_table_value(507, 'F') is True

    def test_valid_code_0507_n(self):
        assert is_valid_table_value(507, 'N') is True

    def test_valid_code_0507_a(self):
        assert is_valid_table_value(507, 'A') is True

    def test_valid_code_0507_cc(self):
        assert is_valid_table_value(507, 'CC') is True

    def test_valid_code_0507_bcc(self):
        assert is_valid_table_value(507, 'BCC') is True

    def test_invalid_code_0507(self):
        assert is_valid_table_value(507, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0507(self):
        result = validate_table_value(507, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0507(self):
        result = validate_table_value(507, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0508:
    """Tests for table 0508: BloodProductProcessingRequirements"""

    def test_get_table_codes_0508(self):
        codes = get_table_codes(508)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0508_lr(self):
        assert is_valid_table_value(508, 'LR') is True

    def test_valid_code_0508_ir(self):
        assert is_valid_table_value(508, 'IR') is True

    def test_valid_code_0508_cs(self):
        assert is_valid_table_value(508, 'CS') is True

    def test_valid_code_0508_fr(self):
        assert is_valid_table_value(508, 'FR') is True

    def test_valid_code_0508_au(self):
        assert is_valid_table_value(508, 'AU') is True

    def test_invalid_code_0508(self):
        assert is_valid_table_value(508, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0508(self):
        result = validate_table_value(508, 'LR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0508(self):
        result = validate_table_value(508, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0510:
    """Tests for table 0510: BloodProductDispenseStatus"""

    def test_get_table_codes_0510(self):
        codes = get_table_codes(510)
        assert codes is not None
        assert len(codes) == 11

    def test_valid_code_0510_ri(self):
        assert is_valid_table_value(510, 'RI') is True

    def test_valid_code_0510_rd(self):
        assert is_valid_table_value(510, 'RD') is True

    def test_valid_code_0510_rs(self):
        assert is_valid_table_value(510, 'RS') is True

    def test_valid_code_0510_re(self):
        assert is_valid_table_value(510, 'RE') is True

    def test_valid_code_0510_ds(self):
        assert is_valid_table_value(510, 'DS') is True

    def test_invalid_code_0510(self):
        assert is_valid_table_value(510, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0510(self):
        result = validate_table_value(510, 'RI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0510(self):
        result = validate_table_value(510, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0511:
    """Tests for table 0511: BpObservationStatusCodesInterpretation"""

    def test_get_table_codes_0511(self):
        codes = get_table_codes(511)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0511_c(self):
        assert is_valid_table_value(511, 'C') is True

    def test_valid_code_0511_d(self):
        assert is_valid_table_value(511, 'D') is True

    def test_valid_code_0511_f(self):
        assert is_valid_table_value(511, 'F') is True

    def test_valid_code_0511_o(self):
        assert is_valid_table_value(511, 'O') is True

    def test_valid_code_0511_p(self):
        assert is_valid_table_value(511, 'P') is True

    def test_invalid_code_0511(self):
        assert is_valid_table_value(511, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0511(self):
        result = validate_table_value(511, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0511(self):
        result = validate_table_value(511, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0513:
    """Tests for table 0513: BloodProductTransfusionDispositionStatus"""

    def test_get_table_codes_0513(self):
        codes = get_table_codes(513)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0513_ra(self):
        assert is_valid_table_value(513, 'RA') is True

    def test_valid_code_0513_rl(self):
        assert is_valid_table_value(513, 'RL') is True

    def test_valid_code_0513_wa(self):
        assert is_valid_table_value(513, 'WA') is True

    def test_valid_code_0513_ti(self):
        assert is_valid_table_value(513, 'TI') is True

    def test_valid_code_0513_tr(self):
        assert is_valid_table_value(513, 'TR') is True

    def test_invalid_code_0513(self):
        assert is_valid_table_value(513, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0513(self):
        result = validate_table_value(513, 'RA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0513(self):
        result = validate_table_value(513, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0514:
    """Tests for table 0514: TransfusionAdverseReaction"""

    def test_get_table_codes_0514(self):
        codes = get_table_codes(514)
        assert codes is not None
        assert len(codes) == 19

    def test_valid_code_0514_aboinc(self):
        assert is_valid_table_value(514, 'ABOINC') is True

    def test_valid_code_0514_acuthehtr(self):
        assert is_valid_table_value(514, 'ACUTHEHTR') is True

    def test_valid_code_0514_allergic1(self):
        assert is_valid_table_value(514, 'ALLERGIC1') is True

    def test_valid_code_0514_allergic2(self):
        assert is_valid_table_value(514, 'ALLERGIC2') is True

    def test_valid_code_0514_allergicr(self):
        assert is_valid_table_value(514, 'ALLERGICR') is True

    def test_invalid_code_0514(self):
        assert is_valid_table_value(514, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0514(self):
        result = validate_table_value(514, 'ABOINC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0514(self):
        result = validate_table_value(514, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0516:
    """Tests for table 0516: ErrorSeverity"""

    def test_get_table_codes_0516(self):
        codes = get_table_codes(516)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0516_w(self):
        assert is_valid_table_value(516, 'W') is True

    def test_valid_code_0516_i(self):
        assert is_valid_table_value(516, 'I') is True

    def test_valid_code_0516_e(self):
        assert is_valid_table_value(516, 'E') is True

    def test_valid_code_0516_f(self):
        assert is_valid_table_value(516, 'F') is True

    def test_invalid_code_0516(self):
        assert is_valid_table_value(516, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0516(self):
        result = validate_table_value(516, 'W', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0516(self):
        result = validate_table_value(516, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0517:
    """Tests for table 0517: InformInstructions"""

    def test_get_table_codes_0517(self):
        codes = get_table_codes(517)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0517_pat(self):
        assert is_valid_table_value(517, 'PAT') is True

    def test_valid_code_0517_npat(self):
        assert is_valid_table_value(517, 'NPAT') is True

    def test_valid_code_0517_usr(self):
        assert is_valid_table_value(517, 'USR') is True

    def test_valid_code_0517_hd(self):
        assert is_valid_table_value(517, 'HD') is True

    def test_invalid_code_0517(self):
        assert is_valid_table_value(517, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0517(self):
        result = validate_table_value(517, 'PAT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0517(self):
        result = validate_table_value(517, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0518:
    """Tests for table 0518: OverrideType"""

    def test_get_table_codes_0518(self):
        codes = get_table_codes(518)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0518_extn(self):
        assert is_valid_table_value(518, 'EXTN') is True

    def test_valid_code_0518_inlv(self):
        assert is_valid_table_value(518, 'INLV') is True

    def test_valid_code_0518_eqv(self):
        assert is_valid_table_value(518, 'EQV') is True

    def test_invalid_code_0518(self):
        assert is_valid_table_value(518, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0518(self):
        result = validate_table_value(518, 'EXTN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0518(self):
        result = validate_table_value(518, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0520:
    """Tests for table 0520: MessageWaitingPriority"""

    def test_get_table_codes_0520(self):
        codes = get_table_codes(520)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0520_h(self):
        assert is_valid_table_value(520, 'H') is True

    def test_valid_code_0520_m(self):
        assert is_valid_table_value(520, 'M') is True

    def test_valid_code_0520_l(self):
        assert is_valid_table_value(520, 'L') is True

    def test_invalid_code_0520(self):
        assert is_valid_table_value(520, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0520(self):
        result = validate_table_value(520, 'H', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0520(self):
        result = validate_table_value(520, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0523:
    """Tests for table 0523: ComputationType"""

    def test_get_table_codes_0523(self):
        codes = get_table_codes(523)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0523_empty(self):
        assert is_valid_table_value(523, '%') is True

    def test_valid_code_0523_a(self):
        assert is_valid_table_value(523, 'a') is True

    def test_invalid_code_0523(self):
        assert is_valid_table_value(523, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0523(self):
        result = validate_table_value(523, '%', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0523(self):
        result = validate_table_value(523, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0524:
    """Tests for table 0524: SequenceCondition"""

    def test_get_table_codes_0524(self):
        codes = get_table_codes(524)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0524_s(self):
        assert is_valid_table_value(524, 'S') is True

    def test_valid_code_0524_c(self):
        assert is_valid_table_value(524, 'C') is True

    def test_valid_code_0524_r(self):
        assert is_valid_table_value(524, 'R') is True

    def test_invalid_code_0524(self):
        assert is_valid_table_value(524, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0524(self):
        result = validate_table_value(524, 'S', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0524(self):
        result = validate_table_value(524, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0527:
    """Tests for table 0527: CalendarAlignment"""

    def test_get_table_codes_0527(self):
        codes = get_table_codes(527)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0527_my(self):
        assert is_valid_table_value(527, 'MY') is True

    def test_valid_code_0527_wy(self):
        assert is_valid_table_value(527, 'WY') is True

    def test_valid_code_0527_dm(self):
        assert is_valid_table_value(527, 'DM') is True

    def test_valid_code_0527_dy(self):
        assert is_valid_table_value(527, 'DY') is True

    def test_valid_code_0527_dw(self):
        assert is_valid_table_value(527, 'DW') is True

    def test_invalid_code_0527(self):
        assert is_valid_table_value(527, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0527(self):
        result = validate_table_value(527, 'MY', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0527(self):
        result = validate_table_value(527, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0528:
    """Tests for table 0528: EventRelatedPeriod"""

    def test_get_table_codes_0528(self):
        codes = get_table_codes(528)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0528_hs(self):
        assert is_valid_table_value(528, 'HS') is True

    def test_valid_code_0528_ac(self):
        assert is_valid_table_value(528, 'AC') is True

    def test_valid_code_0528_pc(self):
        assert is_valid_table_value(528, 'PC') is True

    def test_valid_code_0528_ic(self):
        assert is_valid_table_value(528, 'IC') is True

    def test_valid_code_0528_acm(self):
        assert is_valid_table_value(528, 'ACM') is True

    def test_invalid_code_0528(self):
        assert is_valid_table_value(528, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0528(self):
        result = validate_table_value(528, 'HS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0528(self):
        result = validate_table_value(528, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0529:
    """Tests for table 0529: Precision"""

    def test_get_table_codes_0529(self):
        codes = get_table_codes(529)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0529_y(self):
        assert is_valid_table_value(529, 'Y') is True

    def test_valid_code_0529_l(self):
        assert is_valid_table_value(529, 'L') is True

    def test_valid_code_0529_d(self):
        assert is_valid_table_value(529, 'D') is True

    def test_valid_code_0529_h(self):
        assert is_valid_table_value(529, 'H') is True

    def test_valid_code_0529_m(self):
        assert is_valid_table_value(529, 'M') is True

    def test_invalid_code_0529(self):
        assert is_valid_table_value(529, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0529(self):
        result = validate_table_value(529, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0529(self):
        result = validate_table_value(529, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0530:
    """Tests for table 0530: OrganizationAgencyDepartment"""

    def test_get_table_codes_0530(self):
        codes = get_table_codes(530)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0530_ae(self):
        assert is_valid_table_value(530, 'AE') is True

    def test_valid_code_0530_dea(self):
        assert is_valid_table_value(530, 'DEA') is True

    def test_valid_code_0530_dod(self):
        assert is_valid_table_value(530, 'DOD') is True

    def test_valid_code_0530_mc(self):
        assert is_valid_table_value(530, 'MC') is True

    def test_valid_code_0530_va(self):
        assert is_valid_table_value(530, 'VA') is True

    def test_invalid_code_0530(self):
        assert is_valid_table_value(530, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0530(self):
        result = validate_table_value(530, 'AE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0530(self):
        result = validate_table_value(530, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0532:
    """Tests for table 0532: ExpandedYesNoIndicator"""

    def test_get_table_codes_0532(self):
        codes = get_table_codes(532)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0532_y(self):
        assert is_valid_table_value(532, 'Y') is True

    def test_valid_code_0532_n(self):
        assert is_valid_table_value(532, 'N') is True

    def test_valid_code_0532_ni(self):
        assert is_valid_table_value(532, 'NI') is True

    def test_valid_code_0532_na(self):
        assert is_valid_table_value(532, 'NA') is True

    def test_valid_code_0532_unk(self):
        assert is_valid_table_value(532, 'UNK') is True

    def test_invalid_code_0532(self):
        assert is_valid_table_value(532, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0532(self):
        result = validate_table_value(532, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0532(self):
        result = validate_table_value(532, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0534:
    """Tests for table 0534: ClergyNotificationType"""

    def test_get_table_codes_0534(self):
        codes = get_table_codes(534)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0534_y(self):
        assert is_valid_table_value(534, 'Y') is True

    def test_valid_code_0534_n(self):
        assert is_valid_table_value(534, 'N') is True

    def test_valid_code_0534_l(self):
        assert is_valid_table_value(534, 'L') is True

    def test_valid_code_0534_o(self):
        assert is_valid_table_value(534, 'O') is True

    def test_valid_code_0534_u(self):
        assert is_valid_table_value(534, 'U') is True

    def test_invalid_code_0534(self):
        assert is_valid_table_value(534, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0534(self):
        result = validate_table_value(534, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0534(self):
        result = validate_table_value(534, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0535:
    """Tests for table 0535: SignatureType"""

    def test_get_table_codes_0535(self):
        codes = get_table_codes(535)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0535_c(self):
        assert is_valid_table_value(535, 'C') is True

    def test_valid_code_0535_s(self):
        assert is_valid_table_value(535, 'S') is True

    def test_valid_code_0535_m(self):
        assert is_valid_table_value(535, 'M') is True

    def test_valid_code_0535_p(self):
        assert is_valid_table_value(535, 'P') is True

    def test_invalid_code_0535(self):
        assert is_valid_table_value(535, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0535(self):
        result = validate_table_value(535, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0535(self):
        result = validate_table_value(535, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0536:
    """Tests for table 0536: CertificateStatus"""

    def test_get_table_codes_0536(self):
        codes = get_table_codes(536)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0536_p(self):
        assert is_valid_table_value(536, 'P') is True

    def test_valid_code_0536_r(self):
        assert is_valid_table_value(536, 'R') is True

    def test_valid_code_0536_v(self):
        assert is_valid_table_value(536, 'V') is True

    def test_valid_code_0536_e(self):
        assert is_valid_table_value(536, 'E') is True

    def test_valid_code_0536_i(self):
        assert is_valid_table_value(536, 'I') is True

    def test_invalid_code_0536(self):
        assert is_valid_table_value(536, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0536(self):
        result = validate_table_value(536, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0536(self):
        result = validate_table_value(536, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0538:
    """Tests for table 0538: InstitutionRelationshipType"""

    def test_get_table_codes_0538(self):
        codes = get_table_codes(538)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0538_emp(self):
        assert is_valid_table_value(538, 'EMP') is True

    def test_valid_code_0538_vol(self):
        assert is_valid_table_value(538, 'VOL') is True

    def test_valid_code_0538_con(self):
        assert is_valid_table_value(538, 'CON') is True

    def test_valid_code_0538_cst(self):
        assert is_valid_table_value(538, 'CST') is True

    def test_invalid_code_0538(self):
        assert is_valid_table_value(538, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0538(self):
        result = validate_table_value(538, 'EMP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0538(self):
        result = validate_table_value(538, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0540:
    """Tests for table 0540: InactiveReason"""

    def test_get_table_codes_0540(self):
        codes = get_table_codes(540)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0540_l(self):
        assert is_valid_table_value(540, 'L') is True

    def test_valid_code_0540_t(self):
        assert is_valid_table_value(540, 'T') is True

    def test_valid_code_0540_r(self):
        assert is_valid_table_value(540, 'R') is True

    def test_invalid_code_0540(self):
        assert is_valid_table_value(540, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0540(self):
        result = validate_table_value(540, 'L', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0540(self):
        result = validate_table_value(540, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0544:
    """Tests for table 0544: ContainerCondition"""

    def test_get_table_codes_0544(self):
        codes = get_table_codes(544)
        assert codes is not None
        assert len(codes) == 22

    def test_valid_code_0544_empty(self):
        assert is_valid_table_value(544, '...') is True

    def test_valid_code_0544_xc37(self):
        assert is_valid_table_value(544, 'XC37') is True

    def test_valid_code_0544_xamb(self):
        assert is_valid_table_value(544, 'XAMB') is True

    def test_valid_code_0544_xcamb(self):
        assert is_valid_table_value(544, 'XCAMB') is True

    def test_valid_code_0544_xref(self):
        assert is_valid_table_value(544, 'XREF') is True

    def test_invalid_code_0544(self):
        assert is_valid_table_value(544, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0544(self):
        result = validate_table_value(544, '...', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0544(self):
        result = validate_table_value(544, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0547:
    """Tests for table 0547: JurisdictionalBreadth"""

    def test_get_table_codes_0547(self):
        codes = get_table_codes(547)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0547_c(self):
        assert is_valid_table_value(547, 'C') is True

    def test_valid_code_0547_s(self):
        assert is_valid_table_value(547, 'S') is True

    def test_valid_code_0547_n(self):
        assert is_valid_table_value(547, 'N') is True

    def test_invalid_code_0547(self):
        assert is_valid_table_value(547, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0547(self):
        result = validate_table_value(547, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0547(self):
        result = validate_table_value(547, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0548:
    """Tests for table 0548: SignatorysRelationshipToSubject"""

    def test_get_table_codes_0548(self):
        codes = get_table_codes(548)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0548_c_1(self):
        assert is_valid_table_value(548, '1') is True

    def test_valid_code_0548_c_2(self):
        assert is_valid_table_value(548, '2') is True

    def test_valid_code_0548_c_3(self):
        assert is_valid_table_value(548, '3') is True

    def test_valid_code_0548_c_4(self):
        assert is_valid_table_value(548, '4') is True

    def test_valid_code_0548_c_5(self):
        assert is_valid_table_value(548, '5') is True

    def test_invalid_code_0548(self):
        assert is_valid_table_value(548, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0548(self):
        result = validate_table_value(548, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0548(self):
        result = validate_table_value(548, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0550:
    """Tests for table 0550: BodyParts"""

    def test_get_table_codes_0550(self):
        codes = get_table_codes(550)
        assert codes is not None
        assert len(codes) == 442

    def test_valid_code_0550_juge(self):
        assert is_valid_table_value(550, 'JUGE') is True

    def test_valid_code_0550_adb(self):
        assert is_valid_table_value(550, 'ADB') is True

    def test_valid_code_0550_acet(self):
        assert is_valid_table_value(550, 'ACET') is True

    def test_valid_code_0550_achil(self):
        assert is_valid_table_value(550, 'ACHIL') is True

    def test_valid_code_0550_ade(self):
        assert is_valid_table_value(550, 'ADE') is True

    def test_invalid_code_0550(self):
        assert is_valid_table_value(550, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0550(self):
        result = validate_table_value(550, 'JUGE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0550(self):
        result = validate_table_value(550, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0553:
    """Tests for table 0553: InvoiceControl"""

    def test_get_table_codes_0553(self):
        codes = get_table_codes(553)
        assert codes is not None
        assert len(codes) == 17

    def test_valid_code_0553_or(self):
        assert is_valid_table_value(553, 'OR') is True

    def test_valid_code_0553_cn(self):
        assert is_valid_table_value(553, 'CN') is True

    def test_valid_code_0553_cg(self):
        assert is_valid_table_value(553, 'CG') is True

    def test_valid_code_0553_cl(self):
        assert is_valid_table_value(553, 'CL') is True

    def test_valid_code_0553_pd(self):
        assert is_valid_table_value(553, 'PD') is True

    def test_invalid_code_0553(self):
        assert is_valid_table_value(553, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0553(self):
        result = validate_table_value(553, 'OR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0553(self):
        result = validate_table_value(553, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0554:
    """Tests for table 0554: InvoiceReason"""

    def test_get_table_codes_0554(self):
        codes = get_table_codes(554)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0554_late(self):
        assert is_valid_table_value(554, 'LATE') is True

    def test_valid_code_0554_norm(self):
        assert is_valid_table_value(554, 'NORM') is True

    def test_valid_code_0554_sub(self):
        assert is_valid_table_value(554, 'SUB') is True

    def test_invalid_code_0554(self):
        assert is_valid_table_value(554, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0554(self):
        result = validate_table_value(554, 'LATE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0554(self):
        result = validate_table_value(554, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0555:
    """Tests for table 0555: InvoiceType"""

    def test_get_table_codes_0555(self):
        codes = get_table_codes(555)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0555_fs(self):
        assert is_valid_table_value(555, 'FS') is True

    def test_valid_code_0555_ss(self):
        assert is_valid_table_value(555, 'SS') is True

    def test_valid_code_0555_gp(self):
        assert is_valid_table_value(555, 'GP') is True

    def test_valid_code_0555_bk(self):
        assert is_valid_table_value(555, 'BK') is True

    def test_valid_code_0555_sl(self):
        assert is_valid_table_value(555, 'SL') is True

    def test_invalid_code_0555(self):
        assert is_valid_table_value(555, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0555(self):
        result = validate_table_value(555, 'FS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0555(self):
        result = validate_table_value(555, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0556:
    """Tests for table 0556: BenefitGroup"""

    def test_get_table_codes_0556(self):
        codes = get_table_codes(556)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0556_amb(self):
        assert is_valid_table_value(556, 'AMB') is True

    def test_valid_code_0556_dent(self):
        assert is_valid_table_value(556, 'DENT') is True

    def test_invalid_code_0556(self):
        assert is_valid_table_value(556, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0556(self):
        result = validate_table_value(556, 'AMB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0556(self):
        result = validate_table_value(556, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0557:
    """Tests for table 0557: PayeeType"""

    def test_get_table_codes_0557(self):
        codes = get_table_codes(557)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0557_org(self):
        assert is_valid_table_value(557, 'ORG') is True

    def test_valid_code_0557_pers(self):
        assert is_valid_table_value(557, 'PERS') is True

    def test_valid_code_0557_pper(self):
        assert is_valid_table_value(557, 'PPER') is True

    def test_valid_code_0557_empl(self):
        assert is_valid_table_value(557, 'EMPL') is True

    def test_invalid_code_0557(self):
        assert is_valid_table_value(557, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0557(self):
        result = validate_table_value(557, 'ORG', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0557(self):
        result = validate_table_value(557, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0558:
    """Tests for table 0558: PayeeRelationshipToInvoice"""

    def test_get_table_codes_0558(self):
        codes = get_table_codes(558)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0558_pt(self):
        assert is_valid_table_value(558, 'PT') is True

    def test_valid_code_0558_fm(self):
        assert is_valid_table_value(558, 'FM') is True

    def test_valid_code_0558_sb(self):
        assert is_valid_table_value(558, 'SB') is True

    def test_valid_code_0558_gt(self):
        assert is_valid_table_value(558, 'GT') is True

    def test_invalid_code_0558(self):
        assert is_valid_table_value(558, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0558(self):
        result = validate_table_value(558, 'PT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0558(self):
        result = validate_table_value(558, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0559:
    """Tests for table 0559: ProductServiceStatus"""

    def test_get_table_codes_0559(self):
        codes = get_table_codes(559)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0559_p(self):
        assert is_valid_table_value(559, 'P') is True

    def test_valid_code_0559_d(self):
        assert is_valid_table_value(559, 'D') is True

    def test_valid_code_0559_r(self):
        assert is_valid_table_value(559, 'R') is True

    def test_invalid_code_0559(self):
        assert is_valid_table_value(559, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0559(self):
        result = validate_table_value(559, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0559(self):
        result = validate_table_value(559, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0560:
    """Tests for table 0560: QuantityUnits"""

    def test_get_table_codes_0560(self):
        codes = get_table_codes(560)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0560_fl(self):
        assert is_valid_table_value(560, 'FL') is True

    def test_valid_code_0560_dy(self):
        assert is_valid_table_value(560, 'DY') is True

    def test_valid_code_0560_hs(self):
        assert is_valid_table_value(560, 'HS') is True

    def test_valid_code_0560_mn(self):
        assert is_valid_table_value(560, 'MN') is True

    def test_valid_code_0560_yy(self):
        assert is_valid_table_value(560, 'YY') is True

    def test_invalid_code_0560(self):
        assert is_valid_table_value(560, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0560(self):
        result = validate_table_value(560, 'FL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0560(self):
        result = validate_table_value(560, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0561:
    """Tests for table 0561: ProductServicesClarification"""

    def test_get_table_codes_0561(self):
        codes = get_table_codes(561)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0561_dtctr(self):
        assert is_valid_table_value(561, 'DTCTR') is True

    def test_valid_code_0561_seq(self):
        assert is_valid_table_value(561, 'SEQ') is True

    def test_valid_code_0561_dgapp(self):
        assert is_valid_table_value(561, 'DGAPP') is True

    def test_valid_code_0561_clctr(self):
        assert is_valid_table_value(561, 'CLCTR') is True

    def test_valid_code_0561_enc(self):
        assert is_valid_table_value(561, 'ENC') is True

    def test_invalid_code_0561(self):
        assert is_valid_table_value(561, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0561(self):
        result = validate_table_value(561, 'DTCTR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0561(self):
        result = validate_table_value(561, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0562:
    """Tests for table 0562: ProcessingConsideration"""

    def test_get_table_codes_0562(self):
        codes = get_table_codes(562)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0562_paper(self):
        assert is_valid_table_value(562, 'PAPER') is True

    def test_valid_code_0562_eform(self):
        assert is_valid_table_value(562, 'EFORM') is True

    def test_valid_code_0562_fax(self):
        assert is_valid_table_value(562, 'FAX') is True

    def test_valid_code_0562_rtadj(self):
        assert is_valid_table_value(562, 'RTADJ') is True

    def test_valid_code_0562_dfadj(self):
        assert is_valid_table_value(562, 'DFADJ') is True

    def test_invalid_code_0562(self):
        assert is_valid_table_value(562, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0562(self):
        result = validate_table_value(562, 'PAPER', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0562(self):
        result = validate_table_value(562, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0564:
    """Tests for table 0564: AdjustmentCategory"""

    def test_get_table_codes_0564(self):
        codes = get_table_codes(564)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0564_ea(self):
        assert is_valid_table_value(564, 'EA') is True

    def test_valid_code_0564_in(self):
        assert is_valid_table_value(564, 'IN') is True

    def test_valid_code_0564_pa(self):
        assert is_valid_table_value(564, 'PA') is True

    def test_valid_code_0564_pr(self):
        assert is_valid_table_value(564, 'PR') is True

    def test_invalid_code_0564(self):
        assert is_valid_table_value(564, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0564(self):
        result = validate_table_value(564, 'EA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0564(self):
        result = validate_table_value(564, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0565:
    """Tests for table 0565: ProviderAdjustmentReason"""

    def test_get_table_codes_0565(self):
        codes = get_table_codes(565)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0565_pst(self):
        assert is_valid_table_value(565, 'PST') is True

    def test_valid_code_0565_gst(self):
        assert is_valid_table_value(565, 'GST') is True

    def test_valid_code_0565_hst(self):
        assert is_valid_table_value(565, 'HST') is True

    def test_valid_code_0565_disp(self):
        assert is_valid_table_value(565, 'DISP') is True

    def test_valid_code_0565_mkup(self):
        assert is_valid_table_value(565, 'MKUP') is True

    def test_invalid_code_0565(self):
        assert is_valid_table_value(565, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0565(self):
        result = validate_table_value(565, 'PST', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0565(self):
        result = validate_table_value(565, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0566:
    """Tests for table 0566: BloodUnitType"""

    def test_get_table_codes_0566(self):
        codes = get_table_codes(566)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0566_wbl(self):
        assert is_valid_table_value(566, 'WBL') is True

    def test_valid_code_0566_rbc(self):
        assert is_valid_table_value(566, 'RBC') is True

    def test_valid_code_0566_pls(self):
        assert is_valid_table_value(566, 'PLS') is True

    def test_valid_code_0566_plt(self):
        assert is_valid_table_value(566, 'PLT') is True

    def test_valid_code_0566_grn(self):
        assert is_valid_table_value(566, 'GRN') is True

    def test_invalid_code_0566(self):
        assert is_valid_table_value(566, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0566(self):
        result = validate_table_value(566, 'WBL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0566(self):
        result = validate_table_value(566, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0569:
    """Tests for table 0569: AdjustmentAction"""

    def test_get_table_codes_0569(self):
        codes = get_table_codes(569)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0569_eob(self):
        assert is_valid_table_value(569, 'EOB') is True

    def test_valid_code_0569_pat(self):
        assert is_valid_table_value(569, 'PAT') is True

    def test_valid_code_0569_pro(self):
        assert is_valid_table_value(569, 'PRO') is True

    def test_invalid_code_0569(self):
        assert is_valid_table_value(569, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0569(self):
        result = validate_table_value(569, 'EOB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0569(self):
        result = validate_table_value(569, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0570:
    """Tests for table 0570: PaymentMethod"""

    def test_get_table_codes_0570(self):
        codes = get_table_codes(570)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0570_cash(self):
        assert is_valid_table_value(570, 'CASH') is True

    def test_valid_code_0570_ccca(self):
        assert is_valid_table_value(570, 'CCCA') is True

    def test_valid_code_0570_cchk(self):
        assert is_valid_table_value(570, 'CCHK') is True

    def test_valid_code_0570_cdac(self):
        assert is_valid_table_value(570, 'CDAC') is True

    def test_valid_code_0570_chck(self):
        assert is_valid_table_value(570, 'CHCK') is True

    def test_invalid_code_0570(self):
        assert is_valid_table_value(570, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0570(self):
        result = validate_table_value(570, 'CASH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0570(self):
        result = validate_table_value(570, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0571:
    """Tests for table 0571: InvoiceProcessingResultsStatus"""

    def test_get_table_codes_0571(self):
        codes = get_table_codes(571)
        assert codes is not None
        assert len(codes) == 8

    def test_valid_code_0571_ack(self):
        assert is_valid_table_value(571, 'ACK') is True

    def test_valid_code_0571_reject(self):
        assert is_valid_table_value(571, 'REJECT') is True

    def test_valid_code_0571_pend(self):
        assert is_valid_table_value(571, 'PEND') is True

    def test_valid_code_0571_adjzer(self):
        assert is_valid_table_value(571, 'ADJZER') is True

    def test_valid_code_0571_adjsub(self):
        assert is_valid_table_value(571, 'ADJSUB') is True

    def test_invalid_code_0571(self):
        assert is_valid_table_value(571, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0571(self):
        result = validate_table_value(571, 'ACK', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0571(self):
        result = validate_table_value(571, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0572:
    """Tests for table 0572: TaxStatus"""

    def test_get_table_codes_0572(self):
        codes = get_table_codes(572)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0572_rvat(self):
        assert is_valid_table_value(572, 'RVAT') is True

    def test_valid_code_0572_uvat(self):
        assert is_valid_table_value(572, 'UVAT') is True

    def test_invalid_code_0572(self):
        assert is_valid_table_value(572, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0572(self):
        result = validate_table_value(572, 'RVAT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0572(self):
        result = validate_table_value(572, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0615:
    """Tests for table 0615: UserAuthenticationCredentialType"""

    def test_get_table_codes_0615(self):
        codes = get_table_codes(615)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0615_kerb(self):
        assert is_valid_table_value(615, 'KERB') is True

    def test_valid_code_0615_saml(self):
        assert is_valid_table_value(615, 'SAML') is True

    def test_invalid_code_0615(self):
        assert is_valid_table_value(615, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0615(self):
        result = validate_table_value(615, 'KERB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0615(self):
        result = validate_table_value(615, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0616:
    """Tests for table 0616: AddressExpirationReason"""

    def test_get_table_codes_0616(self):
        codes = get_table_codes(616)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0616_m(self):
        assert is_valid_table_value(616, 'M') is True

    def test_valid_code_0616_e(self):
        assert is_valid_table_value(616, 'E') is True

    def test_valid_code_0616_r(self):
        assert is_valid_table_value(616, 'R') is True

    def test_valid_code_0616_c(self):
        assert is_valid_table_value(616, 'C') is True

    def test_invalid_code_0616(self):
        assert is_valid_table_value(616, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0616(self):
        result = validate_table_value(616, 'M', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0616(self):
        result = validate_table_value(616, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0617:
    """Tests for table 0617: AddressUsage"""

    def test_get_table_codes_0617(self):
        codes = get_table_codes(617)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0617_m(self):
        assert is_valid_table_value(617, 'M') is True

    def test_valid_code_0617_v(self):
        assert is_valid_table_value(617, 'V') is True

    def test_valid_code_0617_c(self):
        assert is_valid_table_value(617, 'C') is True

    def test_invalid_code_0617(self):
        assert is_valid_table_value(617, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0617(self):
        result = validate_table_value(617, 'M', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0617(self):
        result = validate_table_value(617, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0618:
    """Tests for table 0618: Protection"""

    def test_get_table_codes_0618(self):
        codes = get_table_codes(618)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0618_li(self):
        assert is_valid_table_value(618, 'LI') is True

    def test_valid_code_0618_ul(self):
        assert is_valid_table_value(618, 'UL') is True

    def test_valid_code_0618_up(self):
        assert is_valid_table_value(618, 'UP') is True

    def test_invalid_code_0618(self):
        assert is_valid_table_value(618, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0618(self):
        result = validate_table_value(618, 'LI', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0618(self):
        result = validate_table_value(618, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0625:
    """Tests for table 0625: ItemStatus"""

    def test_get_table_codes_0625(self):
        codes = get_table_codes(625)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0625_c_1(self):
        assert is_valid_table_value(625, '1') is True

    def test_valid_code_0625_c_2(self):
        assert is_valid_table_value(625, '2') is True

    def test_valid_code_0625_c_3(self):
        assert is_valid_table_value(625, '3') is True

    def test_invalid_code_0625(self):
        assert is_valid_table_value(625, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0625(self):
        result = validate_table_value(625, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0625(self):
        result = validate_table_value(625, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0634:
    """Tests for table 0634: ItemImportance"""

    def test_get_table_codes_0634(self):
        codes = get_table_codes(634)
        assert codes is not None
        assert len(codes) == 1

    def test_valid_code_0634_crt(self):
        assert is_valid_table_value(634, 'CRT') is True

    def test_invalid_code_0634(self):
        assert is_valid_table_value(634, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0634(self):
        result = validate_table_value(634, 'CRT', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0634(self):
        result = validate_table_value(634, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0642:
    """Tests for table 0642: ReorderTheory"""

    def test_get_table_codes_0642(self):
        codes = get_table_codes(642)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0642_d(self):
        assert is_valid_table_value(642, 'D') is True

    def test_valid_code_0642_m(self):
        assert is_valid_table_value(642, 'M') is True

    def test_valid_code_0642_o(self):
        assert is_valid_table_value(642, 'O') is True

    def test_invalid_code_0642(self):
        assert is_valid_table_value(642, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0642(self):
        result = validate_table_value(642, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0642(self):
        result = validate_table_value(642, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0651:
    """Tests for table 0651: LaborCalculationType"""

    def test_get_table_codes_0651(self):
        codes = get_table_codes(651)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0651_tme(self):
        assert is_valid_table_value(651, 'TME') is True

    def test_valid_code_0651_cst(self):
        assert is_valid_table_value(651, 'CST') is True

    def test_invalid_code_0651(self):
        assert is_valid_table_value(651, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0651(self):
        result = validate_table_value(651, 'TME', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0651(self):
        result = validate_table_value(651, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0653:
    """Tests for table 0653: DateFormat"""

    def test_get_table_codes_0653(self):
        codes = get_table_codes(653)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0653_c_1(self):
        assert is_valid_table_value(653, '1') is True

    def test_valid_code_0653_c_2(self):
        assert is_valid_table_value(653, '2') is True

    def test_valid_code_0653_c_3(self):
        assert is_valid_table_value(653, '3') is True

    def test_valid_code_0653_c_4(self):
        assert is_valid_table_value(653, '4') is True

    def test_valid_code_0653_c_5(self):
        assert is_valid_table_value(653, '5') is True

    def test_invalid_code_0653(self):
        assert is_valid_table_value(653, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0653(self):
        result = validate_table_value(653, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0653(self):
        result = validate_table_value(653, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0657:
    """Tests for table 0657: DeviceType"""

    def test_get_table_codes_0657(self):
        codes = get_table_codes(657)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0657_c_1(self):
        assert is_valid_table_value(657, '1') is True

    def test_valid_code_0657_c_2(self):
        assert is_valid_table_value(657, '2') is True

    def test_valid_code_0657_c_3(self):
        assert is_valid_table_value(657, '3') is True

    def test_invalid_code_0657(self):
        assert is_valid_table_value(657, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0657(self):
        result = validate_table_value(657, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0657(self):
        result = validate_table_value(657, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0659:
    """Tests for table 0659: LotControl"""

    def test_get_table_codes_0659(self):
        codes = get_table_codes(659)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0659_c_1(self):
        assert is_valid_table_value(659, '1') is True

    def test_valid_code_0659_c_2(self):
        assert is_valid_table_value(659, '2') is True

    def test_valid_code_0659_c_3(self):
        assert is_valid_table_value(659, '3') is True

    def test_valid_code_0659_c_4(self):
        assert is_valid_table_value(659, '4') is True

    def test_valid_code_0659_c_5(self):
        assert is_valid_table_value(659, '5') is True

    def test_invalid_code_0659(self):
        assert is_valid_table_value(659, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0659(self):
        result = validate_table_value(659, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0659(self):
        result = validate_table_value(659, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0667:
    """Tests for table 0667: DeviceDataState"""

    def test_get_table_codes_0667(self):
        codes = get_table_codes(667)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0667_c_0(self):
        assert is_valid_table_value(667, '0') is True

    def test_valid_code_0667_c_1(self):
        assert is_valid_table_value(667, '1') is True

    def test_invalid_code_0667(self):
        assert is_valid_table_value(667, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0667(self):
        result = validate_table_value(667, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0667(self):
        result = validate_table_value(667, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0669:
    """Tests for table 0669: LoadStatus"""

    def test_get_table_codes_0669(self):
        codes = get_table_codes(669)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0669_lld(self):
        assert is_valid_table_value(669, 'LLD') is True

    def test_valid_code_0669_lcp(self):
        assert is_valid_table_value(669, 'LCP') is True

    def test_valid_code_0669_lcc(self):
        assert is_valid_table_value(669, 'LCC') is True

    def test_valid_code_0669_lcn(self):
        assert is_valid_table_value(669, 'LCN') is True

    def test_invalid_code_0669(self):
        assert is_valid_table_value(669, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0669(self):
        result = validate_table_value(669, 'LLD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0669(self):
        result = validate_table_value(669, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0682:
    """Tests for table 0682: DeviceStatus"""

    def test_get_table_codes_0682(self):
        codes = get_table_codes(682)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0682_c_0(self):
        assert is_valid_table_value(682, '0') is True

    def test_valid_code_0682_c_1(self):
        assert is_valid_table_value(682, '1') is True

    def test_invalid_code_0682(self):
        assert is_valid_table_value(682, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0682(self):
        result = validate_table_value(682, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0682(self):
        result = validate_table_value(682, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0702:
    """Tests for table 0702: CycleType"""

    def test_get_table_codes_0702(self):
        codes = get_table_codes(702)
        assert codes is not None
        assert len(codes) == 32

    def test_valid_code_0702_fls(self):
        assert is_valid_table_value(702, 'FLS') is True

    def test_valid_code_0702_prv(self):
        assert is_valid_table_value(702, 'PRV') is True

    def test_valid_code_0702_grv(self):
        assert is_valid_table_value(702, 'GRV') is True

    def test_valid_code_0702_lqd(self):
        assert is_valid_table_value(702, 'LQD') is True

    def test_valid_code_0702_exp(self):
        assert is_valid_table_value(702, 'EXP') is True

    def test_invalid_code_0702(self):
        assert is_valid_table_value(702, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0702(self):
        result = validate_table_value(702, 'FLS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0702(self):
        result = validate_table_value(702, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0717:
    """Tests for table 0717: AccessRestrictionValue"""

    def test_get_table_codes_0717(self):
        codes = get_table_codes(717)
        assert codes is not None
        assert len(codes) == 76

    def test_valid_code_0717_persdeid(self):
        assert is_valid_table_value(717, 'PersDEID') is True

    def test_valid_code_0717_all(self):
        assert is_valid_table_value(717, 'ALL') is True

    def test_valid_code_0717_dem(self):
        assert is_valid_table_value(717, 'DEM') is True

    def test_valid_code_0717_loc(self):
        assert is_valid_table_value(717, 'LOC') is True

    def test_valid_code_0717_pid_7(self):
        assert is_valid_table_value(717, 'PID-7') is True

    def test_invalid_code_0717(self):
        assert is_valid_table_value(717, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0717(self):
        result = validate_table_value(717, 'PersDEID', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0717(self):
        result = validate_table_value(717, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0728:
    """Tests for table 0728: CclValue"""

    def test_get_table_codes_0728(self):
        codes = get_table_codes(728)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0728_c_0(self):
        assert is_valid_table_value(728, '0') is True

    def test_valid_code_0728_c_1(self):
        assert is_valid_table_value(728, '1') is True

    def test_valid_code_0728_c_2(self):
        assert is_valid_table_value(728, '2') is True

    def test_valid_code_0728_c_3(self):
        assert is_valid_table_value(728, '3') is True

    def test_valid_code_0728_c_4(self):
        assert is_valid_table_value(728, '4') is True

    def test_invalid_code_0728(self):
        assert is_valid_table_value(728, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0728(self):
        result = validate_table_value(728, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0728(self):
        result = validate_table_value(728, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0731:
    """Tests for table 0731: DrgDiagnosisDeterminationStatus"""

    def test_get_table_codes_0731(self):
        codes = get_table_codes(731)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0731_c_0(self):
        assert is_valid_table_value(731, '0') is True

    def test_valid_code_0731_c_1(self):
        assert is_valid_table_value(731, '1') is True

    def test_valid_code_0731_c_2(self):
        assert is_valid_table_value(731, '2') is True

    def test_valid_code_0731_c_3(self):
        assert is_valid_table_value(731, '3') is True

    def test_valid_code_0731_c_4(self):
        assert is_valid_table_value(731, '4') is True

    def test_invalid_code_0731(self):
        assert is_valid_table_value(731, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0731(self):
        result = validate_table_value(731, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0731(self):
        result = validate_table_value(731, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0734:
    """Tests for table 0734: GrouperStatus"""

    def test_get_table_codes_0734(self):
        codes = get_table_codes(734)
        assert codes is not None
        assert len(codes) == 10

    def test_valid_code_0734_c_0(self):
        assert is_valid_table_value(734, '0') is True

    def test_valid_code_0734_c_1(self):
        assert is_valid_table_value(734, '1') is True

    def test_valid_code_0734_c_2(self):
        assert is_valid_table_value(734, '2') is True

    def test_valid_code_0734_c_3(self):
        assert is_valid_table_value(734, '3') is True

    def test_valid_code_0734_c_4(self):
        assert is_valid_table_value(734, '4') is True

    def test_invalid_code_0734(self):
        assert is_valid_table_value(734, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0734(self):
        result = validate_table_value(734, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0734(self):
        result = validate_table_value(734, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0739:
    """Tests for table 0739: DrgStatusPatient"""

    def test_get_table_codes_0739(self):
        codes = get_table_codes(739)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0739_c_1(self):
        assert is_valid_table_value(739, '1') is True

    def test_valid_code_0739_c_2(self):
        assert is_valid_table_value(739, '2') is True

    def test_valid_code_0739_c_3(self):
        assert is_valid_table_value(739, '3') is True

    def test_invalid_code_0739(self):
        assert is_valid_table_value(739, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0739(self):
        result = validate_table_value(739, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0739(self):
        result = validate_table_value(739, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0742:
    """Tests for table 0742: DrgStatusFinancialCalculation"""

    def test_get_table_codes_0742(self):
        codes = get_table_codes(742)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0742_c_00(self):
        assert is_valid_table_value(742, '00') is True

    def test_valid_code_0742_c_01(self):
        assert is_valid_table_value(742, '01') is True

    def test_valid_code_0742_c_03(self):
        assert is_valid_table_value(742, '03') is True

    def test_valid_code_0742_c_04(self):
        assert is_valid_table_value(742, '04') is True

    def test_valid_code_0742_c_05(self):
        assert is_valid_table_value(742, '05') is True

    def test_invalid_code_0742(self):
        assert is_valid_table_value(742, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0742(self):
        result = validate_table_value(742, '00', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0742(self):
        result = validate_table_value(742, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0749:
    """Tests for table 0749: DrgGroupingStatus"""

    def test_get_table_codes_0749(self):
        codes = get_table_codes(749)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0749_c_0(self):
        assert is_valid_table_value(749, '0') is True

    def test_valid_code_0749_c_1(self):
        assert is_valid_table_value(749, '1') is True

    def test_valid_code_0749_c_2(self):
        assert is_valid_table_value(749, '2') is True

    def test_valid_code_0749_c_3(self):
        assert is_valid_table_value(749, '3') is True

    def test_invalid_code_0749(self):
        assert is_valid_table_value(749, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0749(self):
        result = validate_table_value(749, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0749(self):
        result = validate_table_value(749, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0755:
    """Tests for table 0755: DrgstatusWeightAtBirth"""

    def test_get_table_codes_0755(self):
        codes = get_table_codes(755)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0755_c_0(self):
        assert is_valid_table_value(755, '0') is True

    def test_valid_code_0755_c_1(self):
        assert is_valid_table_value(755, '1') is True

    def test_valid_code_0755_c_2(self):
        assert is_valid_table_value(755, '2') is True

    def test_invalid_code_0755(self):
        assert is_valid_table_value(755, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0755(self):
        result = validate_table_value(755, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0755(self):
        result = validate_table_value(755, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0757:
    """Tests for table 0757: DrgStatusRespirationMinutes"""

    def test_get_table_codes_0757(self):
        codes = get_table_codes(757)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0757_c_0(self):
        assert is_valid_table_value(757, '0') is True

    def test_valid_code_0757_c_1(self):
        assert is_valid_table_value(757, '1') is True

    def test_valid_code_0757_c_2(self):
        assert is_valid_table_value(757, '2') is True

    def test_invalid_code_0757(self):
        assert is_valid_table_value(757, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0757(self):
        result = validate_table_value(757, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0757(self):
        result = validate_table_value(757, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0759:
    """Tests for table 0759: DrgstatusAdmission"""

    def test_get_table_codes_0759(self):
        codes = get_table_codes(759)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0759_c_0(self):
        assert is_valid_table_value(759, '0') is True

    def test_valid_code_0759_c_1(self):
        assert is_valid_table_value(759, '1') is True

    def test_valid_code_0759_c_2(self):
        assert is_valid_table_value(759, '2') is True

    def test_valid_code_0759_c_3(self):
        assert is_valid_table_value(759, '3') is True

    def test_invalid_code_0759(self):
        assert is_valid_table_value(759, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0759(self):
        result = validate_table_value(759, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0759(self):
        result = validate_table_value(759, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0761:
    """Tests for table 0761: DrgProcedureDeterminationStatus"""

    def test_get_table_codes_0761(self):
        codes = get_table_codes(761)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0761_c_0(self):
        assert is_valid_table_value(761, '0') is True

    def test_valid_code_0761_c_1(self):
        assert is_valid_table_value(761, '1') is True

    def test_valid_code_0761_c_2(self):
        assert is_valid_table_value(761, '2') is True

    def test_valid_code_0761_c_3(self):
        assert is_valid_table_value(761, '3') is True

    def test_valid_code_0761_c_4(self):
        assert is_valid_table_value(761, '4') is True

    def test_invalid_code_0761(self):
        assert is_valid_table_value(761, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0761(self):
        result = validate_table_value(761, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0761(self):
        result = validate_table_value(761, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0763:
    """Tests for table 0763: DrgProcedureRelevance"""

    def test_get_table_codes_0763(self):
        codes = get_table_codes(763)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0763_c_0(self):
        assert is_valid_table_value(763, '0') is True

    def test_valid_code_0763_c_1(self):
        assert is_valid_table_value(763, '1') is True

    def test_valid_code_0763_c_2(self):
        assert is_valid_table_value(763, '2') is True

    def test_invalid_code_0763(self):
        assert is_valid_table_value(763, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0763(self):
        result = validate_table_value(763, '0', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0763(self):
        result = validate_table_value(763, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0776:
    """Tests for table 0776: ItemStatus"""

    def test_get_table_codes_0776(self):
        codes = get_table_codes(776)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0776_a(self):
        assert is_valid_table_value(776, 'A') is True

    def test_valid_code_0776_p(self):
        assert is_valid_table_value(776, 'P') is True

    def test_valid_code_0776_i(self):
        assert is_valid_table_value(776, 'I') is True

    def test_invalid_code_0776(self):
        assert is_valid_table_value(776, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0776(self):
        result = validate_table_value(776, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0776(self):
        result = validate_table_value(776, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0778:
    """Tests for table 0778: ItemType"""

    def test_get_table_codes_0778(self):
        codes = get_table_codes(778)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0778_eqp(self):
        assert is_valid_table_value(778, 'EQP') is True

    def test_valid_code_0778_sup(self):
        assert is_valid_table_value(778, 'SUP') is True

    def test_valid_code_0778_imp(self):
        assert is_valid_table_value(778, 'IMP') is True

    def test_valid_code_0778_med(self):
        assert is_valid_table_value(778, 'MED') is True

    def test_valid_code_0778_tdc(self):
        assert is_valid_table_value(778, 'TDC') is True

    def test_invalid_code_0778(self):
        assert is_valid_table_value(778, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0778(self):
        result = validate_table_value(778, 'EQP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0778(self):
        result = validate_table_value(778, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0790:
    """Tests for table 0790: ApprovingRegulatoryAgency"""

    def test_get_table_codes_0790(self):
        codes = get_table_codes(790)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0790_fda(self):
        assert is_valid_table_value(790, 'FDA') is True

    def test_valid_code_0790_ama(self):
        assert is_valid_table_value(790, 'AMA') is True

    def test_invalid_code_0790(self):
        assert is_valid_table_value(790, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0790(self):
        result = validate_table_value(790, 'FDA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0790(self):
        result = validate_table_value(790, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0793:
    """Tests for table 0793: RulingAct"""

    def test_get_table_codes_0793(self):
        codes = get_table_codes(793)
        assert codes is not None
        assert len(codes) == 1

    def test_valid_code_0793_smda(self):
        assert is_valid_table_value(793, 'SMDA') is True

    def test_invalid_code_0793(self):
        assert is_valid_table_value(793, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0793(self):
        result = validate_table_value(793, 'SMDA', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0793(self):
        result = validate_table_value(793, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0806:
    """Tests for table 0806: SterilizationType"""

    def test_get_table_codes_0806(self):
        codes = get_table_codes(806)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0806_eog(self):
        assert is_valid_table_value(806, 'EOG') is True

    def test_valid_code_0806_pca(self):
        assert is_valid_table_value(806, 'PCA') is True

    def test_valid_code_0806_stm(self):
        assert is_valid_table_value(806, 'STM') is True

    def test_invalid_code_0806(self):
        assert is_valid_table_value(806, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0806(self):
        result = validate_table_value(806, 'EOG', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0806(self):
        result = validate_table_value(806, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0818:
    """Tests for table 0818: Package"""

    def test_get_table_codes_0818(self):
        codes = get_table_codes(818)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0818_cs(self):
        assert is_valid_table_value(818, 'CS') is True

    def test_valid_code_0818_bx(self):
        assert is_valid_table_value(818, 'BX') is True

    def test_valid_code_0818_ea(self):
        assert is_valid_table_value(818, 'EA') is True

    def test_valid_code_0818_set(self):
        assert is_valid_table_value(818, 'SET') is True

    def test_invalid_code_0818(self):
        assert is_valid_table_value(818, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0818(self):
        result = validate_table_value(818, 'CS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0818(self):
        result = validate_table_value(818, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0834:
    """Tests for table 0834: MimeTypes"""

    def test_get_table_codes_0834(self):
        codes = get_table_codes(834)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0834_application(self):
        assert is_valid_table_value(834, 'application') is True

    def test_valid_code_0834_audio(self):
        assert is_valid_table_value(834, 'audio') is True

    def test_valid_code_0834_image(self):
        assert is_valid_table_value(834, 'image') is True

    def test_valid_code_0834_model(self):
        assert is_valid_table_value(834, 'model') is True

    def test_valid_code_0834_text(self):
        assert is_valid_table_value(834, 'text') is True

    def test_invalid_code_0834(self):
        assert is_valid_table_value(834, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0834(self):
        result = validate_table_value(834, 'application', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0834(self):
        result = validate_table_value(834, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0868:
    """Tests for table 0868: TelecommunicationExpirationReason"""

    def test_get_table_codes_0868(self):
        codes = get_table_codes(868)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0868_m(self):
        assert is_valid_table_value(868, 'M') is True

    def test_valid_code_0868_e(self):
        assert is_valid_table_value(868, 'E') is True

    def test_valid_code_0868_r(self):
        assert is_valid_table_value(868, 'R') is True

    def test_valid_code_0868_c(self):
        assert is_valid_table_value(868, 'C') is True

    def test_valid_code_0868_n(self):
        assert is_valid_table_value(868, 'N') is True

    def test_invalid_code_0868(self):
        assert is_valid_table_value(868, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0868(self):
        result = validate_table_value(868, 'M', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0868(self):
        result = validate_table_value(868, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0871:
    """Tests for table 0871: SupplyRisk"""

    def test_get_table_codes_0871(self):
        codes = get_table_codes(871)
        assert codes is not None
        assert len(codes) == 7

    def test_valid_code_0871_cor(self):
        assert is_valid_table_value(871, 'COR') is True

    def test_valid_code_0871_fla(self):
        assert is_valid_table_value(871, 'FLA') is True

    def test_valid_code_0871_exp(self):
        assert is_valid_table_value(871, 'EXP') is True

    def test_valid_code_0871_inj(self):
        assert is_valid_table_value(871, 'INJ') is True

    def test_valid_code_0871_tox(self):
        assert is_valid_table_value(871, 'TOX') is True

    def test_invalid_code_0871(self):
        assert is_valid_table_value(871, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0871(self):
        result = validate_table_value(871, 'COR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0871(self):
        result = validate_table_value(871, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0881:
    """Tests for table 0881: RoleExecutingPhysician"""

    def test_get_table_codes_0881(self):
        codes = get_table_codes(881)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0881_t(self):
        assert is_valid_table_value(881, 'T') is True

    def test_valid_code_0881_p(self):
        assert is_valid_table_value(881, 'P') is True

    def test_valid_code_0881_b(self):
        assert is_valid_table_value(881, 'B') is True

    def test_invalid_code_0881(self):
        assert is_valid_table_value(881, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0881(self):
        result = validate_table_value(881, 'T', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0881(self):
        result = validate_table_value(881, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0882:
    """Tests for table 0882: MedicalRoleExecutingPhysician"""

    def test_get_table_codes_0882(self):
        codes = get_table_codes(882)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0882_e(self):
        assert is_valid_table_value(882, 'E') is True

    def test_valid_code_0882_se(self):
        assert is_valid_table_value(882, 'SE') is True

    def test_invalid_code_0882(self):
        assert is_valid_table_value(882, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0882(self):
        result = validate_table_value(882, 'E', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0882(self):
        result = validate_table_value(882, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0894:
    """Tests for table 0894: SideOfBody"""

    def test_get_table_codes_0894(self):
        codes = get_table_codes(894)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0894_l(self):
        assert is_valid_table_value(894, 'L') is True

    def test_valid_code_0894_r(self):
        assert is_valid_table_value(894, 'R') is True

    def test_invalid_code_0894(self):
        assert is_valid_table_value(894, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0894(self):
        result = validate_table_value(894, 'L', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0894(self):
        result = validate_table_value(894, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0904:
    """Tests for table 0904: SecurityCheckScheme"""

    def test_get_table_codes_0904(self):
        codes = get_table_codes(904)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0904_bcv(self):
        assert is_valid_table_value(904, 'BCV') is True

    def test_valid_code_0904_ccs(self):
        assert is_valid_table_value(904, 'CCS') is True

    def test_valid_code_0904_vid(self):
        assert is_valid_table_value(904, 'VID') is True

    def test_invalid_code_0904(self):
        assert is_valid_table_value(904, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0904(self):
        result = validate_table_value(904, 'BCV', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0904(self):
        result = validate_table_value(904, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0905:
    """Tests for table 0905: ShipmentStatus"""

    def test_get_table_codes_0905(self):
        codes = get_table_codes(905)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0905_onh(self):
        assert is_valid_table_value(905, 'ONH') is True

    def test_valid_code_0905_inv(self):
        assert is_valid_table_value(905, 'INV') is True

    def test_valid_code_0905_prc(self):
        assert is_valid_table_value(905, 'PRC') is True

    def test_valid_code_0905_rej(self):
        assert is_valid_table_value(905, 'REJ') is True

    def test_valid_code_0905_ttl(self):
        assert is_valid_table_value(905, 'TTL') is True

    def test_invalid_code_0905(self):
        assert is_valid_table_value(905, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0905(self):
        result = validate_table_value(905, 'ONH', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0905(self):
        result = validate_table_value(905, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0906:
    """Tests for table 0906: Actpriority"""

    def test_get_table_codes_0906(self):
        codes = get_table_codes(906)
        assert codes is not None
        assert len(codes) == 15

    def test_valid_code_0906_a(self):
        assert is_valid_table_value(906, 'A') is True

    def test_valid_code_0906_cr(self):
        assert is_valid_table_value(906, 'CR') is True

    def test_valid_code_0906_cs(self):
        assert is_valid_table_value(906, 'CS') is True

    def test_valid_code_0906_csp(self):
        assert is_valid_table_value(906, 'CSP') is True

    def test_valid_code_0906_csr(self):
        assert is_valid_table_value(906, 'CSR') is True

    def test_invalid_code_0906(self):
        assert is_valid_table_value(906, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0906(self):
        result = validate_table_value(906, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0906(self):
        result = validate_table_value(906, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0907:
    """Tests for table 0907: Confidentiality"""

    def test_get_table_codes_0907(self):
        codes = get_table_codes(907)
        assert codes is not None
        assert len(codes) == 14

    def test_valid_code_0907_b(self):
        assert is_valid_table_value(907, 'B') is True

    def test_valid_code_0907_d(self):
        assert is_valid_table_value(907, 'D') is True

    def test_valid_code_0907_i(self):
        assert is_valid_table_value(907, 'I') is True

    def test_valid_code_0907_l(self):
        assert is_valid_table_value(907, 'L') is True

    def test_valid_code_0907_n(self):
        assert is_valid_table_value(907, 'N') is True

    def test_invalid_code_0907(self):
        assert is_valid_table_value(907, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0907(self):
        result = validate_table_value(907, 'B', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0907(self):
        result = validate_table_value(907, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0909:
    """Tests for table 0909: PatientResultsReleaseCategorizationScheme"""

    def test_get_table_codes_0909(self):
        codes = get_table_codes(909)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0909_stbd(self):
        assert is_valid_table_value(909, 'STBD') is True

    def test_valid_code_0909_simm(self):
        assert is_valid_table_value(909, 'SIMM') is True

    def test_valid_code_0909_swnl(self):
        assert is_valid_table_value(909, 'SWNL') is True

    def test_valid_code_0909_sid(self):
        assert is_valid_table_value(909, 'SID') is True

    def test_valid_code_0909_sidc(self):
        assert is_valid_table_value(909, 'SIDC') is True

    def test_invalid_code_0909(self):
        assert is_valid_table_value(909, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0909(self):
        result = validate_table_value(909, 'STBD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0909(self):
        result = validate_table_value(909, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0912:
    """Tests for table 0912: Participation"""

    def test_get_table_codes_0912(self):
        codes = get_table_codes(912)
        assert codes is not None
        assert len(codes) == 52

    def test_valid_code_0912_aap(self):
        assert is_valid_table_value(912, 'AAP') is True

    def test_valid_code_0912_ac(self):
        assert is_valid_table_value(912, 'AC') is True

    def test_valid_code_0912_ad(self):
        assert is_valid_table_value(912, 'AD') is True

    def test_valid_code_0912_ahp(self):
        assert is_valid_table_value(912, 'AHP') is True

    def test_valid_code_0912_ai(self):
        assert is_valid_table_value(912, 'AI') is True

    def test_invalid_code_0912(self):
        assert is_valid_table_value(912, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0912(self):
        result = validate_table_value(912, 'AAP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0912(self):
        result = validate_table_value(912, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0914:
    """Tests for table 0914: RootCause"""

    def test_get_table_codes_0914(self):
        codes = get_table_codes(914)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0914_ap(self):
        assert is_valid_table_value(914, 'AP') is True

    def test_valid_code_0914_im(self):
        assert is_valid_table_value(914, 'IM') is True

    def test_valid_code_0914_l(self):
        assert is_valid_table_value(914, 'L') is True

    def test_valid_code_0914_na(self):
        assert is_valid_table_value(914, 'NA') is True

    def test_valid_code_0914_pd(self):
        assert is_valid_table_value(914, 'PD') is True

    def test_invalid_code_0914(self):
        assert is_valid_table_value(914, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0914(self):
        result = validate_table_value(914, 'AP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0914(self):
        result = validate_table_value(914, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0916:
    """Tests for table 0916: RelevantClincialInformation"""

    def test_get_table_codes_0916(self):
        codes = get_table_codes(916)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0916_f(self):
        assert is_valid_table_value(916, 'F') is True

    def test_valid_code_0916_nf(self):
        assert is_valid_table_value(916, 'NF') is True

    def test_valid_code_0916_ng(self):
        assert is_valid_table_value(916, 'NG') is True

    def test_valid_code_0916_fna(self):
        assert is_valid_table_value(916, 'FNA') is True

    def test_invalid_code_0916(self):
        assert is_valid_table_value(916, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0916(self):
        result = validate_table_value(916, 'F', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0916(self):
        result = validate_table_value(916, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0917:
    """Tests for table 0917: BolusType"""

    def test_get_table_codes_0917(self):
        codes = get_table_codes(917)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0917_c(self):
        assert is_valid_table_value(917, 'C') is True

    def test_valid_code_0917_l(self):
        assert is_valid_table_value(917, 'L') is True

    def test_invalid_code_0917(self):
        assert is_valid_table_value(917, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0917(self):
        result = validate_table_value(917, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0917(self):
        result = validate_table_value(917, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0918:
    """Tests for table 0918: PcaType"""

    def test_get_table_codes_0918(self):
        codes = get_table_codes(918)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0918_c(self):
        assert is_valid_table_value(918, 'C') is True

    def test_valid_code_0918_p(self):
        assert is_valid_table_value(918, 'P') is True

    def test_valid_code_0918_pc(self):
        assert is_valid_table_value(918, 'PC') is True

    def test_invalid_code_0918(self):
        assert is_valid_table_value(918, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0918(self):
        result = validate_table_value(918, 'C', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0918(self):
        result = validate_table_value(918, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0919:
    """Tests for table 0919: ExclusiveTest"""

    def test_get_table_codes_0919(self):
        codes = get_table_codes(919)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0919_y(self):
        assert is_valid_table_value(919, 'Y') is True

    def test_valid_code_0919_n(self):
        assert is_valid_table_value(919, 'N') is True

    def test_valid_code_0919_d(self):
        assert is_valid_table_value(919, 'D') is True

    def test_invalid_code_0919(self):
        assert is_valid_table_value(919, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0919(self):
        result = validate_table_value(919, 'Y', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0919(self):
        result = validate_table_value(919, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0920:
    """Tests for table 0920: PreferredSpecimenAttributeStatus"""

    def test_get_table_codes_0920(self):
        codes = get_table_codes(920)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0920_p(self):
        assert is_valid_table_value(920, 'P') is True

    def test_valid_code_0920_a(self):
        assert is_valid_table_value(920, 'A') is True

    def test_invalid_code_0920(self):
        assert is_valid_table_value(920, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0920(self):
        result = validate_table_value(920, 'P', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0920(self):
        result = validate_table_value(920, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0921:
    """Tests for table 0921: CertificationType"""

    def test_get_table_codes_0921(self):
        codes = get_table_codes(921)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0921_adm(self):
        assert is_valid_table_value(921, 'ADM') is True

    def test_valid_code_0921_serv(self):
        assert is_valid_table_value(921, 'SERV') is True

    def test_valid_code_0921_proc(self):
        assert is_valid_table_value(921, 'PROC') is True

    def test_invalid_code_0921(self):
        assert is_valid_table_value(921, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0921(self):
        result = validate_table_value(921, 'ADM', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0921(self):
        result = validate_table_value(921, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0922:
    """Tests for table 0922: CertificationCategory"""

    def test_get_table_codes_0922(self):
        codes = get_table_codes(922)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0922_ir(self):
        assert is_valid_table_value(922, 'IR') is True

    def test_valid_code_0922_ra(self):
        assert is_valid_table_value(922, 'RA') is True

    def test_valid_code_0922_re(self):
        assert is_valid_table_value(922, 'RE') is True

    def test_invalid_code_0922(self):
        assert is_valid_table_value(922, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0922(self):
        result = validate_table_value(922, 'IR', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0922(self):
        result = validate_table_value(922, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0923:
    """Tests for table 0923: ProcessInterruption"""

    def test_get_table_codes_0923(self):
        codes = get_table_codes(923)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0923_nin(self):
        assert is_valid_table_value(923, 'NIN') is True

    def test_valid_code_0923_wot(self):
        assert is_valid_table_value(923, 'WOT') is True

    def test_valid_code_0923_abr(self):
        assert is_valid_table_value(923, 'ABR') is True

    def test_invalid_code_0923(self):
        assert is_valid_table_value(923, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0923(self):
        result = validate_table_value(923, 'NIN', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0923(self):
        result = validate_table_value(923, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0924:
    """Tests for table 0924: CumulativeDosageLimitUom"""

    def test_get_table_codes_0924(self):
        codes = get_table_codes(924)
        assert codes is not None
        assert len(codes) == 6

    def test_valid_code_0924_a(self):
        assert is_valid_table_value(924, 'A') is True

    def test_valid_code_0924_d(self):
        assert is_valid_table_value(924, 'D') is True

    def test_valid_code_0924_m(self):
        assert is_valid_table_value(924, 'M') is True

    def test_valid_code_0924_o(self):
        assert is_valid_table_value(924, 'O') is True

    def test_valid_code_0924_pl(self):
        assert is_valid_table_value(924, 'PL') is True

    def test_invalid_code_0924(self):
        assert is_valid_table_value(924, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0924(self):
        result = validate_table_value(924, 'A', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0924(self):
        result = validate_table_value(924, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0925:
    """Tests for table 0925: PhlebotomyIssue"""

    def test_get_table_codes_0925(self):
        codes = get_table_codes(925)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0925_inf(self):
        assert is_valid_table_value(925, 'INF') is True

    def test_valid_code_0925_vsm(self):
        assert is_valid_table_value(925, 'VSM') is True

    def test_valid_code_0925_col(self):
        assert is_valid_table_value(925, 'COL') is True

    def test_valid_code_0925_mis(self):
        assert is_valid_table_value(925, 'MIS') is True

    def test_valid_code_0925_nad(self):
        assert is_valid_table_value(925, 'NAD') is True

    def test_invalid_code_0925(self):
        assert is_valid_table_value(925, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0925(self):
        result = validate_table_value(925, 'INF', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0925(self):
        result = validate_table_value(925, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0926:
    """Tests for table 0926: PhlebotomyStatus"""

    def test_get_table_codes_0926(self):
        codes = get_table_codes(926)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0926_suc(self):
        assert is_valid_table_value(926, 'SUC') is True

    def test_valid_code_0926_ndr(self):
        assert is_valid_table_value(926, 'NDR') is True

    def test_valid_code_0926_ul5(self):
        assert is_valid_table_value(926, 'UL5') is True

    def test_invalid_code_0926(self):
        assert is_valid_table_value(926, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0926(self):
        result = validate_table_value(926, 'SUC', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0926(self):
        result = validate_table_value(926, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0927:
    """Tests for table 0927: ArmStick"""

    def test_get_table_codes_0927(self):
        codes = get_table_codes(927)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0927_l(self):
        assert is_valid_table_value(927, 'L') is True

    def test_valid_code_0927_r(self):
        assert is_valid_table_value(927, 'R') is True

    def test_valid_code_0927_b(self):
        assert is_valid_table_value(927, 'B') is True

    def test_invalid_code_0927(self):
        assert is_valid_table_value(927, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0927(self):
        result = validate_table_value(927, 'L', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0927(self):
        result = validate_table_value(927, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0933:
    """Tests for table 0933: IntendedProcedureType"""

    def test_get_table_codes_0933(self):
        codes = get_table_codes(933)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0933_wbl(self):
        assert is_valid_table_value(933, 'WBL') is True

    def test_valid_code_0933_c_2rc(self):
        assert is_valid_table_value(933, '2RC') is True

    def test_valid_code_0933_pls(self):
        assert is_valid_table_value(933, 'PLS') is True

    def test_valid_code_0933_plt(self):
        assert is_valid_table_value(933, 'PLT') is True

    def test_valid_code_0933_pnp(self):
        assert is_valid_table_value(933, 'PNP') is True

    def test_invalid_code_0933(self):
        assert is_valid_table_value(933, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0933(self):
        result = validate_table_value(933, 'WBL', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0933(self):
        result = validate_table_value(933, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0935:
    """Tests for table 0935: ProcessInterruptionReason"""

    def test_get_table_codes_0935(self):
        codes = get_table_codes(935)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0935_nrg(self):
        assert is_valid_table_value(935, 'NRG') is True

    def test_valid_code_0935_pcd(self):
        assert is_valid_table_value(935, 'PCD') is True

    def test_valid_code_0935_dcw(self):
        assert is_valid_table_value(935, 'DCW') is True

    def test_valid_code_0935_cft(self):
        assert is_valid_table_value(935, 'CFT') is True

    def test_valid_code_0935_dbb(self):
        assert is_valid_table_value(935, 'DBB') is True

    def test_invalid_code_0935(self):
        assert is_valid_table_value(935, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0935(self):
        result = validate_table_value(935, 'NRG', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0935(self):
        result = validate_table_value(935, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0936:
    """Tests for table 0936: ObservationType"""

    def test_get_table_codes_0936(self):
        codes = get_table_codes(936)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0936_qst(self):
        assert is_valid_table_value(936, 'QST') is True

    def test_valid_code_0936_rslt(self):
        assert is_valid_table_value(936, 'RSLT') is True

    def test_valid_code_0936_sci(self):
        assert is_valid_table_value(936, 'SCI') is True

    def test_invalid_code_0936(self):
        assert is_valid_table_value(936, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0936(self):
        result = validate_table_value(936, 'QST', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0936(self):
        result = validate_table_value(936, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0937:
    """Tests for table 0937: ObservationSubtype"""

    def test_get_table_codes_0937(self):
        codes = get_table_codes(937)
        assert codes is not None
        assert len(codes) == 14

    def test_valid_code_0937_aoe(self):
        assert is_valid_table_value(937, 'AOE') is True

    def test_valid_code_0937_asc(self):
        assert is_valid_table_value(937, 'ASC') is True

    def test_valid_code_0937_mcs(self):
        assert is_valid_table_value(937, 'MCS') is True

    def test_valid_code_0937_mid(self):
        assert is_valid_table_value(937, 'MID') is True

    def test_valid_code_0937_mig(self):
        assert is_valid_table_value(937, 'MIG') is True

    def test_invalid_code_0937(self):
        assert is_valid_table_value(937, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0937(self):
        result = validate_table_value(937, 'AOE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0937(self):
        result = validate_table_value(937, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0938:
    """Tests for table 0938: CollectionEvent"""

    def test_get_table_codes_0938(self):
        codes = get_table_codes(938)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0938_ord(self):
        assert is_valid_table_value(938, 'ORD') is True

    def test_valid_code_0938_drw(self):
        assert is_valid_table_value(938, 'DRW') is True

    def test_invalid_code_0938(self):
        assert is_valid_table_value(938, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0938(self):
        result = validate_table_value(938, 'ORD', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0938(self):
        result = validate_table_value(938, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0939:
    """Tests for table 0939: CommunicationLocation"""

    def test_get_table_codes_0939(self):
        codes = get_table_codes(939)
        assert codes is not None
        assert len(codes) == 21

    def test_valid_code_0939_obr_obx(self):
        assert is_valid_table_value(939, 'OBR-OBX') is True

    def test_valid_code_0939_spm_obx(self):
        assert is_valid_table_value(939, 'SPM-OBX') is True

    def test_valid_code_0939_dg1_3(self):
        assert is_valid_table_value(939, 'DG1-3') is True

    def test_valid_code_0939_nk1_11(self):
        assert is_valid_table_value(939, 'NK1-11') is True

    def test_valid_code_0939_nk1_13(self):
        assert is_valid_table_value(939, 'NK1-13') is True

    def test_invalid_code_0939(self):
        assert is_valid_table_value(939, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0939(self):
        result = validate_table_value(939, 'OBR-OBX', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0939(self):
        result = validate_table_value(939, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0940:
    """Tests for table 0940: LimitationTypeCode"""

    def test_get_table_codes_0940(self):
        codes = get_table_codes(940)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0940_lcp(self):
        assert is_valid_table_value(940, 'LCP') is True

    def test_valid_code_0940_nfda(self):
        assert is_valid_table_value(940, 'NFDA') is True

    def test_valid_code_0940_fldp(self):
        assert is_valid_table_value(940, 'FLDP') is True

    def test_valid_code_0940_nt(self):
        assert is_valid_table_value(940, 'NT') is True

    def test_invalid_code_0940(self):
        assert is_valid_table_value(940, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0940(self):
        result = validate_table_value(940, 'LCP', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0940(self):
        result = validate_table_value(940, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0942:
    """Tests for table 0942: EquipmentStateIndicator"""

    def test_get_table_codes_0942(self):
        codes = get_table_codes(942)
        assert codes is not None
        assert len(codes) == 5

    def test_valid_code_0942_eb(self):
        assert is_valid_table_value(942, 'EB') is True

    def test_valid_code_0942_ib(self):
        assert is_valid_table_value(942, 'IB') is True

    def test_valid_code_0942_ic(self):
        assert is_valid_table_value(942, 'IC') is True

    def test_valid_code_0942_ob(self):
        assert is_valid_table_value(942, 'OB') is True

    def test_valid_code_0942_ta(self):
        assert is_valid_table_value(942, 'TA') is True

    def test_invalid_code_0942(self):
        assert is_valid_table_value(942, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0942(self):
        result = validate_table_value(942, 'EB', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0942(self):
        result = validate_table_value(942, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0945:
    """Tests for table 0945: AutoDilutionType"""

    def test_get_table_codes_0945(self):
        codes = get_table_codes(945)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0945_x2(self):
        assert is_valid_table_value(945, 'X2') is True

    def test_valid_code_0945_x5(self):
        assert is_valid_table_value(945, 'X5') is True

    def test_valid_code_0945_d1(self):
        assert is_valid_table_value(945, 'D1') is True

    def test_valid_code_0945_d2(self):
        assert is_valid_table_value(945, 'D2') is True

    def test_invalid_code_0945(self):
        assert is_valid_table_value(945, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0945(self):
        result = validate_table_value(945, 'X2', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0945(self):
        result = validate_table_value(945, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0946:
    """Tests for table 0946: SupplierType"""

    def test_get_table_codes_0946(self):
        codes = get_table_codes(946)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0946_d(self):
        assert is_valid_table_value(946, 'D') is True

    def test_valid_code_0946_m(self):
        assert is_valid_table_value(946, 'M') is True

    def test_invalid_code_0946(self):
        assert is_valid_table_value(946, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0946(self):
        result = validate_table_value(946, 'D', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0946(self):
        result = validate_table_value(946, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0948:
    """Tests for table 0948: V2CSRelationshipType"""

    def test_get_table_codes_0948(self):
        codes = get_table_codes(948)
        assert codes is not None
        assert len(codes) == 9

    def test_valid_code_0948_caus(self):
        assert is_valid_table_value(948, 'CAUS') is True

    def test_valid_code_0948_comp(self):
        assert is_valid_table_value(948, 'COMP') is True

    def test_valid_code_0948_concr(self):
        assert is_valid_table_value(948, 'CONCR') is True

    def test_valid_code_0948_evid(self):
        assert is_valid_table_value(948, 'EVID') is True

    def test_valid_code_0948_intf(self):
        assert is_valid_table_value(948, 'INTF') is True

    def test_invalid_code_0948(self):
        assert is_valid_table_value(948, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0948(self):
        result = validate_table_value(948, 'CAUS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0948(self):
        result = validate_table_value(948, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0949:
    """Tests for table 0949: OrderControlCodeReason"""

    def test_get_table_codes_0949(self):
        codes = get_table_codes(949)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0949_co(self):
        assert is_valid_table_value(949, 'CO') is True

    def test_valid_code_0949_st(self):
        assert is_valid_table_value(949, 'ST') is True

    def test_valid_code_0949_sv(self):
        assert is_valid_table_value(949, 'SV') is True

    def test_valid_code_0949_un(self):
        assert is_valid_table_value(949, 'UN') is True

    def test_invalid_code_0949(self):
        assert is_valid_table_value(949, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0949(self):
        result = validate_table_value(949, 'CO', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0949(self):
        result = validate_table_value(949, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0950:
    """Tests for table 0950: OrderStatusModifier"""

    def test_get_table_codes_0950(self):
        codes = get_table_codes(950)
        assert codes is not None
        assert len(codes) == 2

    def test_valid_code_0950_eoe(self):
        assert is_valid_table_value(950, 'EOE') is True

    def test_valid_code_0950_eot(self):
        assert is_valid_table_value(950, 'EOT') is True

    def test_invalid_code_0950(self):
        assert is_valid_table_value(950, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0950(self):
        result = validate_table_value(950, 'EOE', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0950(self):
        result = validate_table_value(950, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0951:
    """Tests for table 0951: ReasonForStudy"""

    def test_get_table_codes_0951(self):
        codes = get_table_codes(951)
        assert codes is not None
        assert len(codes) == 13

    def test_valid_code_0951_bs(self):
        assert is_valid_table_value(951, 'BS') is True

    def test_valid_code_0951_cr(self):
        assert is_valid_table_value(951, 'CR') is True

    def test_valid_code_0951_fp(self):
        assert is_valid_table_value(951, 'FP') is True

    def test_valid_code_0951_in(self):
        assert is_valid_table_value(951, 'IN') is True

    def test_valid_code_0951_ir(self):
        assert is_valid_table_value(951, 'IR') is True

    def test_invalid_code_0951(self):
        assert is_valid_table_value(951, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0951(self):
        result = validate_table_value(951, 'BS', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0951(self):
        result = validate_table_value(951, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0970:
    """Tests for table 0970: OnlineVerificationResult"""

    def test_get_table_codes_0970(self):
        codes = get_table_codes(970)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_0970_c_1(self):
        assert is_valid_table_value(970, '1') is True

    def test_valid_code_0970_c_2(self):
        assert is_valid_table_value(970, '2') is True

    def test_valid_code_0970_c_3(self):
        assert is_valid_table_value(970, '3') is True

    def test_invalid_code_0970(self):
        assert is_valid_table_value(970, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0970(self):
        result = validate_table_value(970, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0970(self):
        result = validate_table_value(970, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable0971:
    """Tests for table 0971: OnlineVerificationResultErrorCodes"""

    def test_get_table_codes_0971(self):
        codes = get_table_codes(971)
        assert codes is not None
        assert len(codes) == 4

    def test_valid_code_0971_c_1(self):
        assert is_valid_table_value(971, '1') is True

    def test_valid_code_0971_c_2(self):
        assert is_valid_table_value(971, '2') is True

    def test_valid_code_0971_c_3(self):
        assert is_valid_table_value(971, '3') is True

    def test_valid_code_0971_c_4(self):
        assert is_valid_table_value(971, '4') is True

    def test_invalid_code_0971(self):
        assert is_valid_table_value(971, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_0971(self):
        result = validate_table_value(971, '1', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_0971(self):
        result = validate_table_value(971, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'


class TestTable4000:
    """Tests for table 4000: NameAddressRepresentation"""

    def test_get_table_codes_4000(self):
        codes = get_table_codes(4000)
        assert codes is not None
        assert len(codes) == 3

    def test_valid_code_4000_i(self):
        assert is_valid_table_value(4000, 'I') is True

    def test_valid_code_4000_a(self):
        assert is_valid_table_value(4000, 'A') is True

    def test_valid_code_4000_p(self):
        assert is_valid_table_value(4000, 'P') is True

    def test_invalid_code_4000(self):
        assert is_valid_table_value(4000, 'INVALID_TEST_VALUE_XYZ') is False

    def test_validate_valid_4000(self):
        result = validate_table_value(4000, 'I', 'TEST.1')
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_4000(self):
        result = validate_table_value(4000, 'INVALID_TEST_VALUE_XYZ', 'TEST.1')
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == 'INVALID_TABLE_VALUE'

