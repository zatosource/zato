from __future__ import annotations


class TestMessageClassImports:
    """Test that all message classes can be imported directly."""

    def test_import_ack(self):
        from zato.hl7v2.v2_9.messages import ACK
        assert ACK._structure_id == "ACK"

    def test_import_adr_a19(self):
        from zato.hl7v2.v2_9.messages import ADR_A19
        assert ADR_A19._structure_id == "ADR_A19"

    def test_import_adt_a01(self):
        from zato.hl7v2.v2_9.messages import ADT_A01
        assert ADT_A01._structure_id == "ADT_A01"

    def test_import_adt_a02(self):
        from zato.hl7v2.v2_9.messages import ADT_A02
        assert ADT_A02._structure_id == "ADT_A02"

    def test_import_adt_a03(self):
        from zato.hl7v2.v2_9.messages import ADT_A03
        assert ADT_A03._structure_id == "ADT_A03"

    def test_import_adt_a05(self):
        from zato.hl7v2.v2_9.messages import ADT_A05
        assert ADT_A05._structure_id == "ADT_A05"

    def test_import_adt_a06(self):
        from zato.hl7v2.v2_9.messages import ADT_A06
        assert ADT_A06._structure_id == "ADT_A06"

    def test_import_adt_a09(self):
        from zato.hl7v2.v2_9.messages import ADT_A09
        assert ADT_A09._structure_id == "ADT_A09"

    def test_import_adt_a12(self):
        from zato.hl7v2.v2_9.messages import ADT_A12
        assert ADT_A12._structure_id == "ADT_A12"

    def test_import_adt_a15(self):
        from zato.hl7v2.v2_9.messages import ADT_A15
        assert ADT_A15._structure_id == "ADT_A15"

    def test_import_adt_a16(self):
        from zato.hl7v2.v2_9.messages import ADT_A16
        assert ADT_A16._structure_id == "ADT_A16"

    def test_import_adt_a17(self):
        from zato.hl7v2.v2_9.messages import ADT_A17
        assert ADT_A17._structure_id == "ADT_A17"

    def test_import_adt_a20(self):
        from zato.hl7v2.v2_9.messages import ADT_A20
        assert ADT_A20._structure_id == "ADT_A20"

    def test_import_adt_a21(self):
        from zato.hl7v2.v2_9.messages import ADT_A21
        assert ADT_A21._structure_id == "ADT_A21"

    def test_import_adt_a24(self):
        from zato.hl7v2.v2_9.messages import ADT_A24
        assert ADT_A24._structure_id == "ADT_A24"

    def test_import_adt_a30(self):
        from zato.hl7v2.v2_9.messages import ADT_A30
        assert ADT_A30._structure_id == "ADT_A30"

    def test_import_adt_a37(self):
        from zato.hl7v2.v2_9.messages import ADT_A37
        assert ADT_A37._structure_id == "ADT_A37"

    def test_import_adt_a38(self):
        from zato.hl7v2.v2_9.messages import ADT_A38
        assert ADT_A38._structure_id == "ADT_A38"

    def test_import_adt_a39(self):
        from zato.hl7v2.v2_9.messages import ADT_A39
        assert ADT_A39._structure_id == "ADT_A39"

    def test_import_adt_a43(self):
        from zato.hl7v2.v2_9.messages import ADT_A43
        assert ADT_A43._structure_id == "ADT_A43"

    def test_import_adt_a44(self):
        from zato.hl7v2.v2_9.messages import ADT_A44
        assert ADT_A44._structure_id == "ADT_A44"

    def test_import_adt_a45(self):
        from zato.hl7v2.v2_9.messages import ADT_A45
        assert ADT_A45._structure_id == "ADT_A45"

    def test_import_adt_a50(self):
        from zato.hl7v2.v2_9.messages import ADT_A50
        assert ADT_A50._structure_id == "ADT_A50"

    def test_import_adt_a52(self):
        from zato.hl7v2.v2_9.messages import ADT_A52
        assert ADT_A52._structure_id == "ADT_A52"

    def test_import_adt_a54(self):
        from zato.hl7v2.v2_9.messages import ADT_A54
        assert ADT_A54._structure_id == "ADT_A54"

    def test_import_adt_a60(self):
        from zato.hl7v2.v2_9.messages import ADT_A60
        assert ADT_A60._structure_id == "ADT_A60"

    def test_import_adt_a61(self):
        from zato.hl7v2.v2_9.messages import ADT_A61
        assert ADT_A61._structure_id == "ADT_A61"

    def test_import_bar_p01(self):
        from zato.hl7v2.v2_9.messages import BAR_P01
        assert BAR_P01._structure_id == "BAR_P01"

    def test_import_bar_p02(self):
        from zato.hl7v2.v2_9.messages import BAR_P02
        assert BAR_P02._structure_id == "BAR_P02"

    def test_import_bar_p05(self):
        from zato.hl7v2.v2_9.messages import BAR_P05
        assert BAR_P05._structure_id == "BAR_P05"

    def test_import_bar_p06(self):
        from zato.hl7v2.v2_9.messages import BAR_P06
        assert BAR_P06._structure_id == "BAR_P06"

    def test_import_bar_p10(self):
        from zato.hl7v2.v2_9.messages import BAR_P10
        assert BAR_P10._structure_id == "BAR_P10"

    def test_import_bar_p12(self):
        from zato.hl7v2.v2_9.messages import BAR_P12
        assert BAR_P12._structure_id == "BAR_P12"

    def test_import_bps_o29(self):
        from zato.hl7v2.v2_9.messages import BPS_O29
        assert BPS_O29._structure_id == "BPS_O29"

    def test_import_brp_o30(self):
        from zato.hl7v2.v2_9.messages import BRP_O30
        assert BRP_O30._structure_id == "BRP_O30"

    def test_import_brt_o32(self):
        from zato.hl7v2.v2_9.messages import BRT_O32
        assert BRT_O32._structure_id == "BRT_O32"

    def test_import_bts_o31(self):
        from zato.hl7v2.v2_9.messages import BTS_O31
        assert BTS_O31._structure_id == "BTS_O31"

    def test_import_ccf_i22(self):
        from zato.hl7v2.v2_9.messages import CCF_I22
        assert CCF_I22._structure_id == "CCF_I22"

    def test_import_cci_i22(self):
        from zato.hl7v2.v2_9.messages import CCI_I22
        assert CCI_I22._structure_id == "CCI_I22"

    def test_import_ccm_i21(self):
        from zato.hl7v2.v2_9.messages import CCM_I21
        assert CCM_I21._structure_id == "CCM_I21"

    def test_import_ccq_i19(self):
        from zato.hl7v2.v2_9.messages import CCQ_I19
        assert CCQ_I19._structure_id == "CCQ_I19"

    def test_import_ccr_i16(self):
        from zato.hl7v2.v2_9.messages import CCR_I16
        assert CCR_I16._structure_id == "CCR_I16"

    def test_import_ccu_i20(self):
        from zato.hl7v2.v2_9.messages import CCU_I20
        assert CCU_I20._structure_id == "CCU_I20"

    def test_import_cqu_i19(self):
        from zato.hl7v2.v2_9.messages import CQU_I19
        assert CQU_I19._structure_id == "CQU_I19"

    def test_import_crm_c01(self):
        from zato.hl7v2.v2_9.messages import CRM_C01
        assert CRM_C01._structure_id == "CRM_C01"

    def test_import_csu_c09(self):
        from zato.hl7v2.v2_9.messages import CSU_C09
        assert CSU_C09._structure_id == "CSU_C09"

    def test_import_dbc_o41(self):
        from zato.hl7v2.v2_9.messages import DBC_O41
        assert DBC_O41._structure_id == "DBC_O41"

    def test_import_dbc_o42(self):
        from zato.hl7v2.v2_9.messages import DBC_O42
        assert DBC_O42._structure_id == "DBC_O42"

    def test_import_del_o46(self):
        from zato.hl7v2.v2_9.messages import DEL_O46
        assert DEL_O46._structure_id == "DEL_O46"

    def test_import_deo_o45(self):
        from zato.hl7v2.v2_9.messages import DEO_O45
        assert DEO_O45._structure_id == "DEO_O45"

    def test_import_der_o44(self):
        from zato.hl7v2.v2_9.messages import DER_O44
        assert DER_O44._structure_id == "DER_O44"

    def test_import_dft_p03(self):
        from zato.hl7v2.v2_9.messages import DFT_P03
        assert DFT_P03._structure_id == "DFT_P03"

    def test_import_dft_p11(self):
        from zato.hl7v2.v2_9.messages import DFT_P11
        assert DFT_P11._structure_id == "DFT_P11"

    def test_import_dpr_o48(self):
        from zato.hl7v2.v2_9.messages import DPR_O48
        assert DPR_O48._structure_id == "DPR_O48"

    def test_import_drc_o47(self):
        from zato.hl7v2.v2_9.messages import DRC_O47
        assert DRC_O47._structure_id == "DRC_O47"

    def test_import_drg_o43(self):
        from zato.hl7v2.v2_9.messages import DRG_O43
        assert DRG_O43._structure_id == "DRG_O43"

    def test_import_eac_u07(self):
        from zato.hl7v2.v2_9.messages import EAC_U07
        assert EAC_U07._structure_id == "EAC_U07"

    def test_import_ean_u09(self):
        from zato.hl7v2.v2_9.messages import EAN_U09
        assert EAN_U09._structure_id == "EAN_U09"

    def test_import_ear_u08(self):
        from zato.hl7v2.v2_9.messages import EAR_U08
        assert EAR_U08._structure_id == "EAR_U08"

    def test_import_ehc_e01(self):
        from zato.hl7v2.v2_9.messages import EHC_E01
        assert EHC_E01._structure_id == "EHC_E01"

    def test_import_ehc_e02(self):
        from zato.hl7v2.v2_9.messages import EHC_E02
        assert EHC_E02._structure_id == "EHC_E02"

    def test_import_ehc_e04(self):
        from zato.hl7v2.v2_9.messages import EHC_E04
        assert EHC_E04._structure_id == "EHC_E04"

    def test_import_ehc_e10(self):
        from zato.hl7v2.v2_9.messages import EHC_E10
        assert EHC_E10._structure_id == "EHC_E10"

    def test_import_ehc_e12(self):
        from zato.hl7v2.v2_9.messages import EHC_E12
        assert EHC_E12._structure_id == "EHC_E12"

    def test_import_ehc_e13(self):
        from zato.hl7v2.v2_9.messages import EHC_E13
        assert EHC_E13._structure_id == "EHC_E13"

    def test_import_ehc_e15(self):
        from zato.hl7v2.v2_9.messages import EHC_E15
        assert EHC_E15._structure_id == "EHC_E15"

    def test_import_ehc_e20(self):
        from zato.hl7v2.v2_9.messages import EHC_E20
        assert EHC_E20._structure_id == "EHC_E20"

    def test_import_ehc_e21(self):
        from zato.hl7v2.v2_9.messages import EHC_E21
        assert EHC_E21._structure_id == "EHC_E21"

    def test_import_ehc_e24(self):
        from zato.hl7v2.v2_9.messages import EHC_E24
        assert EHC_E24._structure_id == "EHC_E24"

    def test_import_esr_u02(self):
        from zato.hl7v2.v2_9.messages import ESR_U02
        assert ESR_U02._structure_id == "ESR_U02"

    def test_import_esu_u01(self):
        from zato.hl7v2.v2_9.messages import ESU_U01
        assert ESU_U01._structure_id == "ESU_U01"

    def test_import_inr_u06(self):
        from zato.hl7v2.v2_9.messages import INR_U06
        assert INR_U06._structure_id == "INR_U06"

    def test_import_inr_u14(self):
        from zato.hl7v2.v2_9.messages import INR_U14
        assert INR_U14._structure_id == "INR_U14"

    def test_import_inu_u05(self):
        from zato.hl7v2.v2_9.messages import INU_U05
        assert INU_U05._structure_id == "INU_U05"

    def test_import_lsu_u12(self):
        from zato.hl7v2.v2_9.messages import LSU_U12
        assert LSU_U12._structure_id == "LSU_U12"

    def test_import_mdm_t01(self):
        from zato.hl7v2.v2_9.messages import MDM_T01
        assert MDM_T01._structure_id == "MDM_T01"

    def test_import_mdm_t02(self):
        from zato.hl7v2.v2_9.messages import MDM_T02
        assert MDM_T02._structure_id == "MDM_T02"

    def test_import_mfk_m01(self):
        from zato.hl7v2.v2_9.messages import MFK_M01
        assert MFK_M01._structure_id == "MFK_M01"

    def test_import_mfn_m02(self):
        from zato.hl7v2.v2_9.messages import MFN_M02
        assert MFN_M02._structure_id == "MFN_M02"

    def test_import_mfn_m04(self):
        from zato.hl7v2.v2_9.messages import MFN_M04
        assert MFN_M04._structure_id == "MFN_M04"

    def test_import_mfn_m05(self):
        from zato.hl7v2.v2_9.messages import MFN_M05
        assert MFN_M05._structure_id == "MFN_M05"

    def test_import_mfn_m06(self):
        from zato.hl7v2.v2_9.messages import MFN_M06
        assert MFN_M06._structure_id == "MFN_M06"

    def test_import_mfn_m07(self):
        from zato.hl7v2.v2_9.messages import MFN_M07
        assert MFN_M07._structure_id == "MFN_M07"

    def test_import_mfn_m08(self):
        from zato.hl7v2.v2_9.messages import MFN_M08
        assert MFN_M08._structure_id == "MFN_M08"

    def test_import_mfn_m09(self):
        from zato.hl7v2.v2_9.messages import MFN_M09
        assert MFN_M09._structure_id == "MFN_M09"

    def test_import_mfn_m10(self):
        from zato.hl7v2.v2_9.messages import MFN_M10
        assert MFN_M10._structure_id == "MFN_M10"

    def test_import_mfn_m11(self):
        from zato.hl7v2.v2_9.messages import MFN_M11
        assert MFN_M11._structure_id == "MFN_M11"

    def test_import_mfn_m12(self):
        from zato.hl7v2.v2_9.messages import MFN_M12
        assert MFN_M12._structure_id == "MFN_M12"

    def test_import_mfn_m13(self):
        from zato.hl7v2.v2_9.messages import MFN_M13
        assert MFN_M13._structure_id == "MFN_M13"

    def test_import_mfn_m15(self):
        from zato.hl7v2.v2_9.messages import MFN_M15
        assert MFN_M15._structure_id == "MFN_M15"

    def test_import_mfn_m16(self):
        from zato.hl7v2.v2_9.messages import MFN_M16
        assert MFN_M16._structure_id == "MFN_M16"

    def test_import_mfn_m17(self):
        from zato.hl7v2.v2_9.messages import MFN_M17
        assert MFN_M17._structure_id == "MFN_M17"

    def test_import_mfn_m18(self):
        from zato.hl7v2.v2_9.messages import MFN_M18
        assert MFN_M18._structure_id == "MFN_M18"

    def test_import_mfn_m19(self):
        from zato.hl7v2.v2_9.messages import MFN_M19
        assert MFN_M19._structure_id == "MFN_M19"

    def test_import_mfn_znn(self):
        from zato.hl7v2.v2_9.messages import MFN_Znn
        assert MFN_Znn._structure_id == "MFN_Znn"

    def test_import_nmd_n02(self):
        from zato.hl7v2.v2_9.messages import NMD_N02
        assert NMD_N02._structure_id == "NMD_N02"

    def test_import_omb_o27(self):
        from zato.hl7v2.v2_9.messages import OMB_O27
        assert OMB_O27._structure_id == "OMB_O27"

    def test_import_omd_o03(self):
        from zato.hl7v2.v2_9.messages import OMD_O03
        assert OMD_O03._structure_id == "OMD_O03"

    def test_import_omg_o19(self):
        from zato.hl7v2.v2_9.messages import OMG_O19
        assert OMG_O19._structure_id == "OMG_O19"

    def test_import_omi_o23(self):
        from zato.hl7v2.v2_9.messages import OMI_O23
        assert OMI_O23._structure_id == "OMI_O23"

    def test_import_oml_o21(self):
        from zato.hl7v2.v2_9.messages import OML_O21
        assert OML_O21._structure_id == "OML_O21"

    def test_import_oml_o33(self):
        from zato.hl7v2.v2_9.messages import OML_O33
        assert OML_O33._structure_id == "OML_O33"

    def test_import_oml_o35(self):
        from zato.hl7v2.v2_9.messages import OML_O35
        assert OML_O35._structure_id == "OML_O35"

    def test_import_oml_o39(self):
        from zato.hl7v2.v2_9.messages import OML_O39
        assert OML_O39._structure_id == "OML_O39"

    def test_import_oml_o59(self):
        from zato.hl7v2.v2_9.messages import OML_O59
        assert OML_O59._structure_id == "OML_O59"

    def test_import_omn_o07(self):
        from zato.hl7v2.v2_9.messages import OMN_O07
        assert OMN_O07._structure_id == "OMN_O07"

    def test_import_omp_o09(self):
        from zato.hl7v2.v2_9.messages import OMP_O09
        assert OMP_O09._structure_id == "OMP_O09"

    def test_import_omq_o57(self):
        from zato.hl7v2.v2_9.messages import OMQ_O57
        assert OMQ_O57._structure_id == "OMQ_O57"

    def test_import_oms_o05(self):
        from zato.hl7v2.v2_9.messages import OMS_O05
        assert OMS_O05._structure_id == "OMS_O05"

    def test_import_opl_o37(self):
        from zato.hl7v2.v2_9.messages import OPL_O37
        assert OPL_O37._structure_id == "OPL_O37"

    def test_import_opr_o38(self):
        from zato.hl7v2.v2_9.messages import OPR_O38
        assert OPR_O38._structure_id == "OPR_O38"

    def test_import_opu_r25(self):
        from zato.hl7v2.v2_9.messages import OPU_R25
        assert OPU_R25._structure_id == "OPU_R25"

    def test_import_ora_r33(self):
        from zato.hl7v2.v2_9.messages import ORA_R33
        assert ORA_R33._structure_id == "ORA_R33"

    def test_import_ora_r41(self):
        from zato.hl7v2.v2_9.messages import ORA_R41
        assert ORA_R41._structure_id == "ORA_R41"

    def test_import_orb_o28(self):
        from zato.hl7v2.v2_9.messages import ORB_O28
        assert ORB_O28._structure_id == "ORB_O28"

    def test_import_ord_o04(self):
        from zato.hl7v2.v2_9.messages import ORD_O04
        assert ORD_O04._structure_id == "ORD_O04"

    def test_import_org_o20(self):
        from zato.hl7v2.v2_9.messages import ORG_O20
        assert ORG_O20._structure_id == "ORG_O20"

    def test_import_ori_o24(self):
        from zato.hl7v2.v2_9.messages import ORI_O24
        assert ORI_O24._structure_id == "ORI_O24"

    def test_import_orl_o22(self):
        from zato.hl7v2.v2_9.messages import ORL_O22
        assert ORL_O22._structure_id == "ORL_O22"

    def test_import_orl_o34(self):
        from zato.hl7v2.v2_9.messages import ORL_O34
        assert ORL_O34._structure_id == "ORL_O34"

    def test_import_orl_o36(self):
        from zato.hl7v2.v2_9.messages import ORL_O36
        assert ORL_O36._structure_id == "ORL_O36"

    def test_import_orl_o40(self):
        from zato.hl7v2.v2_9.messages import ORL_O40
        assert ORL_O40._structure_id == "ORL_O40"

    def test_import_orl_o53(self):
        from zato.hl7v2.v2_9.messages import ORL_O53
        assert ORL_O53._structure_id == "ORL_O53"

    def test_import_orl_o54(self):
        from zato.hl7v2.v2_9.messages import ORL_O54
        assert ORL_O54._structure_id == "ORL_O54"

    def test_import_orl_o55(self):
        from zato.hl7v2.v2_9.messages import ORL_O55
        assert ORL_O55._structure_id == "ORL_O55"

    def test_import_orl_o56(self):
        from zato.hl7v2.v2_9.messages import ORL_O56
        assert ORL_O56._structure_id == "ORL_O56"

    def test_import_orm_o01(self):
        from zato.hl7v2.v2_9.messages import ORM_O01
        assert ORM_O01._structure_id == "ORM_O01"

    def test_import_orn_o08(self):
        from zato.hl7v2.v2_9.messages import ORN_O08
        assert ORN_O08._structure_id == "ORN_O08"

    def test_import_orp_o10(self):
        from zato.hl7v2.v2_9.messages import ORP_O10
        assert ORP_O10._structure_id == "ORP_O10"

    def test_import_ors_o06(self):
        from zato.hl7v2.v2_9.messages import ORS_O06
        assert ORS_O06._structure_id == "ORS_O06"

    def test_import_oru_r01(self):
        from zato.hl7v2.v2_9.messages import ORU_R01
        assert ORU_R01._structure_id == "ORU_R01"

    def test_import_oru_r30(self):
        from zato.hl7v2.v2_9.messages import ORU_R30
        assert ORU_R30._structure_id == "ORU_R30"

    def test_import_orx_o58(self):
        from zato.hl7v2.v2_9.messages import ORX_O58
        assert ORX_O58._structure_id == "ORX_O58"

    def test_import_osm_r26(self):
        from zato.hl7v2.v2_9.messages import OSM_R26
        assert OSM_R26._structure_id == "OSM_R26"

    def test_import_osu_o51(self):
        from zato.hl7v2.v2_9.messages import OSU_O51
        assert OSU_O51._structure_id == "OSU_O51"

    def test_import_osu_o52(self):
        from zato.hl7v2.v2_9.messages import OSU_O52
        assert OSU_O52._structure_id == "OSU_O52"

    def test_import_oul_r22(self):
        from zato.hl7v2.v2_9.messages import OUL_R22
        assert OUL_R22._structure_id == "OUL_R22"

    def test_import_oul_r23(self):
        from zato.hl7v2.v2_9.messages import OUL_R23
        assert OUL_R23._structure_id == "OUL_R23"

    def test_import_oul_r24(self):
        from zato.hl7v2.v2_9.messages import OUL_R24
        assert OUL_R24._structure_id == "OUL_R24"

    def test_import_pex_p07(self):
        from zato.hl7v2.v2_9.messages import PEX_P07
        assert PEX_P07._structure_id == "PEX_P07"

    def test_import_pgl_pc6(self):
        from zato.hl7v2.v2_9.messages import PGL_PC6
        assert PGL_PC6._structure_id == "PGL_PC6"

    def test_import_pmu_b01(self):
        from zato.hl7v2.v2_9.messages import PMU_B01
        assert PMU_B01._structure_id == "PMU_B01"

    def test_import_pmu_b03(self):
        from zato.hl7v2.v2_9.messages import PMU_B03
        assert PMU_B03._structure_id == "PMU_B03"

    def test_import_pmu_b04(self):
        from zato.hl7v2.v2_9.messages import PMU_B04
        assert PMU_B04._structure_id == "PMU_B04"

    def test_import_pmu_b07(self):
        from zato.hl7v2.v2_9.messages import PMU_B07
        assert PMU_B07._structure_id == "PMU_B07"

    def test_import_pmu_b08(self):
        from zato.hl7v2.v2_9.messages import PMU_B08
        assert PMU_B08._structure_id == "PMU_B08"

    def test_import_ppg_pcg(self):
        from zato.hl7v2.v2_9.messages import PPG_PCG
        assert PPG_PCG._structure_id == "PPG_PCG"

    def test_import_ppp_pcb(self):
        from zato.hl7v2.v2_9.messages import PPP_PCB
        assert PPP_PCB._structure_id == "PPP_PCB"

    def test_import_ppr_pc1(self):
        from zato.hl7v2.v2_9.messages import PPR_PC1
        assert PPR_PC1._structure_id == "PPR_PC1"

    def test_import_qbp_e03(self):
        from zato.hl7v2.v2_9.messages import QBP_E03
        assert QBP_E03._structure_id == "QBP_E03"

    def test_import_qbp_e22(self):
        from zato.hl7v2.v2_9.messages import QBP_E22
        assert QBP_E22._structure_id == "QBP_E22"

    def test_import_qbp_o33(self):
        from zato.hl7v2.v2_9.messages import QBP_O33
        assert QBP_O33._structure_id == "QBP_O33"

    def test_import_qbp_o34(self):
        from zato.hl7v2.v2_9.messages import QBP_O34
        assert QBP_O34._structure_id == "QBP_O34"

    def test_import_qbp_q11(self):
        from zato.hl7v2.v2_9.messages import QBP_Q11
        assert QBP_Q11._structure_id == "QBP_Q11"

    def test_import_qbp_q13(self):
        from zato.hl7v2.v2_9.messages import QBP_Q13
        assert QBP_Q13._structure_id == "QBP_Q13"

    def test_import_qbp_q15(self):
        from zato.hl7v2.v2_9.messages import QBP_Q15
        assert QBP_Q15._structure_id == "QBP_Q15"

    def test_import_qbp_q21(self):
        from zato.hl7v2.v2_9.messages import QBP_Q21
        assert QBP_Q21._structure_id == "QBP_Q21"

    def test_import_qbp_qnn(self):
        from zato.hl7v2.v2_9.messages import QBP_Qnn
        assert QBP_Qnn._structure_id == "QBP_Qnn"

    def test_import_qbp_z73(self):
        from zato.hl7v2.v2_9.messages import QBP_Z73
        assert QBP_Z73._structure_id == "QBP_Z73"

    def test_import_qcn_j01(self):
        from zato.hl7v2.v2_9.messages import QCN_J01
        assert QCN_J01._structure_id == "QCN_J01"

    def test_import_qry_a19(self):
        from zato.hl7v2.v2_9.messages import QRY_A19
        assert QRY_A19._structure_id == "QRY_A19"

    def test_import_qsb_q16(self):
        from zato.hl7v2.v2_9.messages import QSB_Q16
        assert QSB_Q16._structure_id == "QSB_Q16"

    def test_import_qvr_q17(self):
        from zato.hl7v2.v2_9.messages import QVR_Q17
        assert QVR_Q17._structure_id == "QVR_Q17"

    def test_import_ras_o17(self):
        from zato.hl7v2.v2_9.messages import RAS_O17
        assert RAS_O17._structure_id == "RAS_O17"

    def test_import_rcv_o59(self):
        from zato.hl7v2.v2_9.messages import RCV_O59
        assert RCV_O59._structure_id == "RCV_O59"

    def test_import_rde_o11(self):
        from zato.hl7v2.v2_9.messages import RDE_O11
        assert RDE_O11._structure_id == "RDE_O11"

    def test_import_rde_o49(self):
        from zato.hl7v2.v2_9.messages import RDE_O49
        assert RDE_O49._structure_id == "RDE_O49"

    def test_import_rdr_rdr(self):
        from zato.hl7v2.v2_9.messages import RDR_RDR
        assert RDR_RDR._structure_id == "RDR_RDR"

    def test_import_rds_o13(self):
        from zato.hl7v2.v2_9.messages import RDS_O13
        assert RDS_O13._structure_id == "RDS_O13"

    def test_import_rdy_k15(self):
        from zato.hl7v2.v2_9.messages import RDY_K15
        assert RDY_K15._structure_id == "RDY_K15"

    def test_import_rdy_z80(self):
        from zato.hl7v2.v2_9.messages import RDY_Z80
        assert RDY_Z80._structure_id == "RDY_Z80"

    def test_import_ref_i12(self):
        from zato.hl7v2.v2_9.messages import REF_I12
        assert REF_I12._structure_id == "REF_I12"

    def test_import_rgv_o15(self):
        from zato.hl7v2.v2_9.messages import RGV_O15
        assert RGV_O15._structure_id == "RGV_O15"

    def test_import_rpa_i08(self):
        from zato.hl7v2.v2_9.messages import RPA_I08
        assert RPA_I08._structure_id == "RPA_I08"

    def test_import_rpi_i01(self):
        from zato.hl7v2.v2_9.messages import RPI_I01
        assert RPI_I01._structure_id == "RPI_I01"

    def test_import_rpi_i04(self):
        from zato.hl7v2.v2_9.messages import RPI_I04
        assert RPI_I04._structure_id == "RPI_I04"

    def test_import_rpl_i02(self):
        from zato.hl7v2.v2_9.messages import RPL_I02
        assert RPL_I02._structure_id == "RPL_I02"

    def test_import_rpr_i03(self):
        from zato.hl7v2.v2_9.messages import RPR_I03
        assert RPR_I03._structure_id == "RPR_I03"

    def test_import_rqa_i08(self):
        from zato.hl7v2.v2_9.messages import RQA_I08
        assert RQA_I08._structure_id == "RQA_I08"

    def test_import_rqi_i01(self):
        from zato.hl7v2.v2_9.messages import RQI_I01
        assert RQI_I01._structure_id == "RQI_I01"

    def test_import_rqp_i04(self):
        from zato.hl7v2.v2_9.messages import RQP_I04
        assert RQP_I04._structure_id == "RQP_I04"

    def test_import_rra_o18(self):
        from zato.hl7v2.v2_9.messages import RRA_O18
        assert RRA_O18._structure_id == "RRA_O18"

    def test_import_rrd_o14(self):
        from zato.hl7v2.v2_9.messages import RRD_O14
        assert RRD_O14._structure_id == "RRD_O14"

    def test_import_rre_o12(self):
        from zato.hl7v2.v2_9.messages import RRE_O12
        assert RRE_O12._structure_id == "RRE_O12"

    def test_import_rre_o50(self):
        from zato.hl7v2.v2_9.messages import RRE_O50
        assert RRE_O50._structure_id == "RRE_O50"

    def test_import_rrg_o16(self):
        from zato.hl7v2.v2_9.messages import RRG_O16
        assert RRG_O16._structure_id == "RRG_O16"

    def test_import_rri_i12(self):
        from zato.hl7v2.v2_9.messages import RRI_I12
        assert RRI_I12._structure_id == "RRI_I12"

    def test_import_rsp_e03(self):
        from zato.hl7v2.v2_9.messages import RSP_E03
        assert RSP_E03._structure_id == "RSP_E03"

    def test_import_rsp_e22(self):
        from zato.hl7v2.v2_9.messages import RSP_E22
        assert RSP_E22._structure_id == "RSP_E22"

    def test_import_rsp_k11(self):
        from zato.hl7v2.v2_9.messages import RSP_K11
        assert RSP_K11._structure_id == "RSP_K11"

    def test_import_rsp_k21(self):
        from zato.hl7v2.v2_9.messages import RSP_K21
        assert RSP_K21._structure_id == "RSP_K21"

    def test_import_rsp_k22(self):
        from zato.hl7v2.v2_9.messages import RSP_K22
        assert RSP_K22._structure_id == "RSP_K22"

    def test_import_rsp_k23(self):
        from zato.hl7v2.v2_9.messages import RSP_K23
        assert RSP_K23._structure_id == "RSP_K23"

    def test_import_rsp_k25(self):
        from zato.hl7v2.v2_9.messages import RSP_K25
        assert RSP_K25._structure_id == "RSP_K25"

    def test_import_rsp_k31(self):
        from zato.hl7v2.v2_9.messages import RSP_K31
        assert RSP_K31._structure_id == "RSP_K31"

    def test_import_rsp_k32(self):
        from zato.hl7v2.v2_9.messages import RSP_K32
        assert RSP_K32._structure_id == "RSP_K32"

    def test_import_rsp_o33(self):
        from zato.hl7v2.v2_9.messages import RSP_O33
        assert RSP_O33._structure_id == "RSP_O33"

    def test_import_rsp_o34(self):
        from zato.hl7v2.v2_9.messages import RSP_O34
        assert RSP_O34._structure_id == "RSP_O34"

    def test_import_rsp_z82(self):
        from zato.hl7v2.v2_9.messages import RSP_Z82
        assert RSP_Z82._structure_id == "RSP_Z82"

    def test_import_rsp_z84(self):
        from zato.hl7v2.v2_9.messages import RSP_Z84
        assert RSP_Z84._structure_id == "RSP_Z84"

    def test_import_rsp_z86(self):
        from zato.hl7v2.v2_9.messages import RSP_Z86
        assert RSP_Z86._structure_id == "RSP_Z86"

    def test_import_rsp_z88(self):
        from zato.hl7v2.v2_9.messages import RSP_Z88
        assert RSP_Z88._structure_id == "RSP_Z88"

    def test_import_rsp_z90(self):
        from zato.hl7v2.v2_9.messages import RSP_Z90
        assert RSP_Z90._structure_id == "RSP_Z90"

    def test_import_rsp_znn(self):
        from zato.hl7v2.v2_9.messages import RSP_Znn
        assert RSP_Znn._structure_id == "RSP_Znn"

    def test_import_rtb_k13(self):
        from zato.hl7v2.v2_9.messages import RTB_K13
        assert RTB_K13._structure_id == "RTB_K13"

    def test_import_rtb_knn(self):
        from zato.hl7v2.v2_9.messages import RTB_Knn
        assert RTB_Knn._structure_id == "RTB_Knn"

    def test_import_rtb_z74(self):
        from zato.hl7v2.v2_9.messages import RTB_Z74
        assert RTB_Z74._structure_id == "RTB_Z74"

    def test_import_sdr_s31(self):
        from zato.hl7v2.v2_9.messages import SDR_S31
        assert SDR_S31._structure_id == "SDR_S31"

    def test_import_sdr_s32(self):
        from zato.hl7v2.v2_9.messages import SDR_S32
        assert SDR_S32._structure_id == "SDR_S32"

    def test_import_siu_s12(self):
        from zato.hl7v2.v2_9.messages import SIU_S12
        assert SIU_S12._structure_id == "SIU_S12"

    def test_import_slr_s28(self):
        from zato.hl7v2.v2_9.messages import SLR_S28
        assert SLR_S28._structure_id == "SLR_S28"

    def test_import_srm_s01(self):
        from zato.hl7v2.v2_9.messages import SRM_S01
        assert SRM_S01._structure_id == "SRM_S01"

    def test_import_srr_s01(self):
        from zato.hl7v2.v2_9.messages import SRR_S01
        assert SRR_S01._structure_id == "SRR_S01"

    def test_import_ssr_u04(self):
        from zato.hl7v2.v2_9.messages import SSR_U04
        assert SSR_U04._structure_id == "SSR_U04"

    def test_import_ssu_u03(self):
        from zato.hl7v2.v2_9.messages import SSU_U03
        assert SSU_U03._structure_id == "SSU_U03"

    def test_import_stc_s33(self):
        from zato.hl7v2.v2_9.messages import STC_S33
        assert STC_S33._structure_id == "STC_S33"

    def test_import_tcu_u10(self):
        from zato.hl7v2.v2_9.messages import TCU_U10
        assert TCU_U10._structure_id == "TCU_U10"

    def test_import_udm_q05(self):
        from zato.hl7v2.v2_9.messages import UDM_Q05
        assert UDM_Q05._structure_id == "UDM_Q05"

    def test_import_vxu_v04(self):
        from zato.hl7v2.v2_9.messages import VXU_V04
        assert VXU_V04._structure_id == "VXU_V04"
