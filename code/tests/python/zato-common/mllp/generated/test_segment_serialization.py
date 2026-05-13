from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import (
    ABS,
    ACC,
    ADD,
    ADJ,
    AFF,
    AIG,
    AIL,
    AIP,
    AIS,
    AL1,
    APR,
    ARQ,
    ARV,
    AUT,
    BHS,
    BLC,
    BLG,
    BPO,
    BPX,
    BTS,
    BTX,
    BUI,
    CDM,
    CDO,
    CER,
    CM0,
    CM1,
    CM2,
    CNS,
    CON,
    CSP,
    CSR,
    CSS,
    CTD,
    CTI,
    CTR,
    DB1,
    DEV,
    DG1,
    DMI,
    DON,
    DPS,
    DRG,
    DSC,
    DSP,
    DST,
    ECD,
    ECR,
    EDU,
    EQP,
    EQU,
    ERR,
    EVN,
    FAC,
    FHS,
    FT1,
    FTS,
    GOL,
    GP1,
    GP2,
    GT1,
    IAM,
    IAR,
    IIM,
    ILT,
    IN1,
    IN2,
    IN3,
    INV,
    IPC,
    IPR,
    ISD,
    ITM,
    IVC,
    IVT,
    LAN,
    LCC,
    LCH,
    LDP,
    LOC,
    LRL,
    MCP,
    MFA,
    MFE,
    MFI,
    MRG,
    MSA,
    MSH,
    NCK,
    NDS,
    NK1,
    NPU,
    NSC,
    NST,
    NTE,
    OBR,
    OBX,
    ODS,
    ODT,
    OH1,
    OH2,
    OH3,
    OH4,
    OM1,
    OM2,
    OM3,
    OM4,
    OM5,
    OM6,
    OM7,
    OMC,
    ORC,
    ORG,
    OVR,
    PAC,
    PCE,
    PCR,
    PD1,
    PDA,
    PDC,
    PEO,
    PES,
    PID,
    PKG,
    PM1,
    PMT,
    PR1,
    PRA,
    PRB,
    PRC,
    PRD,
    PRT,
    PSG,
    PSH,
    PSL,
    PSS,
    PTH,
    PV1,
    PV2,
    PYE,
    QAK,
    QID,
    QPD,
    QRI,
    RCP,
    RDF,
    RDT,
    REL,
    RF1,
    RFI,
    RGS,
    RMI,
    RQ1,
    RQD,
    RXA,
    RXC,
    RXD,
    RXE,
    RXG,
    RXO,
    RXR,
    RXV,
    SAC,
    SCD,
    SCH,
    SCP,
    SDD,
    SFT,
    SGH,
    SGT,
    SHP,
    SID,
    SLT,
    SPM,
    STF,
    STZ,
    TCC,
    TCD,
    TQ1,
    TQ2,
    TXA,
    UAC,
    UB2,
    VAR,
    VND,
    ZL7,
)


class TestSegmentSerialization:
    """Test serialization methods for all segment classes."""

    def test_abs_to_dict(self):
        seg = ABS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ABS"

    def test_abs_to_json(self):
        seg = ABS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ABS"

    def test_acc_to_dict(self):
        seg = ACC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ACC"

    def test_acc_to_json(self):
        seg = ACC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ACC"

    def test_add_to_dict(self):
        seg = ADD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ADD"

    def test_add_to_json(self):
        seg = ADD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ADD"

    def test_adj_to_dict(self):
        seg = ADJ()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ADJ"

    def test_adj_to_json(self):
        seg = ADJ()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ADJ"

    def test_aff_to_dict(self):
        seg = AFF()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AFF"

    def test_aff_to_json(self):
        seg = AFF()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AFF"

    def test_aig_to_dict(self):
        seg = AIG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AIG"

    def test_aig_to_json(self):
        seg = AIG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AIG"

    def test_ail_to_dict(self):
        seg = AIL()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AIL"

    def test_ail_to_json(self):
        seg = AIL()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AIL"

    def test_aip_to_dict(self):
        seg = AIP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AIP"

    def test_aip_to_json(self):
        seg = AIP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AIP"

    def test_ais_to_dict(self):
        seg = AIS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AIS"

    def test_ais_to_json(self):
        seg = AIS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AIS"

    def test_al1_to_dict(self):
        seg = AL1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AL1"

    def test_al1_to_json(self):
        seg = AL1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AL1"

    def test_apr_to_dict(self):
        seg = APR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "APR"

    def test_apr_to_json(self):
        seg = APR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "APR"

    def test_arq_to_dict(self):
        seg = ARQ()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ARQ"

    def test_arq_to_json(self):
        seg = ARQ()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ARQ"

    def test_arv_to_dict(self):
        seg = ARV()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ARV"

    def test_arv_to_json(self):
        seg = ARV()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ARV"

    def test_aut_to_dict(self):
        seg = AUT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "AUT"

    def test_aut_to_json(self):
        seg = AUT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "AUT"

    def test_bhs_to_dict(self):
        seg = BHS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BHS"

    def test_bhs_to_json(self):
        seg = BHS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BHS"

    def test_blc_to_dict(self):
        seg = BLC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BLC"

    def test_blc_to_json(self):
        seg = BLC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BLC"

    def test_blg_to_dict(self):
        seg = BLG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BLG"

    def test_blg_to_json(self):
        seg = BLG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BLG"

    def test_bpo_to_dict(self):
        seg = BPO()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BPO"

    def test_bpo_to_json(self):
        seg = BPO()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BPO"

    def test_bpx_to_dict(self):
        seg = BPX()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BPX"

    def test_bpx_to_json(self):
        seg = BPX()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BPX"

    def test_bts_to_dict(self):
        seg = BTS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BTS"

    def test_bts_to_json(self):
        seg = BTS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BTS"

    def test_btx_to_dict(self):
        seg = BTX()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BTX"

    def test_btx_to_json(self):
        seg = BTX()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BTX"

    def test_bui_to_dict(self):
        seg = BUI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "BUI"

    def test_bui_to_json(self):
        seg = BUI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "BUI"

    def test_cdm_to_dict(self):
        seg = CDM()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CDM"

    def test_cdm_to_json(self):
        seg = CDM()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CDM"

    def test_cdo_to_dict(self):
        seg = CDO()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CDO"

    def test_cdo_to_json(self):
        seg = CDO()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CDO"

    def test_cer_to_dict(self):
        seg = CER()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CER"

    def test_cer_to_json(self):
        seg = CER()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CER"

    def test_cm0_to_dict(self):
        seg = CM0()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CM0"

    def test_cm0_to_json(self):
        seg = CM0()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CM0"

    def test_cm1_to_dict(self):
        seg = CM1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CM1"

    def test_cm1_to_json(self):
        seg = CM1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CM1"

    def test_cm2_to_dict(self):
        seg = CM2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CM2"

    def test_cm2_to_json(self):
        seg = CM2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CM2"

    def test_cns_to_dict(self):
        seg = CNS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CNS"

    def test_cns_to_json(self):
        seg = CNS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CNS"

    def test_con_to_dict(self):
        seg = CON()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CON"

    def test_con_to_json(self):
        seg = CON()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CON"

    def test_csp_to_dict(self):
        seg = CSP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CSP"

    def test_csp_to_json(self):
        seg = CSP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CSP"

    def test_csr_to_dict(self):
        seg = CSR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CSR"

    def test_csr_to_json(self):
        seg = CSR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CSR"

    def test_css_to_dict(self):
        seg = CSS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CSS"

    def test_css_to_json(self):
        seg = CSS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CSS"

    def test_ctd_to_dict(self):
        seg = CTD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CTD"

    def test_ctd_to_json(self):
        seg = CTD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CTD"

    def test_cti_to_dict(self):
        seg = CTI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CTI"

    def test_cti_to_json(self):
        seg = CTI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CTI"

    def test_ctr_to_dict(self):
        seg = CTR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "CTR"

    def test_ctr_to_json(self):
        seg = CTR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "CTR"

    def test_db1_to_dict(self):
        seg = DB1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DB1"

    def test_db1_to_json(self):
        seg = DB1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DB1"

    def test_dev_to_dict(self):
        seg = DEV()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DEV"

    def test_dev_to_json(self):
        seg = DEV()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DEV"

    def test_dg1_to_dict(self):
        seg = DG1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DG1"

    def test_dg1_to_json(self):
        seg = DG1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DG1"

    def test_dmi_to_dict(self):
        seg = DMI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DMI"

    def test_dmi_to_json(self):
        seg = DMI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DMI"

    def test_don_to_dict(self):
        seg = DON()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DON"

    def test_don_to_json(self):
        seg = DON()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DON"

    def test_dps_to_dict(self):
        seg = DPS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DPS"

    def test_dps_to_json(self):
        seg = DPS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DPS"

    def test_drg_to_dict(self):
        seg = DRG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DRG"

    def test_drg_to_json(self):
        seg = DRG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DRG"

    def test_dsc_to_dict(self):
        seg = DSC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DSC"

    def test_dsc_to_json(self):
        seg = DSC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DSC"

    def test_dsp_to_dict(self):
        seg = DSP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DSP"

    def test_dsp_to_json(self):
        seg = DSP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DSP"

    def test_dst_to_dict(self):
        seg = DST()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "DST"

    def test_dst_to_json(self):
        seg = DST()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "DST"

    def test_ecd_to_dict(self):
        seg = ECD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ECD"

    def test_ecd_to_json(self):
        seg = ECD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ECD"

    def test_ecr_to_dict(self):
        seg = ECR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ECR"

    def test_ecr_to_json(self):
        seg = ECR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ECR"

    def test_edu_to_dict(self):
        seg = EDU()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "EDU"

    def test_edu_to_json(self):
        seg = EDU()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "EDU"

    def test_eqp_to_dict(self):
        seg = EQP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "EQP"

    def test_eqp_to_json(self):
        seg = EQP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "EQP"

    def test_equ_to_dict(self):
        seg = EQU()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "EQU"

    def test_equ_to_json(self):
        seg = EQU()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "EQU"

    def test_err_to_dict(self):
        seg = ERR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ERR"

    def test_err_to_json(self):
        seg = ERR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ERR"

    def test_evn_to_dict(self):
        seg = EVN()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "EVN"

    def test_evn_to_json(self):
        seg = EVN()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "EVN"

    def test_fac_to_dict(self):
        seg = FAC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "FAC"

    def test_fac_to_json(self):
        seg = FAC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "FAC"

    def test_fhs_to_dict(self):
        seg = FHS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "FHS"

    def test_fhs_to_json(self):
        seg = FHS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "FHS"

    def test_ft1_to_dict(self):
        seg = FT1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "FT1"

    def test_ft1_to_json(self):
        seg = FT1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "FT1"

    def test_fts_to_dict(self):
        seg = FTS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "FTS"

    def test_fts_to_json(self):
        seg = FTS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "FTS"

    def test_gol_to_dict(self):
        seg = GOL()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "GOL"

    def test_gol_to_json(self):
        seg = GOL()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "GOL"

    def test_gp1_to_dict(self):
        seg = GP1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "GP1"

    def test_gp1_to_json(self):
        seg = GP1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "GP1"

    def test_gp2_to_dict(self):
        seg = GP2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "GP2"

    def test_gp2_to_json(self):
        seg = GP2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "GP2"

    def test_gt1_to_dict(self):
        seg = GT1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "GT1"

    def test_gt1_to_json(self):
        seg = GT1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "GT1"

    def test_iam_to_dict(self):
        seg = IAM()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IAM"

    def test_iam_to_json(self):
        seg = IAM()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IAM"

    def test_iar_to_dict(self):
        seg = IAR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IAR"

    def test_iar_to_json(self):
        seg = IAR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IAR"

    def test_iim_to_dict(self):
        seg = IIM()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IIM"

    def test_iim_to_json(self):
        seg = IIM()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IIM"

    def test_ilt_to_dict(self):
        seg = ILT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ILT"

    def test_ilt_to_json(self):
        seg = ILT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ILT"

    def test_in1_to_dict(self):
        seg = IN1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IN1"

    def test_in1_to_json(self):
        seg = IN1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IN1"

    def test_in2_to_dict(self):
        seg = IN2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IN2"

    def test_in2_to_json(self):
        seg = IN2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IN2"

    def test_in3_to_dict(self):
        seg = IN3()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IN3"

    def test_in3_to_json(self):
        seg = IN3()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IN3"

    def test_inv_to_dict(self):
        seg = INV()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "INV"

    def test_inv_to_json(self):
        seg = INV()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "INV"

    def test_ipc_to_dict(self):
        seg = IPC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IPC"

    def test_ipc_to_json(self):
        seg = IPC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IPC"

    def test_ipr_to_dict(self):
        seg = IPR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IPR"

    def test_ipr_to_json(self):
        seg = IPR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IPR"

    def test_isd_to_dict(self):
        seg = ISD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ISD"

    def test_isd_to_json(self):
        seg = ISD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ISD"

    def test_itm_to_dict(self):
        seg = ITM()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ITM"

    def test_itm_to_json(self):
        seg = ITM()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ITM"

    def test_ivc_to_dict(self):
        seg = IVC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IVC"

    def test_ivc_to_json(self):
        seg = IVC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IVC"

    def test_ivt_to_dict(self):
        seg = IVT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "IVT"

    def test_ivt_to_json(self):
        seg = IVT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "IVT"

    def test_lan_to_dict(self):
        seg = LAN()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "LAN"

    def test_lan_to_json(self):
        seg = LAN()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "LAN"

    def test_lcc_to_dict(self):
        seg = LCC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "LCC"

    def test_lcc_to_json(self):
        seg = LCC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "LCC"

    def test_lch_to_dict(self):
        seg = LCH()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "LCH"

    def test_lch_to_json(self):
        seg = LCH()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "LCH"

    def test_ldp_to_dict(self):
        seg = LDP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "LDP"

    def test_ldp_to_json(self):
        seg = LDP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "LDP"

    def test_loc_to_dict(self):
        seg = LOC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "LOC"

    def test_loc_to_json(self):
        seg = LOC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "LOC"

    def test_lrl_to_dict(self):
        seg = LRL()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "LRL"

    def test_lrl_to_json(self):
        seg = LRL()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "LRL"

    def test_mcp_to_dict(self):
        seg = MCP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MCP"

    def test_mcp_to_json(self):
        seg = MCP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MCP"

    def test_mfa_to_dict(self):
        seg = MFA()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MFA"

    def test_mfa_to_json(self):
        seg = MFA()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MFA"

    def test_mfe_to_dict(self):
        seg = MFE()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MFE"

    def test_mfe_to_json(self):
        seg = MFE()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MFE"

    def test_mfi_to_dict(self):
        seg = MFI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MFI"

    def test_mfi_to_json(self):
        seg = MFI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MFI"

    def test_mrg_to_dict(self):
        seg = MRG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MRG"

    def test_mrg_to_json(self):
        seg = MRG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MRG"

    def test_msa_to_dict(self):
        seg = MSA()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MSA"

    def test_msa_to_json(self):
        seg = MSA()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MSA"

    def test_msh_to_dict(self):
        seg = MSH()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "MSH"

    def test_msh_to_json(self):
        seg = MSH()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "MSH"

    def test_nck_to_dict(self):
        seg = NCK()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NCK"

    def test_nck_to_json(self):
        seg = NCK()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NCK"

    def test_nds_to_dict(self):
        seg = NDS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NDS"

    def test_nds_to_json(self):
        seg = NDS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NDS"

    def test_nk1_to_dict(self):
        seg = NK1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NK1"

    def test_nk1_to_json(self):
        seg = NK1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NK1"

    def test_npu_to_dict(self):
        seg = NPU()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NPU"

    def test_npu_to_json(self):
        seg = NPU()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NPU"

    def test_nsc_to_dict(self):
        seg = NSC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NSC"

    def test_nsc_to_json(self):
        seg = NSC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NSC"

    def test_nst_to_dict(self):
        seg = NST()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NST"

    def test_nst_to_json(self):
        seg = NST()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NST"

    def test_nte_to_dict(self):
        seg = NTE()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "NTE"

    def test_nte_to_json(self):
        seg = NTE()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "NTE"

    def test_obr_to_dict(self):
        seg = OBR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OBR"

    def test_obr_to_json(self):
        seg = OBR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OBR"

    def test_obx_to_dict(self):
        seg = OBX()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OBX"

    def test_obx_to_json(self):
        seg = OBX()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OBX"

    def test_ods_to_dict(self):
        seg = ODS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ODS"

    def test_ods_to_json(self):
        seg = ODS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ODS"

    def test_odt_to_dict(self):
        seg = ODT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ODT"

    def test_odt_to_json(self):
        seg = ODT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ODT"

    def test_oh1_to_dict(self):
        seg = OH1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OH1"

    def test_oh1_to_json(self):
        seg = OH1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OH1"

    def test_oh2_to_dict(self):
        seg = OH2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OH2"

    def test_oh2_to_json(self):
        seg = OH2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OH2"

    def test_oh3_to_dict(self):
        seg = OH3()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OH3"

    def test_oh3_to_json(self):
        seg = OH3()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OH3"

    def test_oh4_to_dict(self):
        seg = OH4()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OH4"

    def test_oh4_to_json(self):
        seg = OH4()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OH4"

    def test_om1_to_dict(self):
        seg = OM1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM1"

    def test_om1_to_json(self):
        seg = OM1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM1"

    def test_om2_to_dict(self):
        seg = OM2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM2"

    def test_om2_to_json(self):
        seg = OM2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM2"

    def test_om3_to_dict(self):
        seg = OM3()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM3"

    def test_om3_to_json(self):
        seg = OM3()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM3"

    def test_om4_to_dict(self):
        seg = OM4()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM4"

    def test_om4_to_json(self):
        seg = OM4()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM4"

    def test_om5_to_dict(self):
        seg = OM5()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM5"

    def test_om5_to_json(self):
        seg = OM5()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM5"

    def test_om6_to_dict(self):
        seg = OM6()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM6"

    def test_om6_to_json(self):
        seg = OM6()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM6"

    def test_om7_to_dict(self):
        seg = OM7()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OM7"

    def test_om7_to_json(self):
        seg = OM7()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OM7"

    def test_omc_to_dict(self):
        seg = OMC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OMC"

    def test_omc_to_json(self):
        seg = OMC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OMC"

    def test_orc_to_dict(self):
        seg = ORC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ORC"

    def test_orc_to_json(self):
        seg = ORC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ORC"

    def test_org_to_dict(self):
        seg = ORG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ORG"

    def test_org_to_json(self):
        seg = ORG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ORG"

    def test_ovr_to_dict(self):
        seg = OVR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "OVR"

    def test_ovr_to_json(self):
        seg = OVR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "OVR"

    def test_pac_to_dict(self):
        seg = PAC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PAC"

    def test_pac_to_json(self):
        seg = PAC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PAC"

    def test_pce_to_dict(self):
        seg = PCE()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PCE"

    def test_pce_to_json(self):
        seg = PCE()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PCE"

    def test_pcr_to_dict(self):
        seg = PCR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PCR"

    def test_pcr_to_json(self):
        seg = PCR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PCR"

    def test_pd1_to_dict(self):
        seg = PD1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PD1"

    def test_pd1_to_json(self):
        seg = PD1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PD1"

    def test_pda_to_dict(self):
        seg = PDA()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PDA"

    def test_pda_to_json(self):
        seg = PDA()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PDA"

    def test_pdc_to_dict(self):
        seg = PDC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PDC"

    def test_pdc_to_json(self):
        seg = PDC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PDC"

    def test_peo_to_dict(self):
        seg = PEO()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PEO"

    def test_peo_to_json(self):
        seg = PEO()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PEO"

    def test_pes_to_dict(self):
        seg = PES()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PES"

    def test_pes_to_json(self):
        seg = PES()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PES"

    def test_pid_to_dict(self):
        seg = PID()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PID"

    def test_pid_to_json(self):
        seg = PID()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PID"

    def test_pkg_to_dict(self):
        seg = PKG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PKG"

    def test_pkg_to_json(self):
        seg = PKG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PKG"

    def test_pm1_to_dict(self):
        seg = PM1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PM1"

    def test_pm1_to_json(self):
        seg = PM1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PM1"

    def test_pmt_to_dict(self):
        seg = PMT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PMT"

    def test_pmt_to_json(self):
        seg = PMT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PMT"

    def test_pr1_to_dict(self):
        seg = PR1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PR1"

    def test_pr1_to_json(self):
        seg = PR1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PR1"

    def test_pra_to_dict(self):
        seg = PRA()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PRA"

    def test_pra_to_json(self):
        seg = PRA()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PRA"

    def test_prb_to_dict(self):
        seg = PRB()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PRB"

    def test_prb_to_json(self):
        seg = PRB()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PRB"

    def test_prc_to_dict(self):
        seg = PRC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PRC"

    def test_prc_to_json(self):
        seg = PRC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PRC"

    def test_prd_to_dict(self):
        seg = PRD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PRD"

    def test_prd_to_json(self):
        seg = PRD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PRD"

    def test_prt_to_dict(self):
        seg = PRT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PRT"

    def test_prt_to_json(self):
        seg = PRT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PRT"

    def test_psg_to_dict(self):
        seg = PSG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PSG"

    def test_psg_to_json(self):
        seg = PSG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PSG"

    def test_psh_to_dict(self):
        seg = PSH()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PSH"

    def test_psh_to_json(self):
        seg = PSH()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PSH"

    def test_psl_to_dict(self):
        seg = PSL()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PSL"

    def test_psl_to_json(self):
        seg = PSL()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PSL"

    def test_pss_to_dict(self):
        seg = PSS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PSS"

    def test_pss_to_json(self):
        seg = PSS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PSS"

    def test_pth_to_dict(self):
        seg = PTH()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PTH"

    def test_pth_to_json(self):
        seg = PTH()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PTH"

    def test_pv1_to_dict(self):
        seg = PV1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PV1"

    def test_pv1_to_json(self):
        seg = PV1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PV1"

    def test_pv2_to_dict(self):
        seg = PV2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PV2"

    def test_pv2_to_json(self):
        seg = PV2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PV2"

    def test_pye_to_dict(self):
        seg = PYE()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "PYE"

    def test_pye_to_json(self):
        seg = PYE()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "PYE"

    def test_qak_to_dict(self):
        seg = QAK()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "QAK"

    def test_qak_to_json(self):
        seg = QAK()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "QAK"

    def test_qid_to_dict(self):
        seg = QID()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "QID"

    def test_qid_to_json(self):
        seg = QID()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "QID"

    def test_qpd_to_dict(self):
        seg = QPD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "QPD"

    def test_qpd_to_json(self):
        seg = QPD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "QPD"

    def test_qri_to_dict(self):
        seg = QRI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "QRI"

    def test_qri_to_json(self):
        seg = QRI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "QRI"

    def test_rcp_to_dict(self):
        seg = RCP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RCP"

    def test_rcp_to_json(self):
        seg = RCP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RCP"

    def test_rdf_to_dict(self):
        seg = RDF()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RDF"

    def test_rdf_to_json(self):
        seg = RDF()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RDF"

    def test_rdt_to_dict(self):
        seg = RDT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RDT"

    def test_rdt_to_json(self):
        seg = RDT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RDT"

    def test_rel_to_dict(self):
        seg = REL()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "REL"

    def test_rel_to_json(self):
        seg = REL()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "REL"

    def test_rf1_to_dict(self):
        seg = RF1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RF1"

    def test_rf1_to_json(self):
        seg = RF1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RF1"

    def test_rfi_to_dict(self):
        seg = RFI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RFI"

    def test_rfi_to_json(self):
        seg = RFI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RFI"

    def test_rgs_to_dict(self):
        seg = RGS()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RGS"

    def test_rgs_to_json(self):
        seg = RGS()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RGS"

    def test_rmi_to_dict(self):
        seg = RMI()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RMI"

    def test_rmi_to_json(self):
        seg = RMI()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RMI"

    def test_rq1_to_dict(self):
        seg = RQ1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RQ1"

    def test_rq1_to_json(self):
        seg = RQ1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RQ1"

    def test_rqd_to_dict(self):
        seg = RQD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RQD"

    def test_rqd_to_json(self):
        seg = RQD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RQD"

    def test_rxa_to_dict(self):
        seg = RXA()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXA"

    def test_rxa_to_json(self):
        seg = RXA()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXA"

    def test_rxc_to_dict(self):
        seg = RXC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXC"

    def test_rxc_to_json(self):
        seg = RXC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXC"

    def test_rxd_to_dict(self):
        seg = RXD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXD"

    def test_rxd_to_json(self):
        seg = RXD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXD"

    def test_rxe_to_dict(self):
        seg = RXE()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXE"

    def test_rxe_to_json(self):
        seg = RXE()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXE"

    def test_rxg_to_dict(self):
        seg = RXG()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXG"

    def test_rxg_to_json(self):
        seg = RXG()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXG"

    def test_rxo_to_dict(self):
        seg = RXO()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXO"

    def test_rxo_to_json(self):
        seg = RXO()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXO"

    def test_rxr_to_dict(self):
        seg = RXR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXR"

    def test_rxr_to_json(self):
        seg = RXR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXR"

    def test_rxv_to_dict(self):
        seg = RXV()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "RXV"

    def test_rxv_to_json(self):
        seg = RXV()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "RXV"

    def test_sac_to_dict(self):
        seg = SAC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SAC"

    def test_sac_to_json(self):
        seg = SAC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SAC"

    def test_scd_to_dict(self):
        seg = SCD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SCD"

    def test_scd_to_json(self):
        seg = SCD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SCD"

    def test_sch_to_dict(self):
        seg = SCH()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SCH"

    def test_sch_to_json(self):
        seg = SCH()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SCH"

    def test_scp_to_dict(self):
        seg = SCP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SCP"

    def test_scp_to_json(self):
        seg = SCP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SCP"

    def test_sdd_to_dict(self):
        seg = SDD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SDD"

    def test_sdd_to_json(self):
        seg = SDD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SDD"

    def test_sft_to_dict(self):
        seg = SFT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SFT"

    def test_sft_to_json(self):
        seg = SFT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SFT"

    def test_sgh_to_dict(self):
        seg = SGH()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SGH"

    def test_sgh_to_json(self):
        seg = SGH()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SGH"

    def test_sgt_to_dict(self):
        seg = SGT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SGT"

    def test_sgt_to_json(self):
        seg = SGT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SGT"

    def test_shp_to_dict(self):
        seg = SHP()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SHP"

    def test_shp_to_json(self):
        seg = SHP()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SHP"

    def test_sid_to_dict(self):
        seg = SID()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SID"

    def test_sid_to_json(self):
        seg = SID()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SID"

    def test_slt_to_dict(self):
        seg = SLT()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SLT"

    def test_slt_to_json(self):
        seg = SLT()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SLT"

    def test_spm_to_dict(self):
        seg = SPM()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "SPM"

    def test_spm_to_json(self):
        seg = SPM()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "SPM"

    def test_stf_to_dict(self):
        seg = STF()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "STF"

    def test_stf_to_json(self):
        seg = STF()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "STF"

    def test_stz_to_dict(self):
        seg = STZ()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "STZ"

    def test_stz_to_json(self):
        seg = STZ()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "STZ"

    def test_tcc_to_dict(self):
        seg = TCC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "TCC"

    def test_tcc_to_json(self):
        seg = TCC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "TCC"

    def test_tcd_to_dict(self):
        seg = TCD()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "TCD"

    def test_tcd_to_json(self):
        seg = TCD()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "TCD"

    def test_tq1_to_dict(self):
        seg = TQ1()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "TQ1"

    def test_tq1_to_json(self):
        seg = TQ1()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "TQ1"

    def test_tq2_to_dict(self):
        seg = TQ2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "TQ2"

    def test_tq2_to_json(self):
        seg = TQ2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "TQ2"

    def test_txa_to_dict(self):
        seg = TXA()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "TXA"

    def test_txa_to_json(self):
        seg = TXA()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "TXA"

    def test_uac_to_dict(self):
        seg = UAC()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "UAC"

    def test_uac_to_json(self):
        seg = UAC()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "UAC"

    def test_ub2_to_dict(self):
        seg = UB2()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "UB2"

    def test_ub2_to_json(self):
        seg = UB2()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "UB2"

    def test_var_to_dict(self):
        seg = VAR()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "VAR"

    def test_var_to_json(self):
        seg = VAR()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "VAR"

    def test_vnd_to_dict(self):
        seg = VND()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "VND"

    def test_vnd_to_json(self):
        seg = VND()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "VND"

    def test_zl7_to_dict(self):
        seg = ZL7()
        d = seg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_segment_id") == "ZL7"

    def test_zl7_to_json(self):
        seg = ZL7()
        j = seg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_segment_id") == "ZL7"
