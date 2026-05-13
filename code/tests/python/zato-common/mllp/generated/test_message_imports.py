from __future__ import annotations

import pytest


class TestMessageClassImports:
    """Test that all message classes can be imported directly."""

    def test_import_ack(self):
        from zato.hl7v2.v2_9.messages import Ack
        assert Ack._structure_id == "ACK"

    def test_import_adt_a01(self):
        from zato.hl7v2.v2_9.messages import AdtA01
        assert AdtA01._structure_id == "ADT_A01"

    def test_import_adt_a02(self):
        from zato.hl7v2.v2_9.messages import AdtA02
        assert AdtA02._structure_id == "ADT_A02"

    def test_import_adt_a03(self):
        from zato.hl7v2.v2_9.messages import AdtA03
        assert AdtA03._structure_id == "ADT_A03"

    def test_import_adt_a05(self):
        from zato.hl7v2.v2_9.messages import AdtA05
        assert AdtA05._structure_id == "ADT_A05"

    def test_import_adt_a06(self):
        from zato.hl7v2.v2_9.messages import AdtA06
        assert AdtA06._structure_id == "ADT_A06"

    def test_import_adt_a09(self):
        from zato.hl7v2.v2_9.messages import AdtA09
        assert AdtA09._structure_id == "ADT_A09"

    def test_import_adt_a12(self):
        from zato.hl7v2.v2_9.messages import AdtA12
        assert AdtA12._structure_id == "ADT_A12"

    def test_import_adt_a15(self):
        from zato.hl7v2.v2_9.messages import AdtA15
        assert AdtA15._structure_id == "ADT_A15"

    def test_import_adt_a16(self):
        from zato.hl7v2.v2_9.messages import AdtA16
        assert AdtA16._structure_id == "ADT_A16"

    def test_import_adt_a17(self):
        from zato.hl7v2.v2_9.messages import AdtA17
        assert AdtA17._structure_id == "ADT_A17"

    def test_import_adt_a20(self):
        from zato.hl7v2.v2_9.messages import AdtA20
        assert AdtA20._structure_id == "ADT_A20"

    def test_import_adt_a21(self):
        from zato.hl7v2.v2_9.messages import AdtA21
        assert AdtA21._structure_id == "ADT_A21"

    def test_import_adt_a24(self):
        from zato.hl7v2.v2_9.messages import AdtA24
        assert AdtA24._structure_id == "ADT_A24"

    def test_import_adt_a37(self):
        from zato.hl7v2.v2_9.messages import AdtA37
        assert AdtA37._structure_id == "ADT_A37"

    def test_import_adt_a38(self):
        from zato.hl7v2.v2_9.messages import AdtA38
        assert AdtA38._structure_id == "ADT_A38"

    def test_import_adt_a39(self):
        from zato.hl7v2.v2_9.messages import AdtA39
        assert AdtA39._structure_id == "ADT_A39"

    def test_import_adt_a43(self):
        from zato.hl7v2.v2_9.messages import AdtA43
        assert AdtA43._structure_id == "ADT_A43"

    def test_import_adt_a44(self):
        from zato.hl7v2.v2_9.messages import AdtA44
        assert AdtA44._structure_id == "ADT_A44"

    def test_import_adt_a45(self):
        from zato.hl7v2.v2_9.messages import AdtA45
        assert AdtA45._structure_id == "ADT_A45"

    def test_import_adt_a50(self):
        from zato.hl7v2.v2_9.messages import AdtA50
        assert AdtA50._structure_id == "ADT_A50"

    def test_import_adt_a52(self):
        from zato.hl7v2.v2_9.messages import AdtA52
        assert AdtA52._structure_id == "ADT_A52"

    def test_import_adt_a54(self):
        from zato.hl7v2.v2_9.messages import AdtA54
        assert AdtA54._structure_id == "ADT_A54"

    def test_import_adt_a60(self):
        from zato.hl7v2.v2_9.messages import AdtA60
        assert AdtA60._structure_id == "ADT_A60"

    def test_import_adt_a61(self):
        from zato.hl7v2.v2_9.messages import AdtA61
        assert AdtA61._structure_id == "ADT_A61"

    def test_import_bar_p01(self):
        from zato.hl7v2.v2_9.messages import BarP01
        assert BarP01._structure_id == "BAR_P01"

    def test_import_bar_p02(self):
        from zato.hl7v2.v2_9.messages import BarP02
        assert BarP02._structure_id == "BAR_P02"

    def test_import_bar_p05(self):
        from zato.hl7v2.v2_9.messages import BarP05
        assert BarP05._structure_id == "BAR_P05"

    def test_import_bar_p06(self):
        from zato.hl7v2.v2_9.messages import BarP06
        assert BarP06._structure_id == "BAR_P06"

    def test_import_bar_p10(self):
        from zato.hl7v2.v2_9.messages import BarP10
        assert BarP10._structure_id == "BAR_P10"

    def test_import_bar_p12(self):
        from zato.hl7v2.v2_9.messages import BarP12
        assert BarP12._structure_id == "BAR_P12"

    def test_import_bps_o29(self):
        from zato.hl7v2.v2_9.messages import BpsO29
        assert BpsO29._structure_id == "BPS_O29"

    def test_import_brp_o30(self):
        from zato.hl7v2.v2_9.messages import BrpO30
        assert BrpO30._structure_id == "BRP_O30"

    def test_import_brt_o32(self):
        from zato.hl7v2.v2_9.messages import BrtO32
        assert BrtO32._structure_id == "BRT_O32"

    def test_import_bts_o31(self):
        from zato.hl7v2.v2_9.messages import BtsO31
        assert BtsO31._structure_id == "BTS_O31"

    def test_import_ccf_i22(self):
        from zato.hl7v2.v2_9.messages import CcfI22
        assert CcfI22._structure_id == "CCF_I22"

    def test_import_cci_i22(self):
        from zato.hl7v2.v2_9.messages import CciI22
        assert CciI22._structure_id == "CCI_I22"

    def test_import_ccm_i21(self):
        from zato.hl7v2.v2_9.messages import CcmI21
        assert CcmI21._structure_id == "CCM_I21"

    def test_import_ccq_i19(self):
        from zato.hl7v2.v2_9.messages import CcqI19
        assert CcqI19._structure_id == "CCQ_I19"

    def test_import_ccr_i16(self):
        from zato.hl7v2.v2_9.messages import CcrI16
        assert CcrI16._structure_id == "CCR_I16"

    def test_import_ccu_i20(self):
        from zato.hl7v2.v2_9.messages import CcuI20
        assert CcuI20._structure_id == "CCU_I20"

    def test_import_cqu_i19(self):
        from zato.hl7v2.v2_9.messages import CquI19
        assert CquI19._structure_id == "CQU_I19"

    def test_import_crm_c01(self):
        from zato.hl7v2.v2_9.messages import CrmC01
        assert CrmC01._structure_id == "CRM_C01"

    def test_import_csu_c09(self):
        from zato.hl7v2.v2_9.messages import CsuC09
        assert CsuC09._structure_id == "CSU_C09"

    def test_import_dbc_o41(self):
        from zato.hl7v2.v2_9.messages import DbcO41
        assert DbcO41._structure_id == "DBC_O41"

    def test_import_dbc_o42(self):
        from zato.hl7v2.v2_9.messages import DbcO42
        assert DbcO42._structure_id == "DBC_O42"

    def test_import_del_o46(self):
        from zato.hl7v2.v2_9.messages import DelO46
        assert DelO46._structure_id == "DEL_O46"

    def test_import_deo_o45(self):
        from zato.hl7v2.v2_9.messages import DeoO45
        assert DeoO45._structure_id == "DEO_O45"

    def test_import_der_o44(self):
        from zato.hl7v2.v2_9.messages import DerO44
        assert DerO44._structure_id == "DER_O44"

    def test_import_dft_p03(self):
        from zato.hl7v2.v2_9.messages import DftP03
        assert DftP03._structure_id == "DFT_P03"

    def test_import_dft_p11(self):
        from zato.hl7v2.v2_9.messages import DftP11
        assert DftP11._structure_id == "DFT_P11"

    def test_import_dpr_o48(self):
        from zato.hl7v2.v2_9.messages import DprO48
        assert DprO48._structure_id == "DPR_O48"

    def test_import_drc_o47(self):
        from zato.hl7v2.v2_9.messages import DrcO47
        assert DrcO47._structure_id == "DRC_O47"

    def test_import_drg_o43(self):
        from zato.hl7v2.v2_9.messages import DrgO43
        assert DrgO43._structure_id == "DRG_O43"

    def test_import_eac_u07(self):
        from zato.hl7v2.v2_9.messages import EacU07
        assert EacU07._structure_id == "EAC_U07"

    def test_import_ean_u09(self):
        from zato.hl7v2.v2_9.messages import EanU09
        assert EanU09._structure_id == "EAN_U09"

    def test_import_ear_u08(self):
        from zato.hl7v2.v2_9.messages import EarU08
        assert EarU08._structure_id == "EAR_U08"

    def test_import_ehc_e01(self):
        from zato.hl7v2.v2_9.messages import EhcE01
        assert EhcE01._structure_id == "EHC_E01"

    def test_import_ehc_e02(self):
        from zato.hl7v2.v2_9.messages import EhcE02
        assert EhcE02._structure_id == "EHC_E02"

    def test_import_ehc_e04(self):
        from zato.hl7v2.v2_9.messages import EhcE04
        assert EhcE04._structure_id == "EHC_E04"

    def test_import_ehc_e10(self):
        from zato.hl7v2.v2_9.messages import EhcE10
        assert EhcE10._structure_id == "EHC_E10"

    def test_import_ehc_e12(self):
        from zato.hl7v2.v2_9.messages import EhcE12
        assert EhcE12._structure_id == "EHC_E12"

    def test_import_ehc_e13(self):
        from zato.hl7v2.v2_9.messages import EhcE13
        assert EhcE13._structure_id == "EHC_E13"

    def test_import_ehc_e15(self):
        from zato.hl7v2.v2_9.messages import EhcE15
        assert EhcE15._structure_id == "EHC_E15"

    def test_import_ehc_e20(self):
        from zato.hl7v2.v2_9.messages import EhcE20
        assert EhcE20._structure_id == "EHC_E20"

    def test_import_ehc_e21(self):
        from zato.hl7v2.v2_9.messages import EhcE21
        assert EhcE21._structure_id == "EHC_E21"

    def test_import_ehc_e24(self):
        from zato.hl7v2.v2_9.messages import EhcE24
        assert EhcE24._structure_id == "EHC_E24"

    def test_import_esr_u02(self):
        from zato.hl7v2.v2_9.messages import EsrU02
        assert EsrU02._structure_id == "ESR_U02"

    def test_import_esu_u01(self):
        from zato.hl7v2.v2_9.messages import EsuU01
        assert EsuU01._structure_id == "ESU_U01"

    def test_import_inr_u06(self):
        from zato.hl7v2.v2_9.messages import InrU06
        assert InrU06._structure_id == "INR_U06"

    def test_import_inr_u14(self):
        from zato.hl7v2.v2_9.messages import InrU14
        assert InrU14._structure_id == "INR_U14"

    def test_import_inu_u05(self):
        from zato.hl7v2.v2_9.messages import InuU05
        assert InuU05._structure_id == "INU_U05"

    def test_import_lsu_u12(self):
        from zato.hl7v2.v2_9.messages import LsuU12
        assert LsuU12._structure_id == "LSU_U12"

    def test_import_mdm_t01(self):
        from zato.hl7v2.v2_9.messages import MdmT01
        assert MdmT01._structure_id == "MDM_T01"

    def test_import_mdm_t02(self):
        from zato.hl7v2.v2_9.messages import MdmT02
        assert MdmT02._structure_id == "MDM_T02"

    def test_import_mfk_m01(self):
        from zato.hl7v2.v2_9.messages import MfkM01
        assert MfkM01._structure_id == "MFK_M01"

    def test_import_mfn_m02(self):
        from zato.hl7v2.v2_9.messages import MfnM02
        assert MfnM02._structure_id == "MFN_M02"

    def test_import_mfn_m04(self):
        from zato.hl7v2.v2_9.messages import MfnM04
        assert MfnM04._structure_id == "MFN_M04"

    def test_import_mfn_m05(self):
        from zato.hl7v2.v2_9.messages import MfnM05
        assert MfnM05._structure_id == "MFN_M05"

    def test_import_mfn_m06(self):
        from zato.hl7v2.v2_9.messages import MfnM06
        assert MfnM06._structure_id == "MFN_M06"

    def test_import_mfn_m07(self):
        from zato.hl7v2.v2_9.messages import MfnM07
        assert MfnM07._structure_id == "MFN_M07"

    def test_import_mfn_m08(self):
        from zato.hl7v2.v2_9.messages import MfnM08
        assert MfnM08._structure_id == "MFN_M08"

    def test_import_mfn_m09(self):
        from zato.hl7v2.v2_9.messages import MfnM09
        assert MfnM09._structure_id == "MFN_M09"

    def test_import_mfn_m10(self):
        from zato.hl7v2.v2_9.messages import MfnM10
        assert MfnM10._structure_id == "MFN_M10"

    def test_import_mfn_m11(self):
        from zato.hl7v2.v2_9.messages import MfnM11
        assert MfnM11._structure_id == "MFN_M11"

    def test_import_mfn_m12(self):
        from zato.hl7v2.v2_9.messages import MfnM12
        assert MfnM12._structure_id == "MFN_M12"

    def test_import_mfn_m13(self):
        from zato.hl7v2.v2_9.messages import MfnM13
        assert MfnM13._structure_id == "MFN_M13"

    def test_import_mfn_m15(self):
        from zato.hl7v2.v2_9.messages import MfnM15
        assert MfnM15._structure_id == "MFN_M15"

    def test_import_mfn_m16(self):
        from zato.hl7v2.v2_9.messages import MfnM16
        assert MfnM16._structure_id == "MFN_M16"

    def test_import_mfn_m17(self):
        from zato.hl7v2.v2_9.messages import MfnM17
        assert MfnM17._structure_id == "MFN_M17"

    def test_import_mfn_m18(self):
        from zato.hl7v2.v2_9.messages import MfnM18
        assert MfnM18._structure_id == "MFN_M18"

    def test_import_mfn_m19(self):
        from zato.hl7v2.v2_9.messages import MfnM19
        assert MfnM19._structure_id == "MFN_M19"

    def test_import_mfn_znn(self):
        from zato.hl7v2.v2_9.messages import MfnZnn
        assert MfnZnn._structure_id == "MFN_Znn"

    def test_import_nmd_n02(self):
        from zato.hl7v2.v2_9.messages import NmdN02
        assert NmdN02._structure_id == "NMD_N02"

    def test_import_omb_o27(self):
        from zato.hl7v2.v2_9.messages import OmbO27
        assert OmbO27._structure_id == "OMB_O27"

    def test_import_omd_o03(self):
        from zato.hl7v2.v2_9.messages import OmdO03
        assert OmdO03._structure_id == "OMD_O03"

    def test_import_omg_o19(self):
        from zato.hl7v2.v2_9.messages import OmgO19
        assert OmgO19._structure_id == "OMG_O19"

    def test_import_omi_o23(self):
        from zato.hl7v2.v2_9.messages import OmiO23
        assert OmiO23._structure_id == "OMI_O23"

    def test_import_oml_o21(self):
        from zato.hl7v2.v2_9.messages import OmlO21
        assert OmlO21._structure_id == "OML_O21"

    def test_import_oml_o33(self):
        from zato.hl7v2.v2_9.messages import OmlO33
        assert OmlO33._structure_id == "OML_O33"

    def test_import_oml_o35(self):
        from zato.hl7v2.v2_9.messages import OmlO35
        assert OmlO35._structure_id == "OML_O35"

    def test_import_oml_o39(self):
        from zato.hl7v2.v2_9.messages import OmlO39
        assert OmlO39._structure_id == "OML_O39"

    def test_import_oml_o59(self):
        from zato.hl7v2.v2_9.messages import OmlO59
        assert OmlO59._structure_id == "OML_O59"

    def test_import_omn_o07(self):
        from zato.hl7v2.v2_9.messages import OmnO07
        assert OmnO07._structure_id == "OMN_O07"

    def test_import_omp_o09(self):
        from zato.hl7v2.v2_9.messages import OmpO09
        assert OmpO09._structure_id == "OMP_O09"

    def test_import_omq_o57(self):
        from zato.hl7v2.v2_9.messages import OmqO57
        assert OmqO57._structure_id == "OMQ_O57"

    def test_import_oms_o05(self):
        from zato.hl7v2.v2_9.messages import OmsO05
        assert OmsO05._structure_id == "OMS_O05"

    def test_import_opl_o37(self):
        from zato.hl7v2.v2_9.messages import OplO37
        assert OplO37._structure_id == "OPL_O37"

    def test_import_opr_o38(self):
        from zato.hl7v2.v2_9.messages import OprO38
        assert OprO38._structure_id == "OPR_O38"

    def test_import_opu_r25(self):
        from zato.hl7v2.v2_9.messages import OpuR25
        assert OpuR25._structure_id == "OPU_R25"

    def test_import_ora_r33(self):
        from zato.hl7v2.v2_9.messages import OraR33
        assert OraR33._structure_id == "ORA_R33"

    def test_import_ora_r41(self):
        from zato.hl7v2.v2_9.messages import OraR41
        assert OraR41._structure_id == "ORA_R41"

    def test_import_orb_o28(self):
        from zato.hl7v2.v2_9.messages import OrbO28
        assert OrbO28._structure_id == "ORB_O28"

    def test_import_ord_o04(self):
        from zato.hl7v2.v2_9.messages import OrdO04
        assert OrdO04._structure_id == "ORD_O04"

    def test_import_org_o20(self):
        from zato.hl7v2.v2_9.messages import OrgO20
        assert OrgO20._structure_id == "ORG_O20"

    def test_import_ori_o24(self):
        from zato.hl7v2.v2_9.messages import OriO24
        assert OriO24._structure_id == "ORI_O24"

    def test_import_orl_o22(self):
        from zato.hl7v2.v2_9.messages import OrlO22
        assert OrlO22._structure_id == "ORL_O22"

    def test_import_orl_o34(self):
        from zato.hl7v2.v2_9.messages import OrlO34
        assert OrlO34._structure_id == "ORL_O34"

    def test_import_orl_o36(self):
        from zato.hl7v2.v2_9.messages import OrlO36
        assert OrlO36._structure_id == "ORL_O36"

    def test_import_orl_o40(self):
        from zato.hl7v2.v2_9.messages import OrlO40
        assert OrlO40._structure_id == "ORL_O40"

    def test_import_orl_o53(self):
        from zato.hl7v2.v2_9.messages import OrlO53
        assert OrlO53._structure_id == "ORL_O53"

    def test_import_orl_o54(self):
        from zato.hl7v2.v2_9.messages import OrlO54
        assert OrlO54._structure_id == "ORL_O54"

    def test_import_orl_o55(self):
        from zato.hl7v2.v2_9.messages import OrlO55
        assert OrlO55._structure_id == "ORL_O55"

    def test_import_orl_o56(self):
        from zato.hl7v2.v2_9.messages import OrlO56
        assert OrlO56._structure_id == "ORL_O56"

    def test_import_orm_o01(self):
        from zato.hl7v2.v2_9.messages import OrmO01
        assert OrmO01._structure_id == "ORM_O01"

    def test_import_orn_o08(self):
        from zato.hl7v2.v2_9.messages import OrnO08
        assert OrnO08._structure_id == "ORN_O08"

    def test_import_orp_o10(self):
        from zato.hl7v2.v2_9.messages import OrpO10
        assert OrpO10._structure_id == "ORP_O10"

    def test_import_ors_o06(self):
        from zato.hl7v2.v2_9.messages import OrsO06
        assert OrsO06._structure_id == "ORS_O06"

    def test_import_oru_r01(self):
        from zato.hl7v2.v2_9.messages import OruR01
        assert OruR01._structure_id == "ORU_R01"

    def test_import_oru_r30(self):
        from zato.hl7v2.v2_9.messages import OruR30
        assert OruR30._structure_id == "ORU_R30"

    def test_import_orx_o58(self):
        from zato.hl7v2.v2_9.messages import OrxO58
        assert OrxO58._structure_id == "ORX_O58"

    def test_import_osm_r26(self):
        from zato.hl7v2.v2_9.messages import OsmR26
        assert OsmR26._structure_id == "OSM_R26"

    def test_import_osu_o51(self):
        from zato.hl7v2.v2_9.messages import OsuO51
        assert OsuO51._structure_id == "OSU_O51"

    def test_import_osu_o52(self):
        from zato.hl7v2.v2_9.messages import OsuO52
        assert OsuO52._structure_id == "OSU_O52"

    def test_import_oul_r22(self):
        from zato.hl7v2.v2_9.messages import OulR22
        assert OulR22._structure_id == "OUL_R22"

    def test_import_oul_r23(self):
        from zato.hl7v2.v2_9.messages import OulR23
        assert OulR23._structure_id == "OUL_R23"

    def test_import_oul_r24(self):
        from zato.hl7v2.v2_9.messages import OulR24
        assert OulR24._structure_id == "OUL_R24"

    def test_import_pex_p07(self):
        from zato.hl7v2.v2_9.messages import PexP07
        assert PexP07._structure_id == "PEX_P07"

    def test_import_pgl_pc6(self):
        from zato.hl7v2.v2_9.messages import PglPc6
        assert PglPc6._structure_id == "PGL_PC6"

    def test_import_pmu_b01(self):
        from zato.hl7v2.v2_9.messages import PmuB01
        assert PmuB01._structure_id == "PMU_B01"

    def test_import_pmu_b03(self):
        from zato.hl7v2.v2_9.messages import PmuB03
        assert PmuB03._structure_id == "PMU_B03"

    def test_import_pmu_b04(self):
        from zato.hl7v2.v2_9.messages import PmuB04
        assert PmuB04._structure_id == "PMU_B04"

    def test_import_pmu_b07(self):
        from zato.hl7v2.v2_9.messages import PmuB07
        assert PmuB07._structure_id == "PMU_B07"

    def test_import_pmu_b08(self):
        from zato.hl7v2.v2_9.messages import PmuB08
        assert PmuB08._structure_id == "PMU_B08"

    def test_import_ppg_pcg(self):
        from zato.hl7v2.v2_9.messages import PpgPcg
        assert PpgPcg._structure_id == "PPG_PCG"

    def test_import_ppp_pcb(self):
        from zato.hl7v2.v2_9.messages import PppPcb
        assert PppPcb._structure_id == "PPP_PCB"

    def test_import_ppr_pc1(self):
        from zato.hl7v2.v2_9.messages import PprPc1
        assert PprPc1._structure_id == "PPR_PC1"

    def test_import_qbp_e03(self):
        from zato.hl7v2.v2_9.messages import QbpE03
        assert QbpE03._structure_id == "QBP_E03"

    def test_import_qbp_e22(self):
        from zato.hl7v2.v2_9.messages import QbpE22
        assert QbpE22._structure_id == "QBP_E22"

    def test_import_qbp_o33(self):
        from zato.hl7v2.v2_9.messages import QbpO33
        assert QbpO33._structure_id == "QBP_O33"

    def test_import_qbp_o34(self):
        from zato.hl7v2.v2_9.messages import QbpO34
        assert QbpO34._structure_id == "QBP_O34"

    def test_import_qbp_q11(self):
        from zato.hl7v2.v2_9.messages import QbpQ11
        assert QbpQ11._structure_id == "QBP_Q11"

    def test_import_qbp_q13(self):
        from zato.hl7v2.v2_9.messages import QbpQ13
        assert QbpQ13._structure_id == "QBP_Q13"

    def test_import_qbp_q15(self):
        from zato.hl7v2.v2_9.messages import QbpQ15
        assert QbpQ15._structure_id == "QBP_Q15"

    def test_import_qbp_q21(self):
        from zato.hl7v2.v2_9.messages import QbpQ21
        assert QbpQ21._structure_id == "QBP_Q21"

    def test_import_qbp_qnn(self):
        from zato.hl7v2.v2_9.messages import QbpQnn
        assert QbpQnn._structure_id == "QBP_Qnn"

    def test_import_qbp_z73(self):
        from zato.hl7v2.v2_9.messages import QbpZ73
        assert QbpZ73._structure_id == "QBP_Z73"

    def test_import_qcn_j01(self):
        from zato.hl7v2.v2_9.messages import QcnJ01
        assert QcnJ01._structure_id == "QCN_J01"

    def test_import_qsb_q16(self):
        from zato.hl7v2.v2_9.messages import QsbQ16
        assert QsbQ16._structure_id == "QSB_Q16"

    def test_import_qvr_q17(self):
        from zato.hl7v2.v2_9.messages import QvrQ17
        assert QvrQ17._structure_id == "QVR_Q17"

    def test_import_ras_o17(self):
        from zato.hl7v2.v2_9.messages import RasO17
        assert RasO17._structure_id == "RAS_O17"

    def test_import_rcv_o59(self):
        from zato.hl7v2.v2_9.messages import RcvO59
        assert RcvO59._structure_id == "RCV_O59"

    def test_import_rde_o11(self):
        from zato.hl7v2.v2_9.messages import RdeO11
        assert RdeO11._structure_id == "RDE_O11"

    def test_import_rde_o49(self):
        from zato.hl7v2.v2_9.messages import RdeO49
        assert RdeO49._structure_id == "RDE_O49"

    def test_import_rdr_rdr(self):
        from zato.hl7v2.v2_9.messages import RdrRdr
        assert RdrRdr._structure_id == "RDR_RDR"

    def test_import_rds_o13(self):
        from zato.hl7v2.v2_9.messages import RdsO13
        assert RdsO13._structure_id == "RDS_O13"

    def test_import_rdy_k15(self):
        from zato.hl7v2.v2_9.messages import RdyK15
        assert RdyK15._structure_id == "RDY_K15"

    def test_import_rdy_z80(self):
        from zato.hl7v2.v2_9.messages import RdyZ80
        assert RdyZ80._structure_id == "RDY_Z80"

    def test_import_ref_i12(self):
        from zato.hl7v2.v2_9.messages import RefI12
        assert RefI12._structure_id == "REF_I12"

    def test_import_rgv_o15(self):
        from zato.hl7v2.v2_9.messages import RgvO15
        assert RgvO15._structure_id == "RGV_O15"

    def test_import_rpa_i08(self):
        from zato.hl7v2.v2_9.messages import RpaI08
        assert RpaI08._structure_id == "RPA_I08"

    def test_import_rpi_i01(self):
        from zato.hl7v2.v2_9.messages import RpiI01
        assert RpiI01._structure_id == "RPI_I01"

    def test_import_rpi_i04(self):
        from zato.hl7v2.v2_9.messages import RpiI04
        assert RpiI04._structure_id == "RPI_I04"

    def test_import_rpl_i02(self):
        from zato.hl7v2.v2_9.messages import RplI02
        assert RplI02._structure_id == "RPL_I02"

    def test_import_rpr_i03(self):
        from zato.hl7v2.v2_9.messages import RprI03
        assert RprI03._structure_id == "RPR_I03"

    def test_import_rqa_i08(self):
        from zato.hl7v2.v2_9.messages import RqaI08
        assert RqaI08._structure_id == "RQA_I08"

    def test_import_rqi_i01(self):
        from zato.hl7v2.v2_9.messages import RqiI01
        assert RqiI01._structure_id == "RQI_I01"

    def test_import_rqp_i04(self):
        from zato.hl7v2.v2_9.messages import RqpI04
        assert RqpI04._structure_id == "RQP_I04"

    def test_import_rra_o18(self):
        from zato.hl7v2.v2_9.messages import RraO18
        assert RraO18._structure_id == "RRA_O18"

    def test_import_rrd_o14(self):
        from zato.hl7v2.v2_9.messages import RrdO14
        assert RrdO14._structure_id == "RRD_O14"

    def test_import_rre_o12(self):
        from zato.hl7v2.v2_9.messages import RreO12
        assert RreO12._structure_id == "RRE_O12"

    def test_import_rre_o50(self):
        from zato.hl7v2.v2_9.messages import RreO50
        assert RreO50._structure_id == "RRE_O50"

    def test_import_rrg_o16(self):
        from zato.hl7v2.v2_9.messages import RrgO16
        assert RrgO16._structure_id == "RRG_O16"

    def test_import_rri_i12(self):
        from zato.hl7v2.v2_9.messages import RriI12
        assert RriI12._structure_id == "RRI_I12"

    def test_import_rsp_e03(self):
        from zato.hl7v2.v2_9.messages import RspE03
        assert RspE03._structure_id == "RSP_E03"

    def test_import_rsp_e22(self):
        from zato.hl7v2.v2_9.messages import RspE22
        assert RspE22._structure_id == "RSP_E22"

    def test_import_rsp_k11(self):
        from zato.hl7v2.v2_9.messages import RspK11
        assert RspK11._structure_id == "RSP_K11"

    def test_import_rsp_k21(self):
        from zato.hl7v2.v2_9.messages import RspK21
        assert RspK21._structure_id == "RSP_K21"

    def test_import_rsp_k22(self):
        from zato.hl7v2.v2_9.messages import RspK22
        assert RspK22._structure_id == "RSP_K22"

    def test_import_rsp_k23(self):
        from zato.hl7v2.v2_9.messages import RspK23
        assert RspK23._structure_id == "RSP_K23"

    def test_import_rsp_k25(self):
        from zato.hl7v2.v2_9.messages import RspK25
        assert RspK25._structure_id == "RSP_K25"

    def test_import_rsp_k31(self):
        from zato.hl7v2.v2_9.messages import RspK31
        assert RspK31._structure_id == "RSP_K31"

    def test_import_rsp_k32(self):
        from zato.hl7v2.v2_9.messages import RspK32
        assert RspK32._structure_id == "RSP_K32"

    def test_import_rsp_o33(self):
        from zato.hl7v2.v2_9.messages import RspO33
        assert RspO33._structure_id == "RSP_O33"

    def test_import_rsp_o34(self):
        from zato.hl7v2.v2_9.messages import RspO34
        assert RspO34._structure_id == "RSP_O34"

    def test_import_rsp_z82(self):
        from zato.hl7v2.v2_9.messages import RspZ82
        assert RspZ82._structure_id == "RSP_Z82"

    def test_import_rsp_z84(self):
        from zato.hl7v2.v2_9.messages import RspZ84
        assert RspZ84._structure_id == "RSP_Z84"

    def test_import_rsp_z86(self):
        from zato.hl7v2.v2_9.messages import RspZ86
        assert RspZ86._structure_id == "RSP_Z86"

    def test_import_rsp_z88(self):
        from zato.hl7v2.v2_9.messages import RspZ88
        assert RspZ88._structure_id == "RSP_Z88"

    def test_import_rsp_z90(self):
        from zato.hl7v2.v2_9.messages import RspZ90
        assert RspZ90._structure_id == "RSP_Z90"

    def test_import_rsp_znn(self):
        from zato.hl7v2.v2_9.messages import RspZnn
        assert RspZnn._structure_id == "RSP_Znn"

    def test_import_rtb_k13(self):
        from zato.hl7v2.v2_9.messages import RtbK13
        assert RtbK13._structure_id == "RTB_K13"

    def test_import_rtb_knn(self):
        from zato.hl7v2.v2_9.messages import RtbKnn
        assert RtbKnn._structure_id == "RTB_Knn"

    def test_import_rtb_z74(self):
        from zato.hl7v2.v2_9.messages import RtbZ74
        assert RtbZ74._structure_id == "RTB_Z74"

    def test_import_sdr_s31(self):
        from zato.hl7v2.v2_9.messages import SdrS31
        assert SdrS31._structure_id == "SDR_S31"

    def test_import_sdr_s32(self):
        from zato.hl7v2.v2_9.messages import SdrS32
        assert SdrS32._structure_id == "SDR_S32"

    def test_import_siu_s12(self):
        from zato.hl7v2.v2_9.messages import SiuS12
        assert SiuS12._structure_id == "SIU_S12"

    def test_import_slr_s28(self):
        from zato.hl7v2.v2_9.messages import SlrS28
        assert SlrS28._structure_id == "SLR_S28"

    def test_import_srm_s01(self):
        from zato.hl7v2.v2_9.messages import SrmS01
        assert SrmS01._structure_id == "SRM_S01"

    def test_import_srr_s01(self):
        from zato.hl7v2.v2_9.messages import SrrS01
        assert SrrS01._structure_id == "SRR_S01"

    def test_import_ssr_u04(self):
        from zato.hl7v2.v2_9.messages import SsrU04
        assert SsrU04._structure_id == "SSR_U04"

    def test_import_ssu_u03(self):
        from zato.hl7v2.v2_9.messages import SsuU03
        assert SsuU03._structure_id == "SSU_U03"

    def test_import_stc_s33(self):
        from zato.hl7v2.v2_9.messages import StcS33
        assert StcS33._structure_id == "STC_S33"

    def test_import_tcu_u10(self):
        from zato.hl7v2.v2_9.messages import TcuU10
        assert TcuU10._structure_id == "TCU_U10"

    def test_import_udm_q05(self):
        from zato.hl7v2.v2_9.messages import UdmQ05
        assert UdmQ05._structure_id == "UDM_Q05"

    def test_import_vxu_v04(self):
        from zato.hl7v2.v2_9.messages import VxuV04
        assert VxuV04._structure_id == "VXU_V04"
