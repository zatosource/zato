from __future__ import annotations

import pytest

from zato.hl7v2.v2_9.messages import (
    Ack,
    AdtA01,
    AdtA02,
    AdtA03,
    AdtA05,
    AdtA06,
    AdtA09,
    AdtA12,
    AdtA15,
    AdtA16,
    AdtA17,
    AdtA20,
    AdtA21,
    AdtA24,
    AdtA37,
    AdtA38,
    AdtA39,
    AdtA43,
    AdtA44,
    AdtA45,
    AdtA50,
    AdtA52,
    AdtA54,
    AdtA60,
    AdtA61,
    BarP01,
    BarP02,
    BarP05,
    BarP06,
    BarP10,
    BarP12,
    BpsO29,
    BrpO30,
    BrtO32,
    BtsO31,
    CcfI22,
    CciI22,
    CcmI21,
    CcqI19,
    CcrI16,
    CcuI20,
    CquI19,
    CrmC01,
    CsuC09,
    DbcO41,
    DbcO42,
    DelO46,
    DeoO45,
    DerO44,
    DftP03,
    DftP11,
    DprO48,
    DrcO47,
    DrgO43,
    EacU07,
    EanU09,
    EarU08,
    EhcE01,
    EhcE02,
    EhcE04,
    EhcE10,
    EhcE12,
    EhcE13,
    EhcE15,
    EhcE20,
    EhcE21,
    EhcE24,
    EsrU02,
    EsuU01,
    InrU06,
    InrU14,
    InuU05,
    LsuU12,
    MdmT01,
    MdmT02,
    MfkM01,
    MfnM02,
    MfnM04,
    MfnM05,
    MfnM06,
    MfnM07,
    MfnM08,
    MfnM09,
    MfnM10,
    MfnM11,
    MfnM12,
    MfnM13,
    MfnM15,
    MfnM16,
    MfnM17,
    MfnM18,
    MfnM19,
    MfnZnn,
    NmdN02,
    OmbO27,
    OmdO03,
    OmgO19,
    OmiO23,
    OmlO21,
    OmlO33,
    OmlO35,
    OmlO39,
    OmlO59,
    OmnO07,
    OmpO09,
    OmqO57,
    OmsO05,
    OplO37,
    OprO38,
    OpuR25,
    OraR33,
    OraR41,
    OrbO28,
    OrdO04,
    OrgO20,
    OriO24,
    OrlO22,
    OrlO34,
    OrlO36,
    OrlO40,
    OrlO53,
    OrlO54,
    OrlO55,
    OrlO56,
    OrmO01,
    OrnO08,
    OrpO10,
    OrsO06,
    OruR01,
    OruR30,
    OrxO58,
    OsmR26,
    OsuO51,
    OsuO52,
    OulR22,
    OulR23,
    OulR24,
    PexP07,
    PglPc6,
    PmuB01,
    PmuB03,
    PmuB04,
    PmuB07,
    PmuB08,
    PpgPcg,
    PppPcb,
    PprPc1,
    QbpE03,
    QbpE22,
    QbpO33,
    QbpO34,
    QbpQ11,
    QbpQ13,
    QbpQ15,
    QbpQ21,
    QbpQnn,
    QbpZ73,
    QcnJ01,
    QsbQ16,
    QvrQ17,
    RasO17,
    RcvO59,
    RdeO11,
    RdeO49,
    RdrRdr,
    RdsO13,
    RdyK15,
    RdyZ80,
    RefI12,
    RgvO15,
    RpaI08,
    RpiI01,
    RpiI04,
    RplI02,
    RprI03,
    RqaI08,
    RqiI01,
    RqpI04,
    RraO18,
    RrdO14,
    RreO12,
    RreO50,
    RrgO16,
    RriI12,
    RspE03,
    RspE22,
    RspK11,
    RspK21,
    RspK22,
    RspK23,
    RspK25,
    RspK31,
    RspK32,
    RspO33,
    RspO34,
    RspZ82,
    RspZ84,
    RspZ86,
    RspZ88,
    RspZ90,
    RspZnn,
    RtbK13,
    RtbKnn,
    RtbZ74,
    SdrS31,
    SdrS32,
    SiuS12,
    SlrS28,
    SrmS01,
    SrrS01,
    SsrU04,
    SsuU03,
    StcS33,
    TcuU10,
    UdmQ05,
    VxuV04,
)


class TestMessageInstantiation:
    """Test that all message classes can be instantiated."""

    def test_instantiate_ack(self):
        msg = Ack()
        assert msg._structure_id == "ACK"

    def test_instantiate_adt_a01(self):
        msg = AdtA01()
        assert msg._structure_id == "ADT_A01"

    def test_instantiate_adt_a02(self):
        msg = AdtA02()
        assert msg._structure_id == "ADT_A02"

    def test_instantiate_adt_a03(self):
        msg = AdtA03()
        assert msg._structure_id == "ADT_A03"

    def test_instantiate_adt_a05(self):
        msg = AdtA05()
        assert msg._structure_id == "ADT_A05"

    def test_instantiate_adt_a06(self):
        msg = AdtA06()
        assert msg._structure_id == "ADT_A06"

    def test_instantiate_adt_a09(self):
        msg = AdtA09()
        assert msg._structure_id == "ADT_A09"

    def test_instantiate_adt_a12(self):
        msg = AdtA12()
        assert msg._structure_id == "ADT_A12"

    def test_instantiate_adt_a15(self):
        msg = AdtA15()
        assert msg._structure_id == "ADT_A15"

    def test_instantiate_adt_a16(self):
        msg = AdtA16()
        assert msg._structure_id == "ADT_A16"

    def test_instantiate_adt_a17(self):
        msg = AdtA17()
        assert msg._structure_id == "ADT_A17"

    def test_instantiate_adt_a20(self):
        msg = AdtA20()
        assert msg._structure_id == "ADT_A20"

    def test_instantiate_adt_a21(self):
        msg = AdtA21()
        assert msg._structure_id == "ADT_A21"

    def test_instantiate_adt_a24(self):
        msg = AdtA24()
        assert msg._structure_id == "ADT_A24"

    def test_instantiate_adt_a37(self):
        msg = AdtA37()
        assert msg._structure_id == "ADT_A37"

    def test_instantiate_adt_a38(self):
        msg = AdtA38()
        assert msg._structure_id == "ADT_A38"

    def test_instantiate_adt_a39(self):
        msg = AdtA39()
        assert msg._structure_id == "ADT_A39"

    def test_instantiate_adt_a43(self):
        msg = AdtA43()
        assert msg._structure_id == "ADT_A43"

    def test_instantiate_adt_a44(self):
        msg = AdtA44()
        assert msg._structure_id == "ADT_A44"

    def test_instantiate_adt_a45(self):
        msg = AdtA45()
        assert msg._structure_id == "ADT_A45"

    def test_instantiate_adt_a50(self):
        msg = AdtA50()
        assert msg._structure_id == "ADT_A50"

    def test_instantiate_adt_a52(self):
        msg = AdtA52()
        assert msg._structure_id == "ADT_A52"

    def test_instantiate_adt_a54(self):
        msg = AdtA54()
        assert msg._structure_id == "ADT_A54"

    def test_instantiate_adt_a60(self):
        msg = AdtA60()
        assert msg._structure_id == "ADT_A60"

    def test_instantiate_adt_a61(self):
        msg = AdtA61()
        assert msg._structure_id == "ADT_A61"

    def test_instantiate_bar_p01(self):
        msg = BarP01()
        assert msg._structure_id == "BAR_P01"

    def test_instantiate_bar_p02(self):
        msg = BarP02()
        assert msg._structure_id == "BAR_P02"

    def test_instantiate_bar_p05(self):
        msg = BarP05()
        assert msg._structure_id == "BAR_P05"

    def test_instantiate_bar_p06(self):
        msg = BarP06()
        assert msg._structure_id == "BAR_P06"

    def test_instantiate_bar_p10(self):
        msg = BarP10()
        assert msg._structure_id == "BAR_P10"

    def test_instantiate_bar_p12(self):
        msg = BarP12()
        assert msg._structure_id == "BAR_P12"

    def test_instantiate_bps_o29(self):
        msg = BpsO29()
        assert msg._structure_id == "BPS_O29"

    def test_instantiate_brp_o30(self):
        msg = BrpO30()
        assert msg._structure_id == "BRP_O30"

    def test_instantiate_brt_o32(self):
        msg = BrtO32()
        assert msg._structure_id == "BRT_O32"

    def test_instantiate_bts_o31(self):
        msg = BtsO31()
        assert msg._structure_id == "BTS_O31"

    def test_instantiate_ccf_i22(self):
        msg = CcfI22()
        assert msg._structure_id == "CCF_I22"

    def test_instantiate_cci_i22(self):
        msg = CciI22()
        assert msg._structure_id == "CCI_I22"

    def test_instantiate_ccm_i21(self):
        msg = CcmI21()
        assert msg._structure_id == "CCM_I21"

    def test_instantiate_ccq_i19(self):
        msg = CcqI19()
        assert msg._structure_id == "CCQ_I19"

    def test_instantiate_ccr_i16(self):
        msg = CcrI16()
        assert msg._structure_id == "CCR_I16"

    def test_instantiate_ccu_i20(self):
        msg = CcuI20()
        assert msg._structure_id == "CCU_I20"

    def test_instantiate_cqu_i19(self):
        msg = CquI19()
        assert msg._structure_id == "CQU_I19"

    def test_instantiate_crm_c01(self):
        msg = CrmC01()
        assert msg._structure_id == "CRM_C01"

    def test_instantiate_csu_c09(self):
        msg = CsuC09()
        assert msg._structure_id == "CSU_C09"

    def test_instantiate_dbc_o41(self):
        msg = DbcO41()
        assert msg._structure_id == "DBC_O41"

    def test_instantiate_dbc_o42(self):
        msg = DbcO42()
        assert msg._structure_id == "DBC_O42"

    def test_instantiate_del_o46(self):
        msg = DelO46()
        assert msg._structure_id == "DEL_O46"

    def test_instantiate_deo_o45(self):
        msg = DeoO45()
        assert msg._structure_id == "DEO_O45"

    def test_instantiate_der_o44(self):
        msg = DerO44()
        assert msg._structure_id == "DER_O44"

    def test_instantiate_dft_p03(self):
        msg = DftP03()
        assert msg._structure_id == "DFT_P03"

    def test_instantiate_dft_p11(self):
        msg = DftP11()
        assert msg._structure_id == "DFT_P11"

    def test_instantiate_dpr_o48(self):
        msg = DprO48()
        assert msg._structure_id == "DPR_O48"

    def test_instantiate_drc_o47(self):
        msg = DrcO47()
        assert msg._structure_id == "DRC_O47"

    def test_instantiate_drg_o43(self):
        msg = DrgO43()
        assert msg._structure_id == "DRG_O43"

    def test_instantiate_eac_u07(self):
        msg = EacU07()
        assert msg._structure_id == "EAC_U07"

    def test_instantiate_ean_u09(self):
        msg = EanU09()
        assert msg._structure_id == "EAN_U09"

    def test_instantiate_ear_u08(self):
        msg = EarU08()
        assert msg._structure_id == "EAR_U08"

    def test_instantiate_ehc_e01(self):
        msg = EhcE01()
        assert msg._structure_id == "EHC_E01"

    def test_instantiate_ehc_e02(self):
        msg = EhcE02()
        assert msg._structure_id == "EHC_E02"

    def test_instantiate_ehc_e04(self):
        msg = EhcE04()
        assert msg._structure_id == "EHC_E04"

    def test_instantiate_ehc_e10(self):
        msg = EhcE10()
        assert msg._structure_id == "EHC_E10"

    def test_instantiate_ehc_e12(self):
        msg = EhcE12()
        assert msg._structure_id == "EHC_E12"

    def test_instantiate_ehc_e13(self):
        msg = EhcE13()
        assert msg._structure_id == "EHC_E13"

    def test_instantiate_ehc_e15(self):
        msg = EhcE15()
        assert msg._structure_id == "EHC_E15"

    def test_instantiate_ehc_e20(self):
        msg = EhcE20()
        assert msg._structure_id == "EHC_E20"

    def test_instantiate_ehc_e21(self):
        msg = EhcE21()
        assert msg._structure_id == "EHC_E21"

    def test_instantiate_ehc_e24(self):
        msg = EhcE24()
        assert msg._structure_id == "EHC_E24"

    def test_instantiate_esr_u02(self):
        msg = EsrU02()
        assert msg._structure_id == "ESR_U02"

    def test_instantiate_esu_u01(self):
        msg = EsuU01()
        assert msg._structure_id == "ESU_U01"

    def test_instantiate_inr_u06(self):
        msg = InrU06()
        assert msg._structure_id == "INR_U06"

    def test_instantiate_inr_u14(self):
        msg = InrU14()
        assert msg._structure_id == "INR_U14"

    def test_instantiate_inu_u05(self):
        msg = InuU05()
        assert msg._structure_id == "INU_U05"

    def test_instantiate_lsu_u12(self):
        msg = LsuU12()
        assert msg._structure_id == "LSU_U12"

    def test_instantiate_mdm_t01(self):
        msg = MdmT01()
        assert msg._structure_id == "MDM_T01"

    def test_instantiate_mdm_t02(self):
        msg = MdmT02()
        assert msg._structure_id == "MDM_T02"

    def test_instantiate_mfk_m01(self):
        msg = MfkM01()
        assert msg._structure_id == "MFK_M01"

    def test_instantiate_mfn_m02(self):
        msg = MfnM02()
        assert msg._structure_id == "MFN_M02"

    def test_instantiate_mfn_m04(self):
        msg = MfnM04()
        assert msg._structure_id == "MFN_M04"

    def test_instantiate_mfn_m05(self):
        msg = MfnM05()
        assert msg._structure_id == "MFN_M05"

    def test_instantiate_mfn_m06(self):
        msg = MfnM06()
        assert msg._structure_id == "MFN_M06"

    def test_instantiate_mfn_m07(self):
        msg = MfnM07()
        assert msg._structure_id == "MFN_M07"

    def test_instantiate_mfn_m08(self):
        msg = MfnM08()
        assert msg._structure_id == "MFN_M08"

    def test_instantiate_mfn_m09(self):
        msg = MfnM09()
        assert msg._structure_id == "MFN_M09"

    def test_instantiate_mfn_m10(self):
        msg = MfnM10()
        assert msg._structure_id == "MFN_M10"

    def test_instantiate_mfn_m11(self):
        msg = MfnM11()
        assert msg._structure_id == "MFN_M11"

    def test_instantiate_mfn_m12(self):
        msg = MfnM12()
        assert msg._structure_id == "MFN_M12"

    def test_instantiate_mfn_m13(self):
        msg = MfnM13()
        assert msg._structure_id == "MFN_M13"

    def test_instantiate_mfn_m15(self):
        msg = MfnM15()
        assert msg._structure_id == "MFN_M15"

    def test_instantiate_mfn_m16(self):
        msg = MfnM16()
        assert msg._structure_id == "MFN_M16"

    def test_instantiate_mfn_m17(self):
        msg = MfnM17()
        assert msg._structure_id == "MFN_M17"

    def test_instantiate_mfn_m18(self):
        msg = MfnM18()
        assert msg._structure_id == "MFN_M18"

    def test_instantiate_mfn_m19(self):
        msg = MfnM19()
        assert msg._structure_id == "MFN_M19"

    def test_instantiate_mfn_znn(self):
        msg = MfnZnn()
        assert msg._structure_id == "MFN_Znn"

    def test_instantiate_nmd_n02(self):
        msg = NmdN02()
        assert msg._structure_id == "NMD_N02"

    def test_instantiate_omb_o27(self):
        msg = OmbO27()
        assert msg._structure_id == "OMB_O27"

    def test_instantiate_omd_o03(self):
        msg = OmdO03()
        assert msg._structure_id == "OMD_O03"

    def test_instantiate_omg_o19(self):
        msg = OmgO19()
        assert msg._structure_id == "OMG_O19"

    def test_instantiate_omi_o23(self):
        msg = OmiO23()
        assert msg._structure_id == "OMI_O23"

    def test_instantiate_oml_o21(self):
        msg = OmlO21()
        assert msg._structure_id == "OML_O21"

    def test_instantiate_oml_o33(self):
        msg = OmlO33()
        assert msg._structure_id == "OML_O33"

    def test_instantiate_oml_o35(self):
        msg = OmlO35()
        assert msg._structure_id == "OML_O35"

    def test_instantiate_oml_o39(self):
        msg = OmlO39()
        assert msg._structure_id == "OML_O39"

    def test_instantiate_oml_o59(self):
        msg = OmlO59()
        assert msg._structure_id == "OML_O59"

    def test_instantiate_omn_o07(self):
        msg = OmnO07()
        assert msg._structure_id == "OMN_O07"

    def test_instantiate_omp_o09(self):
        msg = OmpO09()
        assert msg._structure_id == "OMP_O09"

    def test_instantiate_omq_o57(self):
        msg = OmqO57()
        assert msg._structure_id == "OMQ_O57"

    def test_instantiate_oms_o05(self):
        msg = OmsO05()
        assert msg._structure_id == "OMS_O05"

    def test_instantiate_opl_o37(self):
        msg = OplO37()
        assert msg._structure_id == "OPL_O37"

    def test_instantiate_opr_o38(self):
        msg = OprO38()
        assert msg._structure_id == "OPR_O38"

    def test_instantiate_opu_r25(self):
        msg = OpuR25()
        assert msg._structure_id == "OPU_R25"

    def test_instantiate_ora_r33(self):
        msg = OraR33()
        assert msg._structure_id == "ORA_R33"

    def test_instantiate_ora_r41(self):
        msg = OraR41()
        assert msg._structure_id == "ORA_R41"

    def test_instantiate_orb_o28(self):
        msg = OrbO28()
        assert msg._structure_id == "ORB_O28"

    def test_instantiate_ord_o04(self):
        msg = OrdO04()
        assert msg._structure_id == "ORD_O04"

    def test_instantiate_org_o20(self):
        msg = OrgO20()
        assert msg._structure_id == "ORG_O20"

    def test_instantiate_ori_o24(self):
        msg = OriO24()
        assert msg._structure_id == "ORI_O24"

    def test_instantiate_orl_o22(self):
        msg = OrlO22()
        assert msg._structure_id == "ORL_O22"

    def test_instantiate_orl_o34(self):
        msg = OrlO34()
        assert msg._structure_id == "ORL_O34"

    def test_instantiate_orl_o36(self):
        msg = OrlO36()
        assert msg._structure_id == "ORL_O36"

    def test_instantiate_orl_o40(self):
        msg = OrlO40()
        assert msg._structure_id == "ORL_O40"

    def test_instantiate_orl_o53(self):
        msg = OrlO53()
        assert msg._structure_id == "ORL_O53"

    def test_instantiate_orl_o54(self):
        msg = OrlO54()
        assert msg._structure_id == "ORL_O54"

    def test_instantiate_orl_o55(self):
        msg = OrlO55()
        assert msg._structure_id == "ORL_O55"

    def test_instantiate_orl_o56(self):
        msg = OrlO56()
        assert msg._structure_id == "ORL_O56"

    def test_instantiate_orm_o01(self):
        msg = OrmO01()
        assert msg._structure_id == "ORM_O01"

    def test_instantiate_orn_o08(self):
        msg = OrnO08()
        assert msg._structure_id == "ORN_O08"

    def test_instantiate_orp_o10(self):
        msg = OrpO10()
        assert msg._structure_id == "ORP_O10"

    def test_instantiate_ors_o06(self):
        msg = OrsO06()
        assert msg._structure_id == "ORS_O06"

    def test_instantiate_oru_r01(self):
        msg = OruR01()
        assert msg._structure_id == "ORU_R01"

    def test_instantiate_oru_r30(self):
        msg = OruR30()
        assert msg._structure_id == "ORU_R30"

    def test_instantiate_orx_o58(self):
        msg = OrxO58()
        assert msg._structure_id == "ORX_O58"

    def test_instantiate_osm_r26(self):
        msg = OsmR26()
        assert msg._structure_id == "OSM_R26"

    def test_instantiate_osu_o51(self):
        msg = OsuO51()
        assert msg._structure_id == "OSU_O51"

    def test_instantiate_osu_o52(self):
        msg = OsuO52()
        assert msg._structure_id == "OSU_O52"

    def test_instantiate_oul_r22(self):
        msg = OulR22()
        assert msg._structure_id == "OUL_R22"

    def test_instantiate_oul_r23(self):
        msg = OulR23()
        assert msg._structure_id == "OUL_R23"

    def test_instantiate_oul_r24(self):
        msg = OulR24()
        assert msg._structure_id == "OUL_R24"

    def test_instantiate_pex_p07(self):
        msg = PexP07()
        assert msg._structure_id == "PEX_P07"

    def test_instantiate_pgl_pc6(self):
        msg = PglPc6()
        assert msg._structure_id == "PGL_PC6"

    def test_instantiate_pmu_b01(self):
        msg = PmuB01()
        assert msg._structure_id == "PMU_B01"

    def test_instantiate_pmu_b03(self):
        msg = PmuB03()
        assert msg._structure_id == "PMU_B03"

    def test_instantiate_pmu_b04(self):
        msg = PmuB04()
        assert msg._structure_id == "PMU_B04"

    def test_instantiate_pmu_b07(self):
        msg = PmuB07()
        assert msg._structure_id == "PMU_B07"

    def test_instantiate_pmu_b08(self):
        msg = PmuB08()
        assert msg._structure_id == "PMU_B08"

    def test_instantiate_ppg_pcg(self):
        msg = PpgPcg()
        assert msg._structure_id == "PPG_PCG"

    def test_instantiate_ppp_pcb(self):
        msg = PppPcb()
        assert msg._structure_id == "PPP_PCB"

    def test_instantiate_ppr_pc1(self):
        msg = PprPc1()
        assert msg._structure_id == "PPR_PC1"

    def test_instantiate_qbp_e03(self):
        msg = QbpE03()
        assert msg._structure_id == "QBP_E03"

    def test_instantiate_qbp_e22(self):
        msg = QbpE22()
        assert msg._structure_id == "QBP_E22"

    def test_instantiate_qbp_o33(self):
        msg = QbpO33()
        assert msg._structure_id == "QBP_O33"

    def test_instantiate_qbp_o34(self):
        msg = QbpO34()
        assert msg._structure_id == "QBP_O34"

    def test_instantiate_qbp_q11(self):
        msg = QbpQ11()
        assert msg._structure_id == "QBP_Q11"

    def test_instantiate_qbp_q13(self):
        msg = QbpQ13()
        assert msg._structure_id == "QBP_Q13"

    def test_instantiate_qbp_q15(self):
        msg = QbpQ15()
        assert msg._structure_id == "QBP_Q15"

    def test_instantiate_qbp_q21(self):
        msg = QbpQ21()
        assert msg._structure_id == "QBP_Q21"

    def test_instantiate_qbp_qnn(self):
        msg = QbpQnn()
        assert msg._structure_id == "QBP_Qnn"

    def test_instantiate_qbp_z73(self):
        msg = QbpZ73()
        assert msg._structure_id == "QBP_Z73"

    def test_instantiate_qcn_j01(self):
        msg = QcnJ01()
        assert msg._structure_id == "QCN_J01"

    def test_instantiate_qsb_q16(self):
        msg = QsbQ16()
        assert msg._structure_id == "QSB_Q16"

    def test_instantiate_qvr_q17(self):
        msg = QvrQ17()
        assert msg._structure_id == "QVR_Q17"

    def test_instantiate_ras_o17(self):
        msg = RasO17()
        assert msg._structure_id == "RAS_O17"

    def test_instantiate_rcv_o59(self):
        msg = RcvO59()
        assert msg._structure_id == "RCV_O59"

    def test_instantiate_rde_o11(self):
        msg = RdeO11()
        assert msg._structure_id == "RDE_O11"

    def test_instantiate_rde_o49(self):
        msg = RdeO49()
        assert msg._structure_id == "RDE_O49"

    def test_instantiate_rdr_rdr(self):
        msg = RdrRdr()
        assert msg._structure_id == "RDR_RDR"

    def test_instantiate_rds_o13(self):
        msg = RdsO13()
        assert msg._structure_id == "RDS_O13"

    def test_instantiate_rdy_k15(self):
        msg = RdyK15()
        assert msg._structure_id == "RDY_K15"

    def test_instantiate_rdy_z80(self):
        msg = RdyZ80()
        assert msg._structure_id == "RDY_Z80"

    def test_instantiate_ref_i12(self):
        msg = RefI12()
        assert msg._structure_id == "REF_I12"

    def test_instantiate_rgv_o15(self):
        msg = RgvO15()
        assert msg._structure_id == "RGV_O15"

    def test_instantiate_rpa_i08(self):
        msg = RpaI08()
        assert msg._structure_id == "RPA_I08"

    def test_instantiate_rpi_i01(self):
        msg = RpiI01()
        assert msg._structure_id == "RPI_I01"

    def test_instantiate_rpi_i04(self):
        msg = RpiI04()
        assert msg._structure_id == "RPI_I04"

    def test_instantiate_rpl_i02(self):
        msg = RplI02()
        assert msg._structure_id == "RPL_I02"

    def test_instantiate_rpr_i03(self):
        msg = RprI03()
        assert msg._structure_id == "RPR_I03"

    def test_instantiate_rqa_i08(self):
        msg = RqaI08()
        assert msg._structure_id == "RQA_I08"

    def test_instantiate_rqi_i01(self):
        msg = RqiI01()
        assert msg._structure_id == "RQI_I01"

    def test_instantiate_rqp_i04(self):
        msg = RqpI04()
        assert msg._structure_id == "RQP_I04"

    def test_instantiate_rra_o18(self):
        msg = RraO18()
        assert msg._structure_id == "RRA_O18"

    def test_instantiate_rrd_o14(self):
        msg = RrdO14()
        assert msg._structure_id == "RRD_O14"

    def test_instantiate_rre_o12(self):
        msg = RreO12()
        assert msg._structure_id == "RRE_O12"

    def test_instantiate_rre_o50(self):
        msg = RreO50()
        assert msg._structure_id == "RRE_O50"

    def test_instantiate_rrg_o16(self):
        msg = RrgO16()
        assert msg._structure_id == "RRG_O16"

    def test_instantiate_rri_i12(self):
        msg = RriI12()
        assert msg._structure_id == "RRI_I12"

    def test_instantiate_rsp_e03(self):
        msg = RspE03()
        assert msg._structure_id == "RSP_E03"

    def test_instantiate_rsp_e22(self):
        msg = RspE22()
        assert msg._structure_id == "RSP_E22"

    def test_instantiate_rsp_k11(self):
        msg = RspK11()
        assert msg._structure_id == "RSP_K11"

    def test_instantiate_rsp_k21(self):
        msg = RspK21()
        assert msg._structure_id == "RSP_K21"

    def test_instantiate_rsp_k22(self):
        msg = RspK22()
        assert msg._structure_id == "RSP_K22"

    def test_instantiate_rsp_k23(self):
        msg = RspK23()
        assert msg._structure_id == "RSP_K23"

    def test_instantiate_rsp_k25(self):
        msg = RspK25()
        assert msg._structure_id == "RSP_K25"

    def test_instantiate_rsp_k31(self):
        msg = RspK31()
        assert msg._structure_id == "RSP_K31"

    def test_instantiate_rsp_k32(self):
        msg = RspK32()
        assert msg._structure_id == "RSP_K32"

    def test_instantiate_rsp_o33(self):
        msg = RspO33()
        assert msg._structure_id == "RSP_O33"

    def test_instantiate_rsp_o34(self):
        msg = RspO34()
        assert msg._structure_id == "RSP_O34"

    def test_instantiate_rsp_z82(self):
        msg = RspZ82()
        assert msg._structure_id == "RSP_Z82"

    def test_instantiate_rsp_z84(self):
        msg = RspZ84()
        assert msg._structure_id == "RSP_Z84"

    def test_instantiate_rsp_z86(self):
        msg = RspZ86()
        assert msg._structure_id == "RSP_Z86"

    def test_instantiate_rsp_z88(self):
        msg = RspZ88()
        assert msg._structure_id == "RSP_Z88"

    def test_instantiate_rsp_z90(self):
        msg = RspZ90()
        assert msg._structure_id == "RSP_Z90"

    def test_instantiate_rsp_znn(self):
        msg = RspZnn()
        assert msg._structure_id == "RSP_Znn"

    def test_instantiate_rtb_k13(self):
        msg = RtbK13()
        assert msg._structure_id == "RTB_K13"

    def test_instantiate_rtb_knn(self):
        msg = RtbKnn()
        assert msg._structure_id == "RTB_Knn"

    def test_instantiate_rtb_z74(self):
        msg = RtbZ74()
        assert msg._structure_id == "RTB_Z74"

    def test_instantiate_sdr_s31(self):
        msg = SdrS31()
        assert msg._structure_id == "SDR_S31"

    def test_instantiate_sdr_s32(self):
        msg = SdrS32()
        assert msg._structure_id == "SDR_S32"

    def test_instantiate_siu_s12(self):
        msg = SiuS12()
        assert msg._structure_id == "SIU_S12"

    def test_instantiate_slr_s28(self):
        msg = SlrS28()
        assert msg._structure_id == "SLR_S28"

    def test_instantiate_srm_s01(self):
        msg = SrmS01()
        assert msg._structure_id == "SRM_S01"

    def test_instantiate_srr_s01(self):
        msg = SrrS01()
        assert msg._structure_id == "SRR_S01"

    def test_instantiate_ssr_u04(self):
        msg = SsrU04()
        assert msg._structure_id == "SSR_U04"

    def test_instantiate_ssu_u03(self):
        msg = SsuU03()
        assert msg._structure_id == "SSU_U03"

    def test_instantiate_stc_s33(self):
        msg = StcS33()
        assert msg._structure_id == "STC_S33"

    def test_instantiate_tcu_u10(self):
        msg = TcuU10()
        assert msg._structure_id == "TCU_U10"

    def test_instantiate_udm_q05(self):
        msg = UdmQ05()
        assert msg._structure_id == "UDM_Q05"

    def test_instantiate_vxu_v04(self):
        msg = VxuV04()
        assert msg._structure_id == "VXU_V04"
