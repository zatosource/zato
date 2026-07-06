from __future__ import annotations

from zato.hl7v2.v2_9.messages import (
    ACK,
    ADR_A19,
    ADT_A01,
    ADT_A02,
    ADT_A03,
    ADT_A05,
    ADT_A06,
    ADT_A09,
    ADT_A12,
    ADT_A15,
    ADT_A16,
    ADT_A17,
    ADT_A20,
    ADT_A21,
    ADT_A24,
    ADT_A30,
    ADT_A37,
    ADT_A38,
    ADT_A39,
    ADT_A43,
    ADT_A44,
    ADT_A45,
    ADT_A50,
    ADT_A52,
    ADT_A54,
    ADT_A60,
    ADT_A61,
    BAR_P01,
    BAR_P02,
    BAR_P05,
    BAR_P06,
    BAR_P10,
    BAR_P12,
    BPS_O29,
    BRP_O30,
    BRT_O32,
    BTS_O31,
    CCF_I22,
    CCI_I22,
    CCM_I21,
    CCQ_I19,
    CCR_I16,
    CCU_I20,
    CQU_I19,
    CRM_C01,
    CSU_C09,
    DBC_O41,
    DBC_O42,
    DEL_O46,
    DEO_O45,
    DER_O44,
    DFT_P03,
    DFT_P11,
    DPR_O48,
    DRC_O47,
    DRG_O43,
    EAC_U07,
    EAN_U09,
    EAR_U08,
    EHC_E01,
    EHC_E02,
    EHC_E04,
    EHC_E10,
    EHC_E12,
    EHC_E13,
    EHC_E15,
    EHC_E20,
    EHC_E21,
    EHC_E24,
    ESR_U02,
    ESU_U01,
    INR_U06,
    INR_U14,
    INU_U05,
    LSU_U12,
    MDM_T01,
    MDM_T02,
    MFK_M01,
    MFN_M02,
    MFN_M04,
    MFN_M05,
    MFN_M06,
    MFN_M07,
    MFN_M08,
    MFN_M09,
    MFN_M10,
    MFN_M11,
    MFN_M12,
    MFN_M13,
    MFN_M15,
    MFN_M16,
    MFN_M17,
    MFN_M18,
    MFN_M19,
    MFN_Znn,
    NMD_N02,
    OMB_O27,
    OMD_O03,
    OMG_O19,
    OMI_O23,
    OML_O21,
    OML_O33,
    OML_O35,
    OML_O39,
    OML_O59,
    OMN_O07,
    OMP_O09,
    OMQ_O57,
    OMS_O05,
    OPL_O37,
    OPR_O38,
    OPU_R25,
    ORA_R33,
    ORA_R41,
    ORB_O28,
    ORD_O04,
    ORG_O20,
    ORI_O24,
    ORL_O22,
    ORL_O34,
    ORL_O36,
    ORL_O40,
    ORL_O53,
    ORL_O54,
    ORL_O55,
    ORL_O56,
    ORM_O01,
    ORN_O08,
    ORP_O10,
    ORS_O06,
    ORU_R01,
    ORU_R30,
    ORX_O58,
    OSM_R26,
    OSU_O51,
    OSU_O52,
    OUL_R22,
    OUL_R23,
    OUL_R24,
    PEX_P07,
    PGL_PC6,
    PMU_B01,
    PMU_B03,
    PMU_B04,
    PMU_B07,
    PMU_B08,
    PPG_PCG,
    PPP_PCB,
    PPR_PC1,
    QBP_E03,
    QBP_E22,
    QBP_O33,
    QBP_O34,
    QBP_Q11,
    QBP_Q13,
    QBP_Q15,
    QBP_Q21,
    QBP_Qnn,
    QBP_Z73,
    QCN_J01,
    QRY_A19,
    QSB_Q16,
    QVR_Q17,
    RAS_O17,
    RCV_O59,
    RDE_O11,
    RDE_O49,
    RDR_RDR,
    RDS_O13,
    RDY_K15,
    RDY_Z80,
    REF_I12,
    RGV_O15,
    RPA_I08,
    RPI_I01,
    RPI_I04,
    RPL_I02,
    RPR_I03,
    RQA_I08,
    RQI_I01,
    RQP_I04,
    RRA_O18,
    RRD_O14,
    RRE_O12,
    RRE_O50,
    RRG_O16,
    RRI_I12,
    RSP_E03,
    RSP_E22,
    RSP_K11,
    RSP_K21,
    RSP_K22,
    RSP_K23,
    RSP_K25,
    RSP_K31,
    RSP_K32,
    RSP_O33,
    RSP_O34,
    RSP_Z82,
    RSP_Z84,
    RSP_Z86,
    RSP_Z88,
    RSP_Z90,
    RSP_Znn,
    RTB_K13,
    RTB_Knn,
    RTB_Z74,
    SDR_S31,
    SDR_S32,
    SIU_S12,
    SLR_S28,
    SRM_S01,
    SRR_S01,
    SSR_U04,
    SSU_U03,
    STC_S33,
    TCU_U10,
    UDM_Q05,
    VXU_V04,
)


class TestMessageInstantiation:
    """Test that all message classes can be instantiated."""

    def test_instantiate_ack(self):
        msg = ACK()
        assert msg._structure_id == "ACK"

    def test_instantiate_adr_a19(self):
        msg = ADR_A19()
        assert msg._structure_id == "ADR_A19"

    def test_instantiate_adt_a01(self):
        msg = ADT_A01()
        assert msg._structure_id == "ADT_A01"

    def test_instantiate_adt_a02(self):
        msg = ADT_A02()
        assert msg._structure_id == "ADT_A02"

    def test_instantiate_adt_a03(self):
        msg = ADT_A03()
        assert msg._structure_id == "ADT_A03"

    def test_instantiate_adt_a05(self):
        msg = ADT_A05()
        assert msg._structure_id == "ADT_A05"

    def test_instantiate_adt_a06(self):
        msg = ADT_A06()
        assert msg._structure_id == "ADT_A06"

    def test_instantiate_adt_a09(self):
        msg = ADT_A09()
        assert msg._structure_id == "ADT_A09"

    def test_instantiate_adt_a12(self):
        msg = ADT_A12()
        assert msg._structure_id == "ADT_A12"

    def test_instantiate_adt_a15(self):
        msg = ADT_A15()
        assert msg._structure_id == "ADT_A15"

    def test_instantiate_adt_a16(self):
        msg = ADT_A16()
        assert msg._structure_id == "ADT_A16"

    def test_instantiate_adt_a17(self):
        msg = ADT_A17()
        assert msg._structure_id == "ADT_A17"

    def test_instantiate_adt_a20(self):
        msg = ADT_A20()
        assert msg._structure_id == "ADT_A20"

    def test_instantiate_adt_a21(self):
        msg = ADT_A21()
        assert msg._structure_id == "ADT_A21"

    def test_instantiate_adt_a24(self):
        msg = ADT_A24()
        assert msg._structure_id == "ADT_A24"

    def test_instantiate_adt_a30(self):
        msg = ADT_A30()
        assert msg._structure_id == "ADT_A30"

    def test_instantiate_adt_a37(self):
        msg = ADT_A37()
        assert msg._structure_id == "ADT_A37"

    def test_instantiate_adt_a38(self):
        msg = ADT_A38()
        assert msg._structure_id == "ADT_A38"

    def test_instantiate_adt_a39(self):
        msg = ADT_A39()
        assert msg._structure_id == "ADT_A39"

    def test_instantiate_adt_a43(self):
        msg = ADT_A43()
        assert msg._structure_id == "ADT_A43"

    def test_instantiate_adt_a44(self):
        msg = ADT_A44()
        assert msg._structure_id == "ADT_A44"

    def test_instantiate_adt_a45(self):
        msg = ADT_A45()
        assert msg._structure_id == "ADT_A45"

    def test_instantiate_adt_a50(self):
        msg = ADT_A50()
        assert msg._structure_id == "ADT_A50"

    def test_instantiate_adt_a52(self):
        msg = ADT_A52()
        assert msg._structure_id == "ADT_A52"

    def test_instantiate_adt_a54(self):
        msg = ADT_A54()
        assert msg._structure_id == "ADT_A54"

    def test_instantiate_adt_a60(self):
        msg = ADT_A60()
        assert msg._structure_id == "ADT_A60"

    def test_instantiate_adt_a61(self):
        msg = ADT_A61()
        assert msg._structure_id == "ADT_A61"

    def test_instantiate_bar_p01(self):
        msg = BAR_P01()
        assert msg._structure_id == "BAR_P01"

    def test_instantiate_bar_p02(self):
        msg = BAR_P02()
        assert msg._structure_id == "BAR_P02"

    def test_instantiate_bar_p05(self):
        msg = BAR_P05()
        assert msg._structure_id == "BAR_P05"

    def test_instantiate_bar_p06(self):
        msg = BAR_P06()
        assert msg._structure_id == "BAR_P06"

    def test_instantiate_bar_p10(self):
        msg = BAR_P10()
        assert msg._structure_id == "BAR_P10"

    def test_instantiate_bar_p12(self):
        msg = BAR_P12()
        assert msg._structure_id == "BAR_P12"

    def test_instantiate_bps_o29(self):
        msg = BPS_O29()
        assert msg._structure_id == "BPS_O29"

    def test_instantiate_brp_o30(self):
        msg = BRP_O30()
        assert msg._structure_id == "BRP_O30"

    def test_instantiate_brt_o32(self):
        msg = BRT_O32()
        assert msg._structure_id == "BRT_O32"

    def test_instantiate_bts_o31(self):
        msg = BTS_O31()
        assert msg._structure_id == "BTS_O31"

    def test_instantiate_ccf_i22(self):
        msg = CCF_I22()
        assert msg._structure_id == "CCF_I22"

    def test_instantiate_cci_i22(self):
        msg = CCI_I22()
        assert msg._structure_id == "CCI_I22"

    def test_instantiate_ccm_i21(self):
        msg = CCM_I21()
        assert msg._structure_id == "CCM_I21"

    def test_instantiate_ccq_i19(self):
        msg = CCQ_I19()
        assert msg._structure_id == "CCQ_I19"

    def test_instantiate_ccr_i16(self):
        msg = CCR_I16()
        assert msg._structure_id == "CCR_I16"

    def test_instantiate_ccu_i20(self):
        msg = CCU_I20()
        assert msg._structure_id == "CCU_I20"

    def test_instantiate_cqu_i19(self):
        msg = CQU_I19()
        assert msg._structure_id == "CQU_I19"

    def test_instantiate_crm_c01(self):
        msg = CRM_C01()
        assert msg._structure_id == "CRM_C01"

    def test_instantiate_csu_c09(self):
        msg = CSU_C09()
        assert msg._structure_id == "CSU_C09"

    def test_instantiate_dbc_o41(self):
        msg = DBC_O41()
        assert msg._structure_id == "DBC_O41"

    def test_instantiate_dbc_o42(self):
        msg = DBC_O42()
        assert msg._structure_id == "DBC_O42"

    def test_instantiate_del_o46(self):
        msg = DEL_O46()
        assert msg._structure_id == "DEL_O46"

    def test_instantiate_deo_o45(self):
        msg = DEO_O45()
        assert msg._structure_id == "DEO_O45"

    def test_instantiate_der_o44(self):
        msg = DER_O44()
        assert msg._structure_id == "DER_O44"

    def test_instantiate_dft_p03(self):
        msg = DFT_P03()
        assert msg._structure_id == "DFT_P03"

    def test_instantiate_dft_p11(self):
        msg = DFT_P11()
        assert msg._structure_id == "DFT_P11"

    def test_instantiate_dpr_o48(self):
        msg = DPR_O48()
        assert msg._structure_id == "DPR_O48"

    def test_instantiate_drc_o47(self):
        msg = DRC_O47()
        assert msg._structure_id == "DRC_O47"

    def test_instantiate_drg_o43(self):
        msg = DRG_O43()
        assert msg._structure_id == "DRG_O43"

    def test_instantiate_eac_u07(self):
        msg = EAC_U07()
        assert msg._structure_id == "EAC_U07"

    def test_instantiate_ean_u09(self):
        msg = EAN_U09()
        assert msg._structure_id == "EAN_U09"

    def test_instantiate_ear_u08(self):
        msg = EAR_U08()
        assert msg._structure_id == "EAR_U08"

    def test_instantiate_ehc_e01(self):
        msg = EHC_E01()
        assert msg._structure_id == "EHC_E01"

    def test_instantiate_ehc_e02(self):
        msg = EHC_E02()
        assert msg._structure_id == "EHC_E02"

    def test_instantiate_ehc_e04(self):
        msg = EHC_E04()
        assert msg._structure_id == "EHC_E04"

    def test_instantiate_ehc_e10(self):
        msg = EHC_E10()
        assert msg._structure_id == "EHC_E10"

    def test_instantiate_ehc_e12(self):
        msg = EHC_E12()
        assert msg._structure_id == "EHC_E12"

    def test_instantiate_ehc_e13(self):
        msg = EHC_E13()
        assert msg._structure_id == "EHC_E13"

    def test_instantiate_ehc_e15(self):
        msg = EHC_E15()
        assert msg._structure_id == "EHC_E15"

    def test_instantiate_ehc_e20(self):
        msg = EHC_E20()
        assert msg._structure_id == "EHC_E20"

    def test_instantiate_ehc_e21(self):
        msg = EHC_E21()
        assert msg._structure_id == "EHC_E21"

    def test_instantiate_ehc_e24(self):
        msg = EHC_E24()
        assert msg._structure_id == "EHC_E24"

    def test_instantiate_esr_u02(self):
        msg = ESR_U02()
        assert msg._structure_id == "ESR_U02"

    def test_instantiate_esu_u01(self):
        msg = ESU_U01()
        assert msg._structure_id == "ESU_U01"

    def test_instantiate_inr_u06(self):
        msg = INR_U06()
        assert msg._structure_id == "INR_U06"

    def test_instantiate_inr_u14(self):
        msg = INR_U14()
        assert msg._structure_id == "INR_U14"

    def test_instantiate_inu_u05(self):
        msg = INU_U05()
        assert msg._structure_id == "INU_U05"

    def test_instantiate_lsu_u12(self):
        msg = LSU_U12()
        assert msg._structure_id == "LSU_U12"

    def test_instantiate_mdm_t01(self):
        msg = MDM_T01()
        assert msg._structure_id == "MDM_T01"

    def test_instantiate_mdm_t02(self):
        msg = MDM_T02()
        assert msg._structure_id == "MDM_T02"

    def test_instantiate_mfk_m01(self):
        msg = MFK_M01()
        assert msg._structure_id == "MFK_M01"

    def test_instantiate_mfn_m02(self):
        msg = MFN_M02()
        assert msg._structure_id == "MFN_M02"

    def test_instantiate_mfn_m04(self):
        msg = MFN_M04()
        assert msg._structure_id == "MFN_M04"

    def test_instantiate_mfn_m05(self):
        msg = MFN_M05()
        assert msg._structure_id == "MFN_M05"

    def test_instantiate_mfn_m06(self):
        msg = MFN_M06()
        assert msg._structure_id == "MFN_M06"

    def test_instantiate_mfn_m07(self):
        msg = MFN_M07()
        assert msg._structure_id == "MFN_M07"

    def test_instantiate_mfn_m08(self):
        msg = MFN_M08()
        assert msg._structure_id == "MFN_M08"

    def test_instantiate_mfn_m09(self):
        msg = MFN_M09()
        assert msg._structure_id == "MFN_M09"

    def test_instantiate_mfn_m10(self):
        msg = MFN_M10()
        assert msg._structure_id == "MFN_M10"

    def test_instantiate_mfn_m11(self):
        msg = MFN_M11()
        assert msg._structure_id == "MFN_M11"

    def test_instantiate_mfn_m12(self):
        msg = MFN_M12()
        assert msg._structure_id == "MFN_M12"

    def test_instantiate_mfn_m13(self):
        msg = MFN_M13()
        assert msg._structure_id == "MFN_M13"

    def test_instantiate_mfn_m15(self):
        msg = MFN_M15()
        assert msg._structure_id == "MFN_M15"

    def test_instantiate_mfn_m16(self):
        msg = MFN_M16()
        assert msg._structure_id == "MFN_M16"

    def test_instantiate_mfn_m17(self):
        msg = MFN_M17()
        assert msg._structure_id == "MFN_M17"

    def test_instantiate_mfn_m18(self):
        msg = MFN_M18()
        assert msg._structure_id == "MFN_M18"

    def test_instantiate_mfn_m19(self):
        msg = MFN_M19()
        assert msg._structure_id == "MFN_M19"

    def test_instantiate_mfn_znn(self):
        msg = MFN_Znn()
        assert msg._structure_id == "MFN_Znn"

    def test_instantiate_nmd_n02(self):
        msg = NMD_N02()
        assert msg._structure_id == "NMD_N02"

    def test_instantiate_omb_o27(self):
        msg = OMB_O27()
        assert msg._structure_id == "OMB_O27"

    def test_instantiate_omd_o03(self):
        msg = OMD_O03()
        assert msg._structure_id == "OMD_O03"

    def test_instantiate_omg_o19(self):
        msg = OMG_O19()
        assert msg._structure_id == "OMG_O19"

    def test_instantiate_omi_o23(self):
        msg = OMI_O23()
        assert msg._structure_id == "OMI_O23"

    def test_instantiate_oml_o21(self):
        msg = OML_O21()
        assert msg._structure_id == "OML_O21"

    def test_instantiate_oml_o33(self):
        msg = OML_O33()
        assert msg._structure_id == "OML_O33"

    def test_instantiate_oml_o35(self):
        msg = OML_O35()
        assert msg._structure_id == "OML_O35"

    def test_instantiate_oml_o39(self):
        msg = OML_O39()
        assert msg._structure_id == "OML_O39"

    def test_instantiate_oml_o59(self):
        msg = OML_O59()
        assert msg._structure_id == "OML_O59"

    def test_instantiate_omn_o07(self):
        msg = OMN_O07()
        assert msg._structure_id == "OMN_O07"

    def test_instantiate_omp_o09(self):
        msg = OMP_O09()
        assert msg._structure_id == "OMP_O09"

    def test_instantiate_omq_o57(self):
        msg = OMQ_O57()
        assert msg._structure_id == "OMQ_O57"

    def test_instantiate_oms_o05(self):
        msg = OMS_O05()
        assert msg._structure_id == "OMS_O05"

    def test_instantiate_opl_o37(self):
        msg = OPL_O37()
        assert msg._structure_id == "OPL_O37"

    def test_instantiate_opr_o38(self):
        msg = OPR_O38()
        assert msg._structure_id == "OPR_O38"

    def test_instantiate_opu_r25(self):
        msg = OPU_R25()
        assert msg._structure_id == "OPU_R25"

    def test_instantiate_ora_r33(self):
        msg = ORA_R33()
        assert msg._structure_id == "ORA_R33"

    def test_instantiate_ora_r41(self):
        msg = ORA_R41()
        assert msg._structure_id == "ORA_R41"

    def test_instantiate_orb_o28(self):
        msg = ORB_O28()
        assert msg._structure_id == "ORB_O28"

    def test_instantiate_ord_o04(self):
        msg = ORD_O04()
        assert msg._structure_id == "ORD_O04"

    def test_instantiate_org_o20(self):
        msg = ORG_O20()
        assert msg._structure_id == "ORG_O20"

    def test_instantiate_ori_o24(self):
        msg = ORI_O24()
        assert msg._structure_id == "ORI_O24"

    def test_instantiate_orl_o22(self):
        msg = ORL_O22()
        assert msg._structure_id == "ORL_O22"

    def test_instantiate_orl_o34(self):
        msg = ORL_O34()
        assert msg._structure_id == "ORL_O34"

    def test_instantiate_orl_o36(self):
        msg = ORL_O36()
        assert msg._structure_id == "ORL_O36"

    def test_instantiate_orl_o40(self):
        msg = ORL_O40()
        assert msg._structure_id == "ORL_O40"

    def test_instantiate_orl_o53(self):
        msg = ORL_O53()
        assert msg._structure_id == "ORL_O53"

    def test_instantiate_orl_o54(self):
        msg = ORL_O54()
        assert msg._structure_id == "ORL_O54"

    def test_instantiate_orl_o55(self):
        msg = ORL_O55()
        assert msg._structure_id == "ORL_O55"

    def test_instantiate_orl_o56(self):
        msg = ORL_O56()
        assert msg._structure_id == "ORL_O56"

    def test_instantiate_orm_o01(self):
        msg = ORM_O01()
        assert msg._structure_id == "ORM_O01"

    def test_instantiate_orn_o08(self):
        msg = ORN_O08()
        assert msg._structure_id == "ORN_O08"

    def test_instantiate_orp_o10(self):
        msg = ORP_O10()
        assert msg._structure_id == "ORP_O10"

    def test_instantiate_ors_o06(self):
        msg = ORS_O06()
        assert msg._structure_id == "ORS_O06"

    def test_instantiate_oru_r01(self):
        msg = ORU_R01()
        assert msg._structure_id == "ORU_R01"

    def test_instantiate_oru_r30(self):
        msg = ORU_R30()
        assert msg._structure_id == "ORU_R30"

    def test_instantiate_orx_o58(self):
        msg = ORX_O58()
        assert msg._structure_id == "ORX_O58"

    def test_instantiate_osm_r26(self):
        msg = OSM_R26()
        assert msg._structure_id == "OSM_R26"

    def test_instantiate_osu_o51(self):
        msg = OSU_O51()
        assert msg._structure_id == "OSU_O51"

    def test_instantiate_osu_o52(self):
        msg = OSU_O52()
        assert msg._structure_id == "OSU_O52"

    def test_instantiate_oul_r22(self):
        msg = OUL_R22()
        assert msg._structure_id == "OUL_R22"

    def test_instantiate_oul_r23(self):
        msg = OUL_R23()
        assert msg._structure_id == "OUL_R23"

    def test_instantiate_oul_r24(self):
        msg = OUL_R24()
        assert msg._structure_id == "OUL_R24"

    def test_instantiate_pex_p07(self):
        msg = PEX_P07()
        assert msg._structure_id == "PEX_P07"

    def test_instantiate_pgl_pc6(self):
        msg = PGL_PC6()
        assert msg._structure_id == "PGL_PC6"

    def test_instantiate_pmu_b01(self):
        msg = PMU_B01()
        assert msg._structure_id == "PMU_B01"

    def test_instantiate_pmu_b03(self):
        msg = PMU_B03()
        assert msg._structure_id == "PMU_B03"

    def test_instantiate_pmu_b04(self):
        msg = PMU_B04()
        assert msg._structure_id == "PMU_B04"

    def test_instantiate_pmu_b07(self):
        msg = PMU_B07()
        assert msg._structure_id == "PMU_B07"

    def test_instantiate_pmu_b08(self):
        msg = PMU_B08()
        assert msg._structure_id == "PMU_B08"

    def test_instantiate_ppg_pcg(self):
        msg = PPG_PCG()
        assert msg._structure_id == "PPG_PCG"

    def test_instantiate_ppp_pcb(self):
        msg = PPP_PCB()
        assert msg._structure_id == "PPP_PCB"

    def test_instantiate_ppr_pc1(self):
        msg = PPR_PC1()
        assert msg._structure_id == "PPR_PC1"

    def test_instantiate_qbp_e03(self):
        msg = QBP_E03()
        assert msg._structure_id == "QBP_E03"

    def test_instantiate_qbp_e22(self):
        msg = QBP_E22()
        assert msg._structure_id == "QBP_E22"

    def test_instantiate_qbp_o33(self):
        msg = QBP_O33()
        assert msg._structure_id == "QBP_O33"

    def test_instantiate_qbp_o34(self):
        msg = QBP_O34()
        assert msg._structure_id == "QBP_O34"

    def test_instantiate_qbp_q11(self):
        msg = QBP_Q11()
        assert msg._structure_id == "QBP_Q11"

    def test_instantiate_qbp_q13(self):
        msg = QBP_Q13()
        assert msg._structure_id == "QBP_Q13"

    def test_instantiate_qbp_q15(self):
        msg = QBP_Q15()
        assert msg._structure_id == "QBP_Q15"

    def test_instantiate_qbp_q21(self):
        msg = QBP_Q21()
        assert msg._structure_id == "QBP_Q21"

    def test_instantiate_qbp_qnn(self):
        msg = QBP_Qnn()
        assert msg._structure_id == "QBP_Qnn"

    def test_instantiate_qbp_z73(self):
        msg = QBP_Z73()
        assert msg._structure_id == "QBP_Z73"

    def test_instantiate_qcn_j01(self):
        msg = QCN_J01()
        assert msg._structure_id == "QCN_J01"

    def test_instantiate_qry_a19(self):
        msg = QRY_A19()
        assert msg._structure_id == "QRY_A19"

    def test_instantiate_qsb_q16(self):
        msg = QSB_Q16()
        assert msg._structure_id == "QSB_Q16"

    def test_instantiate_qvr_q17(self):
        msg = QVR_Q17()
        assert msg._structure_id == "QVR_Q17"

    def test_instantiate_ras_o17(self):
        msg = RAS_O17()
        assert msg._structure_id == "RAS_O17"

    def test_instantiate_rcv_o59(self):
        msg = RCV_O59()
        assert msg._structure_id == "RCV_O59"

    def test_instantiate_rde_o11(self):
        msg = RDE_O11()
        assert msg._structure_id == "RDE_O11"

    def test_instantiate_rde_o49(self):
        msg = RDE_O49()
        assert msg._structure_id == "RDE_O49"

    def test_instantiate_rdr_rdr(self):
        msg = RDR_RDR()
        assert msg._structure_id == "RDR_RDR"

    def test_instantiate_rds_o13(self):
        msg = RDS_O13()
        assert msg._structure_id == "RDS_O13"

    def test_instantiate_rdy_k15(self):
        msg = RDY_K15()
        assert msg._structure_id == "RDY_K15"

    def test_instantiate_rdy_z80(self):
        msg = RDY_Z80()
        assert msg._structure_id == "RDY_Z80"

    def test_instantiate_ref_i12(self):
        msg = REF_I12()
        assert msg._structure_id == "REF_I12"

    def test_instantiate_rgv_o15(self):
        msg = RGV_O15()
        assert msg._structure_id == "RGV_O15"

    def test_instantiate_rpa_i08(self):
        msg = RPA_I08()
        assert msg._structure_id == "RPA_I08"

    def test_instantiate_rpi_i01(self):
        msg = RPI_I01()
        assert msg._structure_id == "RPI_I01"

    def test_instantiate_rpi_i04(self):
        msg = RPI_I04()
        assert msg._structure_id == "RPI_I04"

    def test_instantiate_rpl_i02(self):
        msg = RPL_I02()
        assert msg._structure_id == "RPL_I02"

    def test_instantiate_rpr_i03(self):
        msg = RPR_I03()
        assert msg._structure_id == "RPR_I03"

    def test_instantiate_rqa_i08(self):
        msg = RQA_I08()
        assert msg._structure_id == "RQA_I08"

    def test_instantiate_rqi_i01(self):
        msg = RQI_I01()
        assert msg._structure_id == "RQI_I01"

    def test_instantiate_rqp_i04(self):
        msg = RQP_I04()
        assert msg._structure_id == "RQP_I04"

    def test_instantiate_rra_o18(self):
        msg = RRA_O18()
        assert msg._structure_id == "RRA_O18"

    def test_instantiate_rrd_o14(self):
        msg = RRD_O14()
        assert msg._structure_id == "RRD_O14"

    def test_instantiate_rre_o12(self):
        msg = RRE_O12()
        assert msg._structure_id == "RRE_O12"

    def test_instantiate_rre_o50(self):
        msg = RRE_O50()
        assert msg._structure_id == "RRE_O50"

    def test_instantiate_rrg_o16(self):
        msg = RRG_O16()
        assert msg._structure_id == "RRG_O16"

    def test_instantiate_rri_i12(self):
        msg = RRI_I12()
        assert msg._structure_id == "RRI_I12"

    def test_instantiate_rsp_e03(self):
        msg = RSP_E03()
        assert msg._structure_id == "RSP_E03"

    def test_instantiate_rsp_e22(self):
        msg = RSP_E22()
        assert msg._structure_id == "RSP_E22"

    def test_instantiate_rsp_k11(self):
        msg = RSP_K11()
        assert msg._structure_id == "RSP_K11"

    def test_instantiate_rsp_k21(self):
        msg = RSP_K21()
        assert msg._structure_id == "RSP_K21"

    def test_instantiate_rsp_k22(self):
        msg = RSP_K22()
        assert msg._structure_id == "RSP_K22"

    def test_instantiate_rsp_k23(self):
        msg = RSP_K23()
        assert msg._structure_id == "RSP_K23"

    def test_instantiate_rsp_k25(self):
        msg = RSP_K25()
        assert msg._structure_id == "RSP_K25"

    def test_instantiate_rsp_k31(self):
        msg = RSP_K31()
        assert msg._structure_id == "RSP_K31"

    def test_instantiate_rsp_k32(self):
        msg = RSP_K32()
        assert msg._structure_id == "RSP_K32"

    def test_instantiate_rsp_o33(self):
        msg = RSP_O33()
        assert msg._structure_id == "RSP_O33"

    def test_instantiate_rsp_o34(self):
        msg = RSP_O34()
        assert msg._structure_id == "RSP_O34"

    def test_instantiate_rsp_z82(self):
        msg = RSP_Z82()
        assert msg._structure_id == "RSP_Z82"

    def test_instantiate_rsp_z84(self):
        msg = RSP_Z84()
        assert msg._structure_id == "RSP_Z84"

    def test_instantiate_rsp_z86(self):
        msg = RSP_Z86()
        assert msg._structure_id == "RSP_Z86"

    def test_instantiate_rsp_z88(self):
        msg = RSP_Z88()
        assert msg._structure_id == "RSP_Z88"

    def test_instantiate_rsp_z90(self):
        msg = RSP_Z90()
        assert msg._structure_id == "RSP_Z90"

    def test_instantiate_rsp_znn(self):
        msg = RSP_Znn()
        assert msg._structure_id == "RSP_Znn"

    def test_instantiate_rtb_k13(self):
        msg = RTB_K13()
        assert msg._structure_id == "RTB_K13"

    def test_instantiate_rtb_knn(self):
        msg = RTB_Knn()
        assert msg._structure_id == "RTB_Knn"

    def test_instantiate_rtb_z74(self):
        msg = RTB_Z74()
        assert msg._structure_id == "RTB_Z74"

    def test_instantiate_sdr_s31(self):
        msg = SDR_S31()
        assert msg._structure_id == "SDR_S31"

    def test_instantiate_sdr_s32(self):
        msg = SDR_S32()
        assert msg._structure_id == "SDR_S32"

    def test_instantiate_siu_s12(self):
        msg = SIU_S12()
        assert msg._structure_id == "SIU_S12"

    def test_instantiate_slr_s28(self):
        msg = SLR_S28()
        assert msg._structure_id == "SLR_S28"

    def test_instantiate_srm_s01(self):
        msg = SRM_S01()
        assert msg._structure_id == "SRM_S01"

    def test_instantiate_srr_s01(self):
        msg = SRR_S01()
        assert msg._structure_id == "SRR_S01"

    def test_instantiate_ssr_u04(self):
        msg = SSR_U04()
        assert msg._structure_id == "SSR_U04"

    def test_instantiate_ssu_u03(self):
        msg = SSU_U03()
        assert msg._structure_id == "SSU_U03"

    def test_instantiate_stc_s33(self):
        msg = STC_S33()
        assert msg._structure_id == "STC_S33"

    def test_instantiate_tcu_u10(self):
        msg = TCU_U10()
        assert msg._structure_id == "TCU_U10"

    def test_instantiate_udm_q05(self):
        msg = UDM_Q05()
        assert msg._structure_id == "UDM_Q05"

    def test_instantiate_vxu_v04(self):
        msg = VXU_V04()
        assert msg._structure_id == "VXU_V04"
