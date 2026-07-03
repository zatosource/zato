from __future__ import annotations

import json
from zato.hl7v2.v2_9.messages import (
    ACK,
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


class TestMessageSerialization:
    """Test serialization methods for all message classes."""

    def test_ack_to_dict(self):
        msg = ACK()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ACK"

    def test_ack_to_json(self):
        msg = ACK()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ACK"

    def test_adt_a01_to_dict(self):
        msg = ADT_A01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A01"

    def test_adt_a01_to_json(self):
        msg = ADT_A01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A01"

    def test_adt_a02_to_dict(self):
        msg = ADT_A02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A02"

    def test_adt_a02_to_json(self):
        msg = ADT_A02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A02"

    def test_adt_a03_to_dict(self):
        msg = ADT_A03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A03"

    def test_adt_a03_to_json(self):
        msg = ADT_A03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A03"

    def test_adt_a05_to_dict(self):
        msg = ADT_A05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A05"

    def test_adt_a05_to_json(self):
        msg = ADT_A05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A05"

    def test_adt_a06_to_dict(self):
        msg = ADT_A06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A06"

    def test_adt_a06_to_json(self):
        msg = ADT_A06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A06"

    def test_adt_a09_to_dict(self):
        msg = ADT_A09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A09"

    def test_adt_a09_to_json(self):
        msg = ADT_A09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A09"

    def test_adt_a12_to_dict(self):
        msg = ADT_A12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A12"

    def test_adt_a12_to_json(self):
        msg = ADT_A12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A12"

    def test_adt_a15_to_dict(self):
        msg = ADT_A15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A15"

    def test_adt_a15_to_json(self):
        msg = ADT_A15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A15"

    def test_adt_a16_to_dict(self):
        msg = ADT_A16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A16"

    def test_adt_a16_to_json(self):
        msg = ADT_A16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A16"

    def test_adt_a17_to_dict(self):
        msg = ADT_A17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A17"

    def test_adt_a17_to_json(self):
        msg = ADT_A17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A17"

    def test_adt_a20_to_dict(self):
        msg = ADT_A20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A20"

    def test_adt_a20_to_json(self):
        msg = ADT_A20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A20"

    def test_adt_a21_to_dict(self):
        msg = ADT_A21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A21"

    def test_adt_a21_to_json(self):
        msg = ADT_A21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A21"

    def test_adt_a24_to_dict(self):
        msg = ADT_A24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A24"

    def test_adt_a24_to_json(self):
        msg = ADT_A24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A24"

    def test_adt_a37_to_dict(self):
        msg = ADT_A37()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A37"

    def test_adt_a37_to_json(self):
        msg = ADT_A37()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A37"

    def test_adt_a38_to_dict(self):
        msg = ADT_A38()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A38"

    def test_adt_a38_to_json(self):
        msg = ADT_A38()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A38"

    def test_adt_a39_to_dict(self):
        msg = ADT_A39()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A39"

    def test_adt_a39_to_json(self):
        msg = ADT_A39()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A39"

    def test_adt_a43_to_dict(self):
        msg = ADT_A43()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A43"

    def test_adt_a43_to_json(self):
        msg = ADT_A43()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A43"

    def test_adt_a44_to_dict(self):
        msg = ADT_A44()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A44"

    def test_adt_a44_to_json(self):
        msg = ADT_A44()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A44"

    def test_adt_a45_to_dict(self):
        msg = ADT_A45()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A45"

    def test_adt_a45_to_json(self):
        msg = ADT_A45()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A45"

    def test_adt_a50_to_dict(self):
        msg = ADT_A50()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A50"

    def test_adt_a50_to_json(self):
        msg = ADT_A50()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A50"

    def test_adt_a52_to_dict(self):
        msg = ADT_A52()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A52"

    def test_adt_a52_to_json(self):
        msg = ADT_A52()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A52"

    def test_adt_a54_to_dict(self):
        msg = ADT_A54()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A54"

    def test_adt_a54_to_json(self):
        msg = ADT_A54()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A54"

    def test_adt_a60_to_dict(self):
        msg = ADT_A60()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A60"

    def test_adt_a60_to_json(self):
        msg = ADT_A60()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A60"

    def test_adt_a61_to_dict(self):
        msg = ADT_A61()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A61"

    def test_adt_a61_to_json(self):
        msg = ADT_A61()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A61"

    def test_bar_p01_to_dict(self):
        msg = BAR_P01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P01"

    def test_bar_p01_to_json(self):
        msg = BAR_P01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P01"

    def test_bar_p02_to_dict(self):
        msg = BAR_P02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P02"

    def test_bar_p02_to_json(self):
        msg = BAR_P02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P02"

    def test_bar_p05_to_dict(self):
        msg = BAR_P05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P05"

    def test_bar_p05_to_json(self):
        msg = BAR_P05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P05"

    def test_bar_p06_to_dict(self):
        msg = BAR_P06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P06"

    def test_bar_p06_to_json(self):
        msg = BAR_P06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P06"

    def test_bar_p10_to_dict(self):
        msg = BAR_P10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P10"

    def test_bar_p10_to_json(self):
        msg = BAR_P10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P10"

    def test_bar_p12_to_dict(self):
        msg = BAR_P12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P12"

    def test_bar_p12_to_json(self):
        msg = BAR_P12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P12"

    def test_bps_o29_to_dict(self):
        msg = BPS_O29()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BPS_O29"

    def test_bps_o29_to_json(self):
        msg = BPS_O29()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BPS_O29"

    def test_brp_o30_to_dict(self):
        msg = BRP_O30()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BRP_O30"

    def test_brp_o30_to_json(self):
        msg = BRP_O30()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BRP_O30"

    def test_brt_o32_to_dict(self):
        msg = BRT_O32()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BRT_O32"

    def test_brt_o32_to_json(self):
        msg = BRT_O32()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BRT_O32"

    def test_bts_o31_to_dict(self):
        msg = BTS_O31()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BTS_O31"

    def test_bts_o31_to_json(self):
        msg = BTS_O31()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BTS_O31"

    def test_ccf_i22_to_dict(self):
        msg = CCF_I22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCF_I22"

    def test_ccf_i22_to_json(self):
        msg = CCF_I22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCF_I22"

    def test_cci_i22_to_dict(self):
        msg = CCI_I22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCI_I22"

    def test_cci_i22_to_json(self):
        msg = CCI_I22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCI_I22"

    def test_ccm_i21_to_dict(self):
        msg = CCM_I21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCM_I21"

    def test_ccm_i21_to_json(self):
        msg = CCM_I21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCM_I21"

    def test_ccq_i19_to_dict(self):
        msg = CCQ_I19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCQ_I19"

    def test_ccq_i19_to_json(self):
        msg = CCQ_I19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCQ_I19"

    def test_ccr_i16_to_dict(self):
        msg = CCR_I16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCR_I16"

    def test_ccr_i16_to_json(self):
        msg = CCR_I16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCR_I16"

    def test_ccu_i20_to_dict(self):
        msg = CCU_I20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCU_I20"

    def test_ccu_i20_to_json(self):
        msg = CCU_I20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCU_I20"

    def test_cqu_i19_to_dict(self):
        msg = CQU_I19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CQU_I19"

    def test_cqu_i19_to_json(self):
        msg = CQU_I19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CQU_I19"

    def test_crm_c01_to_dict(self):
        msg = CRM_C01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CRM_C01"

    def test_crm_c01_to_json(self):
        msg = CRM_C01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CRM_C01"

    def test_csu_c09_to_dict(self):
        msg = CSU_C09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CSU_C09"

    def test_csu_c09_to_json(self):
        msg = CSU_C09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CSU_C09"

    def test_dbc_o41_to_dict(self):
        msg = DBC_O41()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DBC_O41"

    def test_dbc_o41_to_json(self):
        msg = DBC_O41()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DBC_O41"

    def test_dbc_o42_to_dict(self):
        msg = DBC_O42()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DBC_O42"

    def test_dbc_o42_to_json(self):
        msg = DBC_O42()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DBC_O42"

    def test_del_o46_to_dict(self):
        msg = DEL_O46()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DEL_O46"

    def test_del_o46_to_json(self):
        msg = DEL_O46()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DEL_O46"

    def test_deo_o45_to_dict(self):
        msg = DEO_O45()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DEO_O45"

    def test_deo_o45_to_json(self):
        msg = DEO_O45()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DEO_O45"

    def test_der_o44_to_dict(self):
        msg = DER_O44()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DER_O44"

    def test_der_o44_to_json(self):
        msg = DER_O44()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DER_O44"

    def test_dft_p03_to_dict(self):
        msg = DFT_P03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DFT_P03"

    def test_dft_p03_to_json(self):
        msg = DFT_P03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DFT_P03"

    def test_dft_p11_to_dict(self):
        msg = DFT_P11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DFT_P11"

    def test_dft_p11_to_json(self):
        msg = DFT_P11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DFT_P11"

    def test_dpr_o48_to_dict(self):
        msg = DPR_O48()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DPR_O48"

    def test_dpr_o48_to_json(self):
        msg = DPR_O48()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DPR_O48"

    def test_drc_o47_to_dict(self):
        msg = DRC_O47()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DRC_O47"

    def test_drc_o47_to_json(self):
        msg = DRC_O47()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DRC_O47"

    def test_drg_o43_to_dict(self):
        msg = DRG_O43()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DRG_O43"

    def test_drg_o43_to_json(self):
        msg = DRG_O43()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DRG_O43"

    def test_eac_u07_to_dict(self):
        msg = EAC_U07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EAC_U07"

    def test_eac_u07_to_json(self):
        msg = EAC_U07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EAC_U07"

    def test_ean_u09_to_dict(self):
        msg = EAN_U09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EAN_U09"

    def test_ean_u09_to_json(self):
        msg = EAN_U09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EAN_U09"

    def test_ear_u08_to_dict(self):
        msg = EAR_U08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EAR_U08"

    def test_ear_u08_to_json(self):
        msg = EAR_U08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EAR_U08"

    def test_ehc_e01_to_dict(self):
        msg = EHC_E01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E01"

    def test_ehc_e01_to_json(self):
        msg = EHC_E01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E01"

    def test_ehc_e02_to_dict(self):
        msg = EHC_E02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E02"

    def test_ehc_e02_to_json(self):
        msg = EHC_E02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E02"

    def test_ehc_e04_to_dict(self):
        msg = EHC_E04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E04"

    def test_ehc_e04_to_json(self):
        msg = EHC_E04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E04"

    def test_ehc_e10_to_dict(self):
        msg = EHC_E10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E10"

    def test_ehc_e10_to_json(self):
        msg = EHC_E10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E10"

    def test_ehc_e12_to_dict(self):
        msg = EHC_E12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E12"

    def test_ehc_e12_to_json(self):
        msg = EHC_E12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E12"

    def test_ehc_e13_to_dict(self):
        msg = EHC_E13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E13"

    def test_ehc_e13_to_json(self):
        msg = EHC_E13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E13"

    def test_ehc_e15_to_dict(self):
        msg = EHC_E15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E15"

    def test_ehc_e15_to_json(self):
        msg = EHC_E15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E15"

    def test_ehc_e20_to_dict(self):
        msg = EHC_E20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E20"

    def test_ehc_e20_to_json(self):
        msg = EHC_E20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E20"

    def test_ehc_e21_to_dict(self):
        msg = EHC_E21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E21"

    def test_ehc_e21_to_json(self):
        msg = EHC_E21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E21"

    def test_ehc_e24_to_dict(self):
        msg = EHC_E24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E24"

    def test_ehc_e24_to_json(self):
        msg = EHC_E24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E24"

    def test_esr_u02_to_dict(self):
        msg = ESR_U02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ESR_U02"

    def test_esr_u02_to_json(self):
        msg = ESR_U02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ESR_U02"

    def test_esu_u01_to_dict(self):
        msg = ESU_U01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ESU_U01"

    def test_esu_u01_to_json(self):
        msg = ESU_U01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ESU_U01"

    def test_inr_u06_to_dict(self):
        msg = INR_U06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "INR_U06"

    def test_inr_u06_to_json(self):
        msg = INR_U06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "INR_U06"

    def test_inr_u14_to_dict(self):
        msg = INR_U14()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "INR_U14"

    def test_inr_u14_to_json(self):
        msg = INR_U14()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "INR_U14"

    def test_inu_u05_to_dict(self):
        msg = INU_U05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "INU_U05"

    def test_inu_u05_to_json(self):
        msg = INU_U05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "INU_U05"

    def test_lsu_u12_to_dict(self):
        msg = LSU_U12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "LSU_U12"

    def test_lsu_u12_to_json(self):
        msg = LSU_U12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "LSU_U12"

    def test_mdm_t01_to_dict(self):
        msg = MDM_T01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MDM_T01"

    def test_mdm_t01_to_json(self):
        msg = MDM_T01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MDM_T01"

    def test_mdm_t02_to_dict(self):
        msg = MDM_T02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MDM_T02"

    def test_mdm_t02_to_json(self):
        msg = MDM_T02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MDM_T02"

    def test_mfk_m01_to_dict(self):
        msg = MFK_M01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFK_M01"

    def test_mfk_m01_to_json(self):
        msg = MFK_M01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFK_M01"

    def test_mfn_m02_to_dict(self):
        msg = MFN_M02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M02"

    def test_mfn_m02_to_json(self):
        msg = MFN_M02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M02"

    def test_mfn_m04_to_dict(self):
        msg = MFN_M04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M04"

    def test_mfn_m04_to_json(self):
        msg = MFN_M04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M04"

    def test_mfn_m05_to_dict(self):
        msg = MFN_M05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M05"

    def test_mfn_m05_to_json(self):
        msg = MFN_M05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M05"

    def test_mfn_m06_to_dict(self):
        msg = MFN_M06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M06"

    def test_mfn_m06_to_json(self):
        msg = MFN_M06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M06"

    def test_mfn_m07_to_dict(self):
        msg = MFN_M07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M07"

    def test_mfn_m07_to_json(self):
        msg = MFN_M07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M07"

    def test_mfn_m08_to_dict(self):
        msg = MFN_M08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M08"

    def test_mfn_m08_to_json(self):
        msg = MFN_M08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M08"

    def test_mfn_m09_to_dict(self):
        msg = MFN_M09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M09"

    def test_mfn_m09_to_json(self):
        msg = MFN_M09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M09"

    def test_mfn_m10_to_dict(self):
        msg = MFN_M10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M10"

    def test_mfn_m10_to_json(self):
        msg = MFN_M10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M10"

    def test_mfn_m11_to_dict(self):
        msg = MFN_M11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M11"

    def test_mfn_m11_to_json(self):
        msg = MFN_M11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M11"

    def test_mfn_m12_to_dict(self):
        msg = MFN_M12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M12"

    def test_mfn_m12_to_json(self):
        msg = MFN_M12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M12"

    def test_mfn_m13_to_dict(self):
        msg = MFN_M13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M13"

    def test_mfn_m13_to_json(self):
        msg = MFN_M13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M13"

    def test_mfn_m15_to_dict(self):
        msg = MFN_M15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M15"

    def test_mfn_m15_to_json(self):
        msg = MFN_M15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M15"

    def test_mfn_m16_to_dict(self):
        msg = MFN_M16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M16"

    def test_mfn_m16_to_json(self):
        msg = MFN_M16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M16"

    def test_mfn_m17_to_dict(self):
        msg = MFN_M17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M17"

    def test_mfn_m17_to_json(self):
        msg = MFN_M17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M17"

    def test_mfn_m18_to_dict(self):
        msg = MFN_M18()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M18"

    def test_mfn_m18_to_json(self):
        msg = MFN_M18()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M18"

    def test_mfn_m19_to_dict(self):
        msg = MFN_M19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M19"

    def test_mfn_m19_to_json(self):
        msg = MFN_M19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M19"

    def test_mfn_znn_to_dict(self):
        msg = MFN_Znn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_Znn"

    def test_mfn_znn_to_json(self):
        msg = MFN_Znn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_Znn"

    def test_nmd_n02_to_dict(self):
        msg = NMD_N02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "NMD_N02"

    def test_nmd_n02_to_json(self):
        msg = NMD_N02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "NMD_N02"

    def test_omb_o27_to_dict(self):
        msg = OMB_O27()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMB_O27"

    def test_omb_o27_to_json(self):
        msg = OMB_O27()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMB_O27"

    def test_omd_o03_to_dict(self):
        msg = OMD_O03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMD_O03"

    def test_omd_o03_to_json(self):
        msg = OMD_O03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMD_O03"

    def test_omg_o19_to_dict(self):
        msg = OMG_O19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMG_O19"

    def test_omg_o19_to_json(self):
        msg = OMG_O19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMG_O19"

    def test_omi_o23_to_dict(self):
        msg = OMI_O23()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMI_O23"

    def test_omi_o23_to_json(self):
        msg = OMI_O23()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMI_O23"

    def test_oml_o21_to_dict(self):
        msg = OML_O21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O21"

    def test_oml_o21_to_json(self):
        msg = OML_O21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O21"

    def test_oml_o33_to_dict(self):
        msg = OML_O33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O33"

    def test_oml_o33_to_json(self):
        msg = OML_O33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O33"

    def test_oml_o35_to_dict(self):
        msg = OML_O35()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O35"

    def test_oml_o35_to_json(self):
        msg = OML_O35()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O35"

    def test_oml_o39_to_dict(self):
        msg = OML_O39()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O39"

    def test_oml_o39_to_json(self):
        msg = OML_O39()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O39"

    def test_oml_o59_to_dict(self):
        msg = OML_O59()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O59"

    def test_oml_o59_to_json(self):
        msg = OML_O59()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O59"

    def test_omn_o07_to_dict(self):
        msg = OMN_O07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMN_O07"

    def test_omn_o07_to_json(self):
        msg = OMN_O07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMN_O07"

    def test_omp_o09_to_dict(self):
        msg = OMP_O09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMP_O09"

    def test_omp_o09_to_json(self):
        msg = OMP_O09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMP_O09"

    def test_omq_o57_to_dict(self):
        msg = OMQ_O57()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMQ_O57"

    def test_omq_o57_to_json(self):
        msg = OMQ_O57()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMQ_O57"

    def test_oms_o05_to_dict(self):
        msg = OMS_O05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMS_O05"

    def test_oms_o05_to_json(self):
        msg = OMS_O05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMS_O05"

    def test_opl_o37_to_dict(self):
        msg = OPL_O37()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OPL_O37"

    def test_opl_o37_to_json(self):
        msg = OPL_O37()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OPL_O37"

    def test_opr_o38_to_dict(self):
        msg = OPR_O38()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OPR_O38"

    def test_opr_o38_to_json(self):
        msg = OPR_O38()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OPR_O38"

    def test_opu_r25_to_dict(self):
        msg = OPU_R25()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OPU_R25"

    def test_opu_r25_to_json(self):
        msg = OPU_R25()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OPU_R25"

    def test_ora_r33_to_dict(self):
        msg = ORA_R33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORA_R33"

    def test_ora_r33_to_json(self):
        msg = ORA_R33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORA_R33"

    def test_ora_r41_to_dict(self):
        msg = ORA_R41()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORA_R41"

    def test_ora_r41_to_json(self):
        msg = ORA_R41()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORA_R41"

    def test_orb_o28_to_dict(self):
        msg = ORB_O28()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORB_O28"

    def test_orb_o28_to_json(self):
        msg = ORB_O28()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORB_O28"

    def test_ord_o04_to_dict(self):
        msg = ORD_O04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORD_O04"

    def test_ord_o04_to_json(self):
        msg = ORD_O04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORD_O04"

    def test_org_o20_to_dict(self):
        msg = ORG_O20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORG_O20"

    def test_org_o20_to_json(self):
        msg = ORG_O20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORG_O20"

    def test_ori_o24_to_dict(self):
        msg = ORI_O24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORI_O24"

    def test_ori_o24_to_json(self):
        msg = ORI_O24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORI_O24"

    def test_orl_o22_to_dict(self):
        msg = ORL_O22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O22"

    def test_orl_o22_to_json(self):
        msg = ORL_O22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O22"

    def test_orl_o34_to_dict(self):
        msg = ORL_O34()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O34"

    def test_orl_o34_to_json(self):
        msg = ORL_O34()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O34"

    def test_orl_o36_to_dict(self):
        msg = ORL_O36()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O36"

    def test_orl_o36_to_json(self):
        msg = ORL_O36()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O36"

    def test_orl_o40_to_dict(self):
        msg = ORL_O40()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O40"

    def test_orl_o40_to_json(self):
        msg = ORL_O40()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O40"

    def test_orl_o53_to_dict(self):
        msg = ORL_O53()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O53"

    def test_orl_o53_to_json(self):
        msg = ORL_O53()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O53"

    def test_orl_o54_to_dict(self):
        msg = ORL_O54()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O54"

    def test_orl_o54_to_json(self):
        msg = ORL_O54()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O54"

    def test_orl_o55_to_dict(self):
        msg = ORL_O55()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O55"

    def test_orl_o55_to_json(self):
        msg = ORL_O55()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O55"

    def test_orl_o56_to_dict(self):
        msg = ORL_O56()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O56"

    def test_orl_o56_to_json(self):
        msg = ORL_O56()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O56"

    def test_orm_o01_to_dict(self):
        msg = ORM_O01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORM_O01"

    def test_orm_o01_to_json(self):
        msg = ORM_O01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORM_O01"

    def test_orn_o08_to_dict(self):
        msg = ORN_O08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORN_O08"

    def test_orn_o08_to_json(self):
        msg = ORN_O08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORN_O08"

    def test_orp_o10_to_dict(self):
        msg = ORP_O10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORP_O10"

    def test_orp_o10_to_json(self):
        msg = ORP_O10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORP_O10"

    def test_ors_o06_to_dict(self):
        msg = ORS_O06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORS_O06"

    def test_ors_o06_to_json(self):
        msg = ORS_O06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORS_O06"

    def test_oru_r01_to_dict(self):
        msg = ORU_R01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORU_R01"

    def test_oru_r01_to_json(self):
        msg = ORU_R01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORU_R01"

    def test_oru_r30_to_dict(self):
        msg = ORU_R30()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORU_R30"

    def test_oru_r30_to_json(self):
        msg = ORU_R30()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORU_R30"

    def test_orx_o58_to_dict(self):
        msg = ORX_O58()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORX_O58"

    def test_orx_o58_to_json(self):
        msg = ORX_O58()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORX_O58"

    def test_osm_r26_to_dict(self):
        msg = OSM_R26()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OSM_R26"

    def test_osm_r26_to_json(self):
        msg = OSM_R26()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OSM_R26"

    def test_osu_o51_to_dict(self):
        msg = OSU_O51()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OSU_O51"

    def test_osu_o51_to_json(self):
        msg = OSU_O51()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OSU_O51"

    def test_osu_o52_to_dict(self):
        msg = OSU_O52()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OSU_O52"

    def test_osu_o52_to_json(self):
        msg = OSU_O52()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OSU_O52"

    def test_oul_r22_to_dict(self):
        msg = OUL_R22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OUL_R22"

    def test_oul_r22_to_json(self):
        msg = OUL_R22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OUL_R22"

    def test_oul_r23_to_dict(self):
        msg = OUL_R23()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OUL_R23"

    def test_oul_r23_to_json(self):
        msg = OUL_R23()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OUL_R23"

    def test_oul_r24_to_dict(self):
        msg = OUL_R24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OUL_R24"

    def test_oul_r24_to_json(self):
        msg = OUL_R24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OUL_R24"

    def test_pex_p07_to_dict(self):
        msg = PEX_P07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PEX_P07"

    def test_pex_p07_to_json(self):
        msg = PEX_P07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PEX_P07"

    def test_pgl_pc6_to_dict(self):
        msg = PGL_PC6()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PGL_PC6"

    def test_pgl_pc6_to_json(self):
        msg = PGL_PC6()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PGL_PC6"

    def test_pmu_b01_to_dict(self):
        msg = PMU_B01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B01"

    def test_pmu_b01_to_json(self):
        msg = PMU_B01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B01"

    def test_pmu_b03_to_dict(self):
        msg = PMU_B03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B03"

    def test_pmu_b03_to_json(self):
        msg = PMU_B03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B03"

    def test_pmu_b04_to_dict(self):
        msg = PMU_B04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B04"

    def test_pmu_b04_to_json(self):
        msg = PMU_B04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B04"

    def test_pmu_b07_to_dict(self):
        msg = PMU_B07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B07"

    def test_pmu_b07_to_json(self):
        msg = PMU_B07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B07"

    def test_pmu_b08_to_dict(self):
        msg = PMU_B08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B08"

    def test_pmu_b08_to_json(self):
        msg = PMU_B08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B08"

    def test_ppg_pcg_to_dict(self):
        msg = PPG_PCG()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PPG_PCG"

    def test_ppg_pcg_to_json(self):
        msg = PPG_PCG()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PPG_PCG"

    def test_ppp_pcb_to_dict(self):
        msg = PPP_PCB()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PPP_PCB"

    def test_ppp_pcb_to_json(self):
        msg = PPP_PCB()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PPP_PCB"

    def test_ppr_pc1_to_dict(self):
        msg = PPR_PC1()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PPR_PC1"

    def test_ppr_pc1_to_json(self):
        msg = PPR_PC1()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PPR_PC1"

    def test_qbp_e03_to_dict(self):
        msg = QBP_E03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_E03"

    def test_qbp_e03_to_json(self):
        msg = QBP_E03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_E03"

    def test_qbp_e22_to_dict(self):
        msg = QBP_E22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_E22"

    def test_qbp_e22_to_json(self):
        msg = QBP_E22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_E22"

    def test_qbp_o33_to_dict(self):
        msg = QBP_O33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_O33"

    def test_qbp_o33_to_json(self):
        msg = QBP_O33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_O33"

    def test_qbp_o34_to_dict(self):
        msg = QBP_O34()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_O34"

    def test_qbp_o34_to_json(self):
        msg = QBP_O34()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_O34"

    def test_qbp_q11_to_dict(self):
        msg = QBP_Q11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q11"

    def test_qbp_q11_to_json(self):
        msg = QBP_Q11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q11"

    def test_qbp_q13_to_dict(self):
        msg = QBP_Q13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q13"

    def test_qbp_q13_to_json(self):
        msg = QBP_Q13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q13"

    def test_qbp_q15_to_dict(self):
        msg = QBP_Q15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q15"

    def test_qbp_q15_to_json(self):
        msg = QBP_Q15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q15"

    def test_qbp_q21_to_dict(self):
        msg = QBP_Q21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q21"

    def test_qbp_q21_to_json(self):
        msg = QBP_Q21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q21"

    def test_qbp_qnn_to_dict(self):
        msg = QBP_Qnn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Qnn"

    def test_qbp_qnn_to_json(self):
        msg = QBP_Qnn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Qnn"

    def test_qbp_z73_to_dict(self):
        msg = QBP_Z73()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Z73"

    def test_qbp_z73_to_json(self):
        msg = QBP_Z73()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Z73"

    def test_qcn_j01_to_dict(self):
        msg = QCN_J01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QCN_J01"

    def test_qcn_j01_to_json(self):
        msg = QCN_J01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QCN_J01"

    def test_qsb_q16_to_dict(self):
        msg = QSB_Q16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QSB_Q16"

    def test_qsb_q16_to_json(self):
        msg = QSB_Q16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QSB_Q16"

    def test_qvr_q17_to_dict(self):
        msg = QVR_Q17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QVR_Q17"

    def test_qvr_q17_to_json(self):
        msg = QVR_Q17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QVR_Q17"

    def test_ras_o17_to_dict(self):
        msg = RAS_O17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RAS_O17"

    def test_ras_o17_to_json(self):
        msg = RAS_O17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RAS_O17"

    def test_rcv_o59_to_dict(self):
        msg = RCV_O59()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RCV_O59"

    def test_rcv_o59_to_json(self):
        msg = RCV_O59()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RCV_O59"

    def test_rde_o11_to_dict(self):
        msg = RDE_O11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDE_O11"

    def test_rde_o11_to_json(self):
        msg = RDE_O11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDE_O11"

    def test_rde_o49_to_dict(self):
        msg = RDE_O49()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDE_O49"

    def test_rde_o49_to_json(self):
        msg = RDE_O49()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDE_O49"

    def test_rdr_rdr_to_dict(self):
        msg = RDR_RDR()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDR_RDR"

    def test_rdr_rdr_to_json(self):
        msg = RDR_RDR()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDR_RDR"

    def test_rds_o13_to_dict(self):
        msg = RDS_O13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDS_O13"

    def test_rds_o13_to_json(self):
        msg = RDS_O13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDS_O13"

    def test_rdy_k15_to_dict(self):
        msg = RDY_K15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDY_K15"

    def test_rdy_k15_to_json(self):
        msg = RDY_K15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDY_K15"

    def test_rdy_z80_to_dict(self):
        msg = RDY_Z80()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDY_Z80"

    def test_rdy_z80_to_json(self):
        msg = RDY_Z80()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDY_Z80"

    def test_ref_i12_to_dict(self):
        msg = REF_I12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "REF_I12"

    def test_ref_i12_to_json(self):
        msg = REF_I12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "REF_I12"

    def test_rgv_o15_to_dict(self):
        msg = RGV_O15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RGV_O15"

    def test_rgv_o15_to_json(self):
        msg = RGV_O15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RGV_O15"

    def test_rpa_i08_to_dict(self):
        msg = RPA_I08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPA_I08"

    def test_rpa_i08_to_json(self):
        msg = RPA_I08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPA_I08"

    def test_rpi_i01_to_dict(self):
        msg = RPI_I01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPI_I01"

    def test_rpi_i01_to_json(self):
        msg = RPI_I01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPI_I01"

    def test_rpi_i04_to_dict(self):
        msg = RPI_I04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPI_I04"

    def test_rpi_i04_to_json(self):
        msg = RPI_I04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPI_I04"

    def test_rpl_i02_to_dict(self):
        msg = RPL_I02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPL_I02"

    def test_rpl_i02_to_json(self):
        msg = RPL_I02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPL_I02"

    def test_rpr_i03_to_dict(self):
        msg = RPR_I03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPR_I03"

    def test_rpr_i03_to_json(self):
        msg = RPR_I03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPR_I03"

    def test_rqa_i08_to_dict(self):
        msg = RQA_I08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RQA_I08"

    def test_rqa_i08_to_json(self):
        msg = RQA_I08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RQA_I08"

    def test_rqi_i01_to_dict(self):
        msg = RQI_I01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RQI_I01"

    def test_rqi_i01_to_json(self):
        msg = RQI_I01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RQI_I01"

    def test_rqp_i04_to_dict(self):
        msg = RQP_I04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RQP_I04"

    def test_rqp_i04_to_json(self):
        msg = RQP_I04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RQP_I04"

    def test_rra_o18_to_dict(self):
        msg = RRA_O18()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRA_O18"

    def test_rra_o18_to_json(self):
        msg = RRA_O18()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRA_O18"

    def test_rrd_o14_to_dict(self):
        msg = RRD_O14()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRD_O14"

    def test_rrd_o14_to_json(self):
        msg = RRD_O14()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRD_O14"

    def test_rre_o12_to_dict(self):
        msg = RRE_O12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRE_O12"

    def test_rre_o12_to_json(self):
        msg = RRE_O12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRE_O12"

    def test_rre_o50_to_dict(self):
        msg = RRE_O50()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRE_O50"

    def test_rre_o50_to_json(self):
        msg = RRE_O50()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRE_O50"

    def test_rrg_o16_to_dict(self):
        msg = RRG_O16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRG_O16"

    def test_rrg_o16_to_json(self):
        msg = RRG_O16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRG_O16"

    def test_rri_i12_to_dict(self):
        msg = RRI_I12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRI_I12"

    def test_rri_i12_to_json(self):
        msg = RRI_I12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRI_I12"

    def test_rsp_e03_to_dict(self):
        msg = RSP_E03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_E03"

    def test_rsp_e03_to_json(self):
        msg = RSP_E03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_E03"

    def test_rsp_e22_to_dict(self):
        msg = RSP_E22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_E22"

    def test_rsp_e22_to_json(self):
        msg = RSP_E22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_E22"

    def test_rsp_k11_to_dict(self):
        msg = RSP_K11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K11"

    def test_rsp_k11_to_json(self):
        msg = RSP_K11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K11"

    def test_rsp_k21_to_dict(self):
        msg = RSP_K21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K21"

    def test_rsp_k21_to_json(self):
        msg = RSP_K21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K21"

    def test_rsp_k22_to_dict(self):
        msg = RSP_K22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K22"

    def test_rsp_k22_to_json(self):
        msg = RSP_K22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K22"

    def test_rsp_k23_to_dict(self):
        msg = RSP_K23()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K23"

    def test_rsp_k23_to_json(self):
        msg = RSP_K23()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K23"

    def test_rsp_k25_to_dict(self):
        msg = RSP_K25()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K25"

    def test_rsp_k25_to_json(self):
        msg = RSP_K25()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K25"

    def test_rsp_k31_to_dict(self):
        msg = RSP_K31()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K31"

    def test_rsp_k31_to_json(self):
        msg = RSP_K31()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K31"

    def test_rsp_k32_to_dict(self):
        msg = RSP_K32()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K32"

    def test_rsp_k32_to_json(self):
        msg = RSP_K32()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K32"

    def test_rsp_o33_to_dict(self):
        msg = RSP_O33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_O33"

    def test_rsp_o33_to_json(self):
        msg = RSP_O33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_O33"

    def test_rsp_o34_to_dict(self):
        msg = RSP_O34()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_O34"

    def test_rsp_o34_to_json(self):
        msg = RSP_O34()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_O34"

    def test_rsp_z82_to_dict(self):
        msg = RSP_Z82()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z82"

    def test_rsp_z82_to_json(self):
        msg = RSP_Z82()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z82"

    def test_rsp_z84_to_dict(self):
        msg = RSP_Z84()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z84"

    def test_rsp_z84_to_json(self):
        msg = RSP_Z84()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z84"

    def test_rsp_z86_to_dict(self):
        msg = RSP_Z86()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z86"

    def test_rsp_z86_to_json(self):
        msg = RSP_Z86()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z86"

    def test_rsp_z88_to_dict(self):
        msg = RSP_Z88()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z88"

    def test_rsp_z88_to_json(self):
        msg = RSP_Z88()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z88"

    def test_rsp_z90_to_dict(self):
        msg = RSP_Z90()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z90"

    def test_rsp_z90_to_json(self):
        msg = RSP_Z90()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z90"

    def test_rsp_znn_to_dict(self):
        msg = RSP_Znn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Znn"

    def test_rsp_znn_to_json(self):
        msg = RSP_Znn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Znn"

    def test_rtb_k13_to_dict(self):
        msg = RTB_K13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RTB_K13"

    def test_rtb_k13_to_json(self):
        msg = RTB_K13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RTB_K13"

    def test_rtb_knn_to_dict(self):
        msg = RTB_Knn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RTB_Knn"

    def test_rtb_knn_to_json(self):
        msg = RTB_Knn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RTB_Knn"

    def test_rtb_z74_to_dict(self):
        msg = RTB_Z74()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RTB_Z74"

    def test_rtb_z74_to_json(self):
        msg = RTB_Z74()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RTB_Z74"

    def test_sdr_s31_to_dict(self):
        msg = SDR_S31()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SDR_S31"

    def test_sdr_s31_to_json(self):
        msg = SDR_S31()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SDR_S31"

    def test_sdr_s32_to_dict(self):
        msg = SDR_S32()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SDR_S32"

    def test_sdr_s32_to_json(self):
        msg = SDR_S32()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SDR_S32"

    def test_siu_s12_to_dict(self):
        msg = SIU_S12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SIU_S12"

    def test_siu_s12_to_json(self):
        msg = SIU_S12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SIU_S12"

    def test_slr_s28_to_dict(self):
        msg = SLR_S28()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SLR_S28"

    def test_slr_s28_to_json(self):
        msg = SLR_S28()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SLR_S28"

    def test_srm_s01_to_dict(self):
        msg = SRM_S01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SRM_S01"

    def test_srm_s01_to_json(self):
        msg = SRM_S01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SRM_S01"

    def test_srr_s01_to_dict(self):
        msg = SRR_S01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SRR_S01"

    def test_srr_s01_to_json(self):
        msg = SRR_S01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SRR_S01"

    def test_ssr_u04_to_dict(self):
        msg = SSR_U04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SSR_U04"

    def test_ssr_u04_to_json(self):
        msg = SSR_U04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SSR_U04"

    def test_ssu_u03_to_dict(self):
        msg = SSU_U03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SSU_U03"

    def test_ssu_u03_to_json(self):
        msg = SSU_U03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SSU_U03"

    def test_stc_s33_to_dict(self):
        msg = STC_S33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "STC_S33"

    def test_stc_s33_to_json(self):
        msg = STC_S33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "STC_S33"

    def test_tcu_u10_to_dict(self):
        msg = TCU_U10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "TCU_U10"

    def test_tcu_u10_to_json(self):
        msg = TCU_U10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "TCU_U10"

    def test_udm_q05_to_dict(self):
        msg = UDM_Q05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "UDM_Q05"

    def test_udm_q05_to_json(self):
        msg = UDM_Q05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "UDM_Q05"

    def test_vxu_v04_to_dict(self):
        msg = VXU_V04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "VXU_V04"

    def test_vxu_v04_to_json(self):
        msg = VXU_V04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "VXU_V04"
