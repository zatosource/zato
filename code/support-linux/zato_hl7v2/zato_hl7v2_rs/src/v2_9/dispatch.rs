// Generated - do not edit
use crate::{RawMessage, ParseError, SegmentCursor};
use super::messages::*;

pub fn parse_message(
    msh9: (&str, &str, &str),
    cursor: &mut SegmentCursor,
) -> Result<RawMessage, ParseError> {
    match msh9 {
        ("ACK", "", _) | (_, _, "ACK") =>
            parse_ack(cursor),
        ("ADT", "A01", _) | (_, _, "ADT_A01") =>
            parse_adt_a01(cursor),
        ("ADT", "A04", _) | (_, _, "ADT_A01") =>
            parse_adt_a01(cursor),
        ("ADT", "A08", _) | (_, _, "ADT_A01") =>
            parse_adt_a01(cursor),
        ("ADT", "A13", _) | (_, _, "ADT_A01") =>
            parse_adt_a01(cursor),
        ("ADT", "A02", _) | (_, _, "ADT_A02") =>
            parse_adt_a02(cursor),
        ("ADT", "A03", _) | (_, _, "ADT_A03") =>
            parse_adt_a03(cursor),
        ("ADT", "A05", _) | (_, _, "ADT_A05") =>
            parse_adt_a05(cursor),
        ("ADT", "A14", _) | (_, _, "ADT_A05") =>
            parse_adt_a05(cursor),
        ("ADT", "A28", _) | (_, _, "ADT_A05") =>
            parse_adt_a05(cursor),
        ("ADT", "A31", _) | (_, _, "ADT_A05") =>
            parse_adt_a05(cursor),
        ("ADT", "A06", _) | (_, _, "ADT_A06") =>
            parse_adt_a06(cursor),
        ("ADT", "A07", _) | (_, _, "ADT_A06") =>
            parse_adt_a06(cursor),
        ("ADT", "A09", _) | (_, _, "ADT_A09") =>
            parse_adt_a09(cursor),
        ("ADT", "A10", _) | (_, _, "ADT_A09") =>
            parse_adt_a09(cursor),
        ("ADT", "A11", _) | (_, _, "ADT_A09") =>
            parse_adt_a09(cursor),
        ("ADT", "A12", _) | (_, _, "ADT_A12") =>
            parse_adt_a12(cursor),
        ("ADT", "A15", _) | (_, _, "ADT_A15") =>
            parse_adt_a15(cursor),
        ("ADT", "A16", _) | (_, _, "ADT_A16") =>
            parse_adt_a16(cursor),
        ("ADT", "A17", _) | (_, _, "ADT_A17") =>
            parse_adt_a17(cursor),
        ("ADT", "A20", _) | (_, _, "ADT_A20") =>
            parse_adt_a20(cursor),
        ("ADT", "A21", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A22", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A23", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A25", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A26", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A27", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A29", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A32", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A33", _) | (_, _, "ADT_A21") =>
            parse_adt_a21(cursor),
        ("ADT", "A24", _) | (_, _, "ADT_A24") =>
            parse_adt_a24(cursor),
        ("ADT", "A37", _) | (_, _, "ADT_A37") =>
            parse_adt_a37(cursor),
        ("ADT", "A38", _) | (_, _, "ADT_A38") =>
            parse_adt_a38(cursor),
        ("ADT", "A39", _) | (_, _, "ADT_A39") =>
            parse_adt_a39(cursor),
        ("ADT", "A40", _) | (_, _, "ADT_A39") =>
            parse_adt_a39(cursor),
        ("ADT", "A41", _) | (_, _, "ADT_A39") =>
            parse_adt_a39(cursor),
        ("ADT", "A42", _) | (_, _, "ADT_A39") =>
            parse_adt_a39(cursor),
        ("ADT", "A43", _) | (_, _, "ADT_A43") =>
            parse_adt_a43(cursor),
        ("ADT", "A49", _) | (_, _, "ADT_A43") =>
            parse_adt_a43(cursor),
        ("ADT", "A44", _) | (_, _, "ADT_A44") =>
            parse_adt_a44(cursor),
        ("ADT", "A47", _) | (_, _, "ADT_A44") =>
            parse_adt_a44(cursor),
        ("ADT", "A45", _) | (_, _, "ADT_A45") =>
            parse_adt_a45(cursor),
        ("ADT", "A50", _) | (_, _, "ADT_A50") =>
            parse_adt_a50(cursor),
        ("ADT", "A51", _) | (_, _, "ADT_A50") =>
            parse_adt_a50(cursor),
        ("ADT", "A52", _) | (_, _, "ADT_A52") =>
            parse_adt_a52(cursor),
        ("ADT", "A53", _) | (_, _, "ADT_A52") =>
            parse_adt_a52(cursor),
        ("ADT", "A54", _) | (_, _, "ADT_A54") =>
            parse_adt_a54(cursor),
        ("ADT", "A55", _) | (_, _, "ADT_A54") =>
            parse_adt_a54(cursor),
        ("ADT", "A60", _) | (_, _, "ADT_A60") =>
            parse_adt_a60(cursor),
        ("ADT", "A61", _) | (_, _, "ADT_A61") =>
            parse_adt_a61(cursor),
        ("ADT", "A62", _) | (_, _, "ADT_A61") =>
            parse_adt_a61(cursor),
        ("BAR", "P01", _) | (_, _, "BAR_P01") =>
            parse_bar_p01(cursor),
        ("BAR", "P02", _) | (_, _, "BAR_P02") =>
            parse_bar_p02(cursor),
        ("BAR", "P05", _) | (_, _, "BAR_P05") =>
            parse_bar_p05(cursor),
        ("BAR", "P06", _) | (_, _, "BAR_P06") =>
            parse_bar_p06(cursor),
        ("BAR", "P10", _) | (_, _, "BAR_P10") =>
            parse_bar_p10(cursor),
        ("BAR", "P12", _) | (_, _, "BAR_P12") =>
            parse_bar_p12(cursor),
        ("BPS", "O29", _) | (_, _, "BPS_O29") =>
            parse_bps_o29(cursor),
        ("BRP", "O30", _) | (_, _, "BRP_O30") =>
            parse_brp_o30(cursor),
        ("BRT", "O32", _) | (_, _, "BRT_O32") =>
            parse_brt_o32(cursor),
        ("BTS", "O31", _) | (_, _, "BTS_O31") =>
            parse_bts_o31(cursor),
        ("CCF", "I22", _) | (_, _, "CCF_I22") =>
            parse_ccf_i22(cursor),
        ("CCI", "I22", _) | (_, _, "CCI_I22") =>
            parse_cci_i22(cursor),
        ("CCM", "I21", _) | (_, _, "CCM_I21") =>
            parse_ccm_i21(cursor),
        ("CCQ", "I19", _) | (_, _, "CCQ_I19") =>
            parse_ccq_i19(cursor),
        ("CCR", "I16", _) | (_, _, "CCR_I16") =>
            parse_ccr_i16(cursor),
        ("CCR", "I17", _) | (_, _, "CCR_I16") =>
            parse_ccr_i16(cursor),
        ("CCR", "I18", _) | (_, _, "CCR_I16") =>
            parse_ccr_i16(cursor),
        ("CCU", "I20", _) | (_, _, "CCU_I20") =>
            parse_ccu_i20(cursor),
        ("CQU", "I19", _) | (_, _, "CQU_I19") =>
            parse_cqu_i19(cursor),
        ("CRM", "C01", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C02", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C03", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C04", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C05", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C06", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C07", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CRM", "C08", _) | (_, _, "CRM_C01") =>
            parse_crm_c01(cursor),
        ("CSU", "C09", _) | (_, _, "CSU_C09") =>
            parse_csu_c09(cursor),
        ("CSU", "C10", _) | (_, _, "CSU_C09") =>
            parse_csu_c09(cursor),
        ("CSU", "C11", _) | (_, _, "CSU_C09") =>
            parse_csu_c09(cursor),
        ("CSU", "C12", _) | (_, _, "CSU_C09") =>
            parse_csu_c09(cursor),
        ("DBC", "O41", _) | (_, _, "DBC_O41") =>
            parse_dbc_o41(cursor),
        ("DBC", "O42", _) | (_, _, "DBC_O42") =>
            parse_dbc_o42(cursor),
        ("DEL", "O46", _) | (_, _, "DEL_O46") =>
            parse_del_o46(cursor),
        ("DEO", "O45", _) | (_, _, "DEO_O45") =>
            parse_deo_o45(cursor),
        ("DER", "O44", _) | (_, _, "DER_O44") =>
            parse_der_o44(cursor),
        ("DFT", "P03", _) | (_, _, "DFT_P03") =>
            parse_dft_p03(cursor),
        ("DFT", "P11", _) | (_, _, "DFT_P11") =>
            parse_dft_p11(cursor),
        ("DPR", "O48", _) | (_, _, "DPR_O48") =>
            parse_dpr_o48(cursor),
        ("DRC", "O47", _) | (_, _, "DRC_O47") =>
            parse_drc_o47(cursor),
        ("DRG", "O43", _) | (_, _, "DRG_O43") =>
            parse_drg_o43(cursor),
        ("EAC", "U07", _) | (_, _, "EAC_U07") =>
            parse_eac_u07(cursor),
        ("EAN", "U09", _) | (_, _, "EAN_U09") =>
            parse_ean_u09(cursor),
        ("EAR", "U08", _) | (_, _, "EAR_U08") =>
            parse_ear_u08(cursor),
        ("EHC", "E01", _) | (_, _, "EHC_E01") =>
            parse_ehc_e01(cursor),
        ("EHC", "E02", _) | (_, _, "EHC_E02") =>
            parse_ehc_e02(cursor),
        ("EHC", "E04", _) | (_, _, "EHC_E04") =>
            parse_ehc_e04(cursor),
        ("EHC", "E10", _) | (_, _, "EHC_E10") =>
            parse_ehc_e10(cursor),
        ("EHC", "E12", _) | (_, _, "EHC_E12") =>
            parse_ehc_e12(cursor),
        ("EHC", "E13", _) | (_, _, "EHC_E13") =>
            parse_ehc_e13(cursor),
        ("EHC", "E15", _) | (_, _, "EHC_E15") =>
            parse_ehc_e15(cursor),
        ("EHC", "E20", _) | (_, _, "EHC_E20") =>
            parse_ehc_e20(cursor),
        ("EHC", "E21", _) | (_, _, "EHC_E21") =>
            parse_ehc_e21(cursor),
        ("EHC", "E24", _) | (_, _, "EHC_E24") =>
            parse_ehc_e24(cursor),
        ("ESR", "U02", _) | (_, _, "ESR_U02") =>
            parse_esr_u02(cursor),
        ("ESU", "U01", _) | (_, _, "ESU_U01") =>
            parse_esu_u01(cursor),
        ("INR", "U06", _) | (_, _, "INR_U06") =>
            parse_inr_u06(cursor),
        ("INR", "U14", _) | (_, _, "INR_U14") =>
            parse_inr_u14(cursor),
        ("INU", "U05", _) | (_, _, "INU_U05") =>
            parse_inu_u05(cursor),
        ("LSU", "U12", _) | (_, _, "LSU_U12") =>
            parse_lsu_u12(cursor),
        ("LSR", "U13", _) | (_, _, "LSU_U12") =>
            parse_lsu_u12(cursor),
        ("MDM", "T01", _) | (_, _, "MDM_T01") =>
            parse_mdm_t01(cursor),
        ("MDM", "T03", _) | (_, _, "MDM_T01") =>
            parse_mdm_t01(cursor),
        ("MDM", "T05", _) | (_, _, "MDM_T01") =>
            parse_mdm_t01(cursor),
        ("MDM", "T07", _) | (_, _, "MDM_T01") =>
            parse_mdm_t01(cursor),
        ("MDM", "T09", _) | (_, _, "MDM_T01") =>
            parse_mdm_t01(cursor),
        ("MDM", "T11", _) | (_, _, "MDM_T01") =>
            parse_mdm_t01(cursor),
        ("MDM", "T02", _) | (_, _, "MDM_T02") =>
            parse_mdm_t02(cursor),
        ("MDM", "T04", _) | (_, _, "MDM_T02") =>
            parse_mdm_t02(cursor),
        ("MDM", "T06", _) | (_, _, "MDM_T02") =>
            parse_mdm_t02(cursor),
        ("MDM", "T08", _) | (_, _, "MDM_T02") =>
            parse_mdm_t02(cursor),
        ("MDM", "T10", _) | (_, _, "MDM_T02") =>
            parse_mdm_t02(cursor),
        ("MFK", "M01", _) | (_, _, "MFK_M01") =>
            parse_mfk_m01(cursor),
        ("MFN", "M02", _) | (_, _, "MFN_M02") =>
            parse_mfn_m02(cursor),
        ("MFN", "M04", _) | (_, _, "MFN_M04") =>
            parse_mfn_m04(cursor),
        ("MFN", "M05", _) | (_, _, "MFN_M05") =>
            parse_mfn_m05(cursor),
        ("MFN", "M06", _) | (_, _, "MFN_M06") =>
            parse_mfn_m06(cursor),
        ("MFN", "M07", _) | (_, _, "MFN_M07") =>
            parse_mfn_m07(cursor),
        ("MFN", "M08", _) | (_, _, "MFN_M08") =>
            parse_mfn_m08(cursor),
        ("MFN", "M09", _) | (_, _, "MFN_M09") =>
            parse_mfn_m09(cursor),
        ("MFN", "M10", _) | (_, _, "MFN_M10") =>
            parse_mfn_m10(cursor),
        ("MFN", "M11", _) | (_, _, "MFN_M11") =>
            parse_mfn_m11(cursor),
        ("MFN", "M12", _) | (_, _, "MFN_M12") =>
            parse_mfn_m12(cursor),
        ("MFN", "M13", _) | (_, _, "MFN_M13") =>
            parse_mfn_m13(cursor),
        ("MFN", "M15", _) | (_, _, "MFN_M15") =>
            parse_mfn_m15(cursor),
        ("MFN", "M16", _) | (_, _, "MFN_M16") =>
            parse_mfn_m16(cursor),
        ("MFN", "M17", _) | (_, _, "MFN_M17") =>
            parse_mfn_m17(cursor),
        ("MFN", "M18", _) | (_, _, "MFN_M18") =>
            parse_mfn_m18(cursor),
        ("MFN", "M19", _) | (_, _, "MFN_M19") =>
            parse_mfn_m19(cursor),
        ("MFN", "M14", _) | (_, _, "MFN_Znn") =>
            parse_mfn_znn(cursor),
        ("NMD", "N02", _) | (_, _, "NMD_N02") =>
            parse_nmd_n02(cursor),
        ("OMB", "O27", _) | (_, _, "OMB_O27") =>
            parse_omb_o27(cursor),
        ("OMD", "O03", _) | (_, _, "OMD_O03") =>
            parse_omd_o03(cursor),
        ("OMG", "O19", _) | (_, _, "OMG_O19") =>
            parse_omg_o19(cursor),
        ("OMI", "O23", _) | (_, _, "OMI_O23") =>
            parse_omi_o23(cursor),
        ("OML", "O21", _) | (_, _, "OML_O21") =>
            parse_oml_o21(cursor),
        ("OML", "O33", _) | (_, _, "OML_O33") =>
            parse_oml_o33(cursor),
        ("OML", "O35", _) | (_, _, "OML_O35") =>
            parse_oml_o35(cursor),
        ("OML", "O39", _) | (_, _, "OML_O39") =>
            parse_oml_o39(cursor),
        ("OML", "O59", _) | (_, _, "OML_O59") =>
            parse_oml_o59(cursor),
        ("OMN", "O07", _) | (_, _, "OMN_O07") =>
            parse_omn_o07(cursor),
        ("OMP", "O09", _) | (_, _, "OMP_O09") =>
            parse_omp_o09(cursor),
        ("OMQ", "O57", _) | (_, _, "OMQ_O57") =>
            parse_omq_o57(cursor),
        ("OMS", "O05", _) | (_, _, "OMS_O05") =>
            parse_oms_o05(cursor),
        ("OPL", "O37", _) | (_, _, "OPL_O37") =>
            parse_opl_o37(cursor),
        ("OPR", "O38", _) | (_, _, "OPR_O38") =>
            parse_opr_o38(cursor),
        ("OPU", "R25", _) | (_, _, "OPU_R25") =>
            parse_opu_r25(cursor),
        ("ORA", "R33", _) | (_, _, "ORA_R33") =>
            parse_ora_r33(cursor),
        ("ORA", "R41", _) | (_, _, "ORA_R41") =>
            parse_ora_r41(cursor),
        ("ORB", "O28", _) | (_, _, "ORB_O28") =>
            parse_orb_o28(cursor),
        ("ORD", "O04", _) | (_, _, "ORD_O04") =>
            parse_ord_o04(cursor),
        ("ORG", "O20", _) | (_, _, "ORG_O20") =>
            parse_org_o20(cursor),
        ("ORI", "O24", _) | (_, _, "ORI_O24") =>
            parse_ori_o24(cursor),
        ("ORL", "O22", _) | (_, _, "ORL_O22") =>
            parse_orl_o22(cursor),
        ("ORL", "O34", _) | (_, _, "ORL_O34") =>
            parse_orl_o34(cursor),
        ("ORL", "O36", _) | (_, _, "ORL_O36") =>
            parse_orl_o36(cursor),
        ("ORL", "O40", _) | (_, _, "ORL_O40") =>
            parse_orl_o40(cursor),
        ("ORL", "O53", _) | (_, _, "ORL_O53") =>
            parse_orl_o53(cursor),
        ("ORL", "O54", _) | (_, _, "ORL_O54") =>
            parse_orl_o54(cursor),
        ("ORL", "O55", _) | (_, _, "ORL_O55") =>
            parse_orl_o55(cursor),
        ("ORL", "O56", _) | (_, _, "ORL_O56") =>
            parse_orl_o56(cursor),
        ("ORN", "O08", _) | (_, _, "ORN_O08") =>
            parse_orn_o08(cursor),
        ("ORP", "O10", _) | (_, _, "ORP_O10") =>
            parse_orp_o10(cursor),
        ("ORS", "O06", _) | (_, _, "ORS_O06") =>
            parse_ors_o06(cursor),
        ("ORU", "R01", _) | (_, _, "ORU_R01") =>
            parse_oru_r01(cursor),
        ("ORU", "R40", _) | (_, _, "ORU_R01") =>
            parse_oru_r01(cursor),
        ("ORU", "R30", _) | (_, _, "ORU_R30") =>
            parse_oru_r30(cursor),
        ("ORU", "R31", _) | (_, _, "ORU_R30") =>
            parse_oru_r30(cursor),
        ("ORU", "R32", _) | (_, _, "ORU_R30") =>
            parse_oru_r30(cursor),
        ("ORX", "O58", _) | (_, _, "ORX_O58") =>
            parse_orx_o58(cursor),
        ("OSM", "R26", _) | (_, _, "OSM_R26") =>
            parse_osm_r26(cursor),
        ("OSU", "O51", _) | (_, _, "OSU_O51") =>
            parse_osu_o51(cursor),
        ("OSU", "O52", _) | (_, _, "OSU_O52") =>
            parse_osu_o52(cursor),
        ("OUL", "R22", _) | (_, _, "OUL_R22") =>
            parse_oul_r22(cursor),
        ("OUL", "R23", _) | (_, _, "OUL_R23") =>
            parse_oul_r23(cursor),
        ("OUL", "R24", _) | (_, _, "OUL_R24") =>
            parse_oul_r24(cursor),
        ("PEX", "P07", _) | (_, _, "PEX_P07") =>
            parse_pex_p07(cursor),
        ("PEX", "P08", _) | (_, _, "PEX_P07") =>
            parse_pex_p07(cursor),
        ("PGL", "PC6", _) | (_, _, "PGL_PC6") =>
            parse_pgl_pc6(cursor),
        ("PGL", "PC7", _) | (_, _, "PGL_PC6") =>
            parse_pgl_pc6(cursor),
        ("PGL", "PC8", _) | (_, _, "PGL_PC6") =>
            parse_pgl_pc6(cursor),
        ("PMU", "B01", _) | (_, _, "PMU_B01") =>
            parse_pmu_b01(cursor),
        ("PMU", "B02", _) | (_, _, "PMU_B01") =>
            parse_pmu_b01(cursor),
        ("PMU", "B03", _) | (_, _, "PMU_B03") =>
            parse_pmu_b03(cursor),
        ("PMU", "B04", _) | (_, _, "PMU_B04") =>
            parse_pmu_b04(cursor),
        ("PMU", "B05", _) | (_, _, "PMU_B04") =>
            parse_pmu_b04(cursor),
        ("PMU", "B06", _) | (_, _, "PMU_B04") =>
            parse_pmu_b04(cursor),
        ("PMU", "B07", _) | (_, _, "PMU_B07") =>
            parse_pmu_b07(cursor),
        ("PMU", "B08", _) | (_, _, "PMU_B08") =>
            parse_pmu_b08(cursor),
        ("PPG", "PCG", _) | (_, _, "PPG_PCG") =>
            parse_ppg_pcg(cursor),
        ("PPG", "PCH", _) | (_, _, "PPG_PCG") =>
            parse_ppg_pcg(cursor),
        ("PPG", "PCJ", _) | (_, _, "PPG_PCG") =>
            parse_ppg_pcg(cursor),
        ("PPP", "PCB", _) | (_, _, "PPP_PCB") =>
            parse_ppp_pcb(cursor),
        ("PPP", "PCC", _) | (_, _, "PPP_PCB") =>
            parse_ppp_pcb(cursor),
        ("PPP", "PCD", _) | (_, _, "PPP_PCB") =>
            parse_ppp_pcb(cursor),
        ("PPR", "PC1", _) | (_, _, "PPR_PC1") =>
            parse_ppr_pc1(cursor),
        ("PPR", "PC2", _) | (_, _, "PPR_PC1") =>
            parse_ppr_pc1(cursor),
        ("PPR", "PC3", _) | (_, _, "PPR_PC1") =>
            parse_ppr_pc1(cursor),
        ("QBP", "E03", _) | (_, _, "QBP_E03") =>
            parse_qbp_e03(cursor),
        ("QBP", "E22", _) | (_, _, "QBP_E22") =>
            parse_qbp_e22(cursor),
        ("QBP", "O33", _) | (_, _, "QBP_O33") =>
            parse_qbp_o33(cursor),
        ("QBP", "Q33", _) | (_, _, "QBP_O33") =>
            parse_qbp_o33(cursor),
        ("QBP", "O34", _) | (_, _, "QBP_O34") =>
            parse_qbp_o34(cursor),
        ("QBP", "Q34", _) | (_, _, "QBP_O34") =>
            parse_qbp_o34(cursor),
        ("QBP", "Q11", _) | (_, _, "QBP_Q11") =>
            parse_qbp_q11(cursor),
        ("QBP", "Q31", _) | (_, _, "QBP_Q11") =>
            parse_qbp_q11(cursor),
        ("QBP", "Z87", _) | (_, _, "QBP_Q11") =>
            parse_qbp_q11(cursor),
        ("QBP", "Z89", _) | (_, _, "QBP_Q11") =>
            parse_qbp_q11(cursor),
        ("QBP", "Znn", _) | (_, _, "QBP_Q11") =>
            parse_qbp_q11(cursor),
        ("QBP", "Q13", _) | (_, _, "QBP_Q13") =>
            parse_qbp_q13(cursor),
        ("QBP", "Z99", _) | (_, _, "QBP_Q13") =>
            parse_qbp_q13(cursor),
        ("QBP", "Q15", _) | (_, _, "QBP_Q15") =>
            parse_qbp_q15(cursor),
        ("QBP", "Q21", _) | (_, _, "QBP_Q21") =>
            parse_qbp_q21(cursor),
        ("QBP", "Q22", _) | (_, _, "QBP_Q21") =>
            parse_qbp_q21(cursor),
        ("QBP", "Q23", _) | (_, _, "QBP_Q21") =>
            parse_qbp_q21(cursor),
        ("QBP", "Q24", _) | (_, _, "QBP_Q21") =>
            parse_qbp_q21(cursor),
        ("QBP", "Q25", _) | (_, _, "QBP_Q21") =>
            parse_qbp_q21(cursor),
        ("QBP", "Q32", _) | (_, _, "QBP_Q21") =>
            parse_qbp_q21(cursor),
        ("QBP", "Qnn", _) | (_, _, "QBP_Qnn") =>
            parse_qbp_qnn(cursor),
        ("QBP", "Z73", _) | (_, _, "QBP_Z73") =>
            parse_qbp_z73(cursor),
        ("QCN", "J01", _) | (_, _, "QCN_J01") =>
            parse_qcn_j01(cursor),
        ("QSX", "J02", _) | (_, _, "QCN_J01") =>
            parse_qcn_j01(cursor),
        ("QSB", "Q16", _) | (_, _, "QSB_Q16") =>
            parse_qsb_q16(cursor),
        ("QSB", "Z83", _) | (_, _, "QSB_Q16") =>
            parse_qsb_q16(cursor),
        ("QVR", "Q17", _) | (_, _, "QVR_Q17") =>
            parse_qvr_q17(cursor),
        ("RAS", "O17", _) | (_, _, "RAS_O17") =>
            parse_ras_o17(cursor),
        ("RCV", "O59", _) | (_, _, "RCV_O59") =>
            parse_rcv_o59(cursor),
        ("RDE", "O11", _) | (_, _, "RDE_O11") =>
            parse_rde_o11(cursor),
        ("RDE", "O25", _) | (_, _, "RDE_O11") =>
            parse_rde_o11(cursor),
        ("RDE", "O49", _) | (_, _, "RDE_O49") =>
            parse_rde_o49(cursor),
        ("RDR", "RDR", _) | (_, _, "RDR_RDR") =>
            parse_rdr_rdr(cursor),
        ("RDS", "O13", _) | (_, _, "RDS_O13") =>
            parse_rds_o13(cursor),
        ("RDY", "K15", _) | (_, _, "RDY_K15") =>
            parse_rdy_k15(cursor),
        ("RDY", "Z98", _) | (_, _, "RDY_K15") =>
            parse_rdy_k15(cursor),
        ("RDY", "Z80", _) | (_, _, "RDY_Z80") =>
            parse_rdy_z80(cursor),
        ("REF", "I12", _) | (_, _, "REF_I12") =>
            parse_ref_i12(cursor),
        ("REF", "I13", _) | (_, _, "REF_I12") =>
            parse_ref_i12(cursor),
        ("REF", "I14", _) | (_, _, "REF_I12") =>
            parse_ref_i12(cursor),
        ("REF", "I15", _) | (_, _, "REF_I12") =>
            parse_ref_i12(cursor),
        ("RGV", "O15", _) | (_, _, "RGV_O15") =>
            parse_rgv_o15(cursor),
        ("RPA", "I08", _) | (_, _, "RPA_I08") =>
            parse_rpa_i08(cursor),
        ("RPI", "I01", _) | (_, _, "RPI_I01") =>
            parse_rpi_i01(cursor),
        ("RPI", "I04", _) | (_, _, "RPI_I04") =>
            parse_rpi_i04(cursor),
        ("RPL", "I02", _) | (_, _, "RPL_I02") =>
            parse_rpl_i02(cursor),
        ("RPR", "I03", _) | (_, _, "RPR_I03") =>
            parse_rpr_i03(cursor),
        ("RQA", "I08", _) | (_, _, "RQA_I08") =>
            parse_rqa_i08(cursor),
        ("RQA", "I09", _) | (_, _, "RQA_I08") =>
            parse_rqa_i08(cursor),
        ("RQA", "I10", _) | (_, _, "RQA_I08") =>
            parse_rqa_i08(cursor),
        ("RQA", "I11", _) | (_, _, "RQA_I08") =>
            parse_rqa_i08(cursor),
        ("RQI", "I01", _) | (_, _, "RQI_I01") =>
            parse_rqi_i01(cursor),
        ("RQI", "I02", _) | (_, _, "RQI_I01") =>
            parse_rqi_i01(cursor),
        ("RQI", "I03", _) | (_, _, "RQI_I01") =>
            parse_rqi_i01(cursor),
        ("PIN", "I07", _) | (_, _, "RQI_I01") =>
            parse_rqi_i01(cursor),
        ("RQP", "I04", _) | (_, _, "RQP_I04") =>
            parse_rqp_i04(cursor),
        ("RRA", "O18", _) | (_, _, "RRA_O18") =>
            parse_rra_o18(cursor),
        ("RRD", "O14", _) | (_, _, "RRD_O14") =>
            parse_rrd_o14(cursor),
        ("RRE", "O12", _) | (_, _, "RRE_O12") =>
            parse_rre_o12(cursor),
        ("RRE", "O26", _) | (_, _, "RRE_O12") =>
            parse_rre_o12(cursor),
        ("RRE", "O50", _) | (_, _, "RRE_O50") =>
            parse_rre_o50(cursor),
        ("RRG", "O16", _) | (_, _, "RRG_O16") =>
            parse_rrg_o16(cursor),
        ("RRI", "I12", _) | (_, _, "RRI_I12") =>
            parse_rri_i12(cursor),
        ("RSP", "E03", _) | (_, _, "RSP_E03") =>
            parse_rsp_e03(cursor),
        ("RSP", "E22", _) | (_, _, "RSP_E22") =>
            parse_rsp_e22(cursor),
        ("RSP", "K11", _) | (_, _, "RSP_K11") =>
            parse_rsp_k11(cursor),
        ("RSP", "K21", _) | (_, _, "RSP_K21") =>
            parse_rsp_k21(cursor),
        ("RSP", "K22", _) | (_, _, "RSP_K22") =>
            parse_rsp_k22(cursor),
        ("RSP", "K23", _) | (_, _, "RSP_K23") =>
            parse_rsp_k23(cursor),
        ("RSP", "K24", _) | (_, _, "RSP_K23") =>
            parse_rsp_k23(cursor),
        ("RSP", "K25", _) | (_, _, "RSP_K25") =>
            parse_rsp_k25(cursor),
        ("RSP", "K31", _) | (_, _, "RSP_K31") =>
            parse_rsp_k31(cursor),
        ("RSP", "K32", _) | (_, _, "RSP_K32") =>
            parse_rsp_k32(cursor),
        ("RSP", "O33", _) | (_, _, "RSP_O33") =>
            parse_rsp_o33(cursor),
        ("RSP", "K33", _) | (_, _, "RSP_O33") =>
            parse_rsp_o33(cursor),
        ("RSP", "O34", _) | (_, _, "RSP_O34") =>
            parse_rsp_o34(cursor),
        ("RSP", "K34", _) | (_, _, "RSP_O34") =>
            parse_rsp_o34(cursor),
        ("RSP", "Z82", _) | (_, _, "RSP_Z82") =>
            parse_rsp_z82(cursor),
        ("RSP", "Z84", _) | (_, _, "RSP_Z84") =>
            parse_rsp_z84(cursor),
        ("RSP", "Z86", _) | (_, _, "RSP_Z86") =>
            parse_rsp_z86(cursor),
        ("RSP", "Z88", _) | (_, _, "RSP_Z88") =>
            parse_rsp_z88(cursor),
        ("RSP", "Z90", _) | (_, _, "RSP_Z90") =>
            parse_rsp_z90(cursor),
        ("RSP", "Znn", _) | (_, _, "RSP_Znn") =>
            parse_rsp_znn(cursor),
        ("RTB", "K13", _) | (_, _, "RTB_K13") =>
            parse_rtb_k13(cursor),
        ("RTB", "Z76", _) | (_, _, "RTB_K13") =>
            parse_rtb_k13(cursor),
        ("RTB", "Z78", _) | (_, _, "RTB_K13") =>
            parse_rtb_k13(cursor),
        ("RTB", "Z92", _) | (_, _, "RTB_K13") =>
            parse_rtb_k13(cursor),
        ("RTB", "Z94", _) | (_, _, "RTB_K13") =>
            parse_rtb_k13(cursor),
        ("RTB", "Z96", _) | (_, _, "RTB_K13") =>
            parse_rtb_k13(cursor),
        ("RTB", "Knn", _) | (_, _, "RTB_Knn") =>
            parse_rtb_knn(cursor),
        ("RTB", "Z74", _) | (_, _, "RTB_Z74") =>
            parse_rtb_z74(cursor),
        ("SDR", "S31", _) | (_, _, "SDR_S31") =>
            parse_sdr_s31(cursor),
        ("SDN", "S36", _) | (_, _, "SDR_S31") =>
            parse_sdr_s31(cursor),
        ("SDR", "S32", _) | (_, _, "SDR_S32") =>
            parse_sdr_s32(cursor),
        ("SCN", "S37", _) | (_, _, "SDR_S32") =>
            parse_sdr_s32(cursor),
        ("SMD", "S32", _) | (_, _, "SDR_S32") =>
            parse_sdr_s32(cursor),
        ("SIU", "S12", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S13", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S14", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S15", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S16", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S17", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S18", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S19", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S20", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S21", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S22", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S23", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S24", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S26", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SIU", "S27", _) | (_, _, "SIU_S12") =>
            parse_siu_s12(cursor),
        ("SLR", "S28", _) | (_, _, "SLR_S28") =>
            parse_slr_s28(cursor),
        ("SLR", "S29", _) | (_, _, "SLR_S28") =>
            parse_slr_s28(cursor),
        ("SLN", "S34", _) | (_, _, "SLR_S28") =>
            parse_slr_s28(cursor),
        ("SLN", "S35", _) | (_, _, "SLR_S28") =>
            parse_slr_s28(cursor),
        ("STI", "S30", _) | (_, _, "SLR_S28") =>
            parse_slr_s28(cursor),
        ("SRM", "S01", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S02", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S03", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S04", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S05", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S06", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S07", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S08", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S09", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S10", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRM", "S11", _) | (_, _, "SRM_S01") =>
            parse_srm_s01(cursor),
        ("SRR", "S01", _) | (_, _, "SRR_S01") =>
            parse_srr_s01(cursor),
        ("SSR", "U04", _) | (_, _, "SSR_U04") =>
            parse_ssr_u04(cursor),
        ("SSU", "U03", _) | (_, _, "SSU_U03") =>
            parse_ssu_u03(cursor),
        ("STC", "S33", _) | (_, _, "STC_S33") =>
            parse_stc_s33(cursor),
        ("TCU", "U10", _) | (_, _, "TCU_U10") =>
            parse_tcu_u10(cursor),
        ("TCR", "U11", _) | (_, _, "TCU_U10") =>
            parse_tcu_u10(cursor),
        ("UDM", "Q05", _) | (_, _, "UDM_Q05") =>
            parse_udm_q05(cursor),
        ("VXU", "V04", _) | (_, _, "VXU_V04") =>
            parse_vxu_v04(cursor),
        _ => Err(ParseError::UnknownMessageStructure),
    }
}