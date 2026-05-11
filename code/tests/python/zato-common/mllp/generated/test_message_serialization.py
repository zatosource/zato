from __future__ import annotations

import json
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


class TestMessageSerialization:
    """Test serialization methods for all message classes."""

    def test_ack_to_dict(self):
        msg = Ack()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ACK"

    def test_ack_to_json(self):
        msg = Ack()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ACK"

    def test_adt_a01_to_dict(self):
        msg = AdtA01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A01"

    def test_adt_a01_to_json(self):
        msg = AdtA01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A01"

    def test_adt_a02_to_dict(self):
        msg = AdtA02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A02"

    def test_adt_a02_to_json(self):
        msg = AdtA02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A02"

    def test_adt_a03_to_dict(self):
        msg = AdtA03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A03"

    def test_adt_a03_to_json(self):
        msg = AdtA03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A03"

    def test_adt_a05_to_dict(self):
        msg = AdtA05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A05"

    def test_adt_a05_to_json(self):
        msg = AdtA05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A05"

    def test_adt_a06_to_dict(self):
        msg = AdtA06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A06"

    def test_adt_a06_to_json(self):
        msg = AdtA06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A06"

    def test_adt_a09_to_dict(self):
        msg = AdtA09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A09"

    def test_adt_a09_to_json(self):
        msg = AdtA09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A09"

    def test_adt_a12_to_dict(self):
        msg = AdtA12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A12"

    def test_adt_a12_to_json(self):
        msg = AdtA12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A12"

    def test_adt_a15_to_dict(self):
        msg = AdtA15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A15"

    def test_adt_a15_to_json(self):
        msg = AdtA15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A15"

    def test_adt_a16_to_dict(self):
        msg = AdtA16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A16"

    def test_adt_a16_to_json(self):
        msg = AdtA16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A16"

    def test_adt_a17_to_dict(self):
        msg = AdtA17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A17"

    def test_adt_a17_to_json(self):
        msg = AdtA17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A17"

    def test_adt_a20_to_dict(self):
        msg = AdtA20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A20"

    def test_adt_a20_to_json(self):
        msg = AdtA20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A20"

    def test_adt_a21_to_dict(self):
        msg = AdtA21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A21"

    def test_adt_a21_to_json(self):
        msg = AdtA21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A21"

    def test_adt_a24_to_dict(self):
        msg = AdtA24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A24"

    def test_adt_a24_to_json(self):
        msg = AdtA24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A24"

    def test_adt_a37_to_dict(self):
        msg = AdtA37()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A37"

    def test_adt_a37_to_json(self):
        msg = AdtA37()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A37"

    def test_adt_a38_to_dict(self):
        msg = AdtA38()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A38"

    def test_adt_a38_to_json(self):
        msg = AdtA38()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A38"

    def test_adt_a39_to_dict(self):
        msg = AdtA39()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A39"

    def test_adt_a39_to_json(self):
        msg = AdtA39()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A39"

    def test_adt_a43_to_dict(self):
        msg = AdtA43()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A43"

    def test_adt_a43_to_json(self):
        msg = AdtA43()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A43"

    def test_adt_a44_to_dict(self):
        msg = AdtA44()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A44"

    def test_adt_a44_to_json(self):
        msg = AdtA44()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A44"

    def test_adt_a45_to_dict(self):
        msg = AdtA45()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A45"

    def test_adt_a45_to_json(self):
        msg = AdtA45()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A45"

    def test_adt_a50_to_dict(self):
        msg = AdtA50()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A50"

    def test_adt_a50_to_json(self):
        msg = AdtA50()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A50"

    def test_adt_a52_to_dict(self):
        msg = AdtA52()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A52"

    def test_adt_a52_to_json(self):
        msg = AdtA52()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A52"

    def test_adt_a54_to_dict(self):
        msg = AdtA54()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A54"

    def test_adt_a54_to_json(self):
        msg = AdtA54()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A54"

    def test_adt_a60_to_dict(self):
        msg = AdtA60()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A60"

    def test_adt_a60_to_json(self):
        msg = AdtA60()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A60"

    def test_adt_a61_to_dict(self):
        msg = AdtA61()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ADT_A61"

    def test_adt_a61_to_json(self):
        msg = AdtA61()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ADT_A61"

    def test_bar_p01_to_dict(self):
        msg = BarP01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P01"

    def test_bar_p01_to_json(self):
        msg = BarP01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P01"

    def test_bar_p02_to_dict(self):
        msg = BarP02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P02"

    def test_bar_p02_to_json(self):
        msg = BarP02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P02"

    def test_bar_p05_to_dict(self):
        msg = BarP05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P05"

    def test_bar_p05_to_json(self):
        msg = BarP05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P05"

    def test_bar_p06_to_dict(self):
        msg = BarP06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P06"

    def test_bar_p06_to_json(self):
        msg = BarP06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P06"

    def test_bar_p10_to_dict(self):
        msg = BarP10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P10"

    def test_bar_p10_to_json(self):
        msg = BarP10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P10"

    def test_bar_p12_to_dict(self):
        msg = BarP12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BAR_P12"

    def test_bar_p12_to_json(self):
        msg = BarP12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BAR_P12"

    def test_bps_o29_to_dict(self):
        msg = BpsO29()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BPS_O29"

    def test_bps_o29_to_json(self):
        msg = BpsO29()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BPS_O29"

    def test_brp_o30_to_dict(self):
        msg = BrpO30()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BRP_O30"

    def test_brp_o30_to_json(self):
        msg = BrpO30()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BRP_O30"

    def test_brt_o32_to_dict(self):
        msg = BrtO32()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BRT_O32"

    def test_brt_o32_to_json(self):
        msg = BrtO32()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BRT_O32"

    def test_bts_o31_to_dict(self):
        msg = BtsO31()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "BTS_O31"

    def test_bts_o31_to_json(self):
        msg = BtsO31()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "BTS_O31"

    def test_ccf_i22_to_dict(self):
        msg = CcfI22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCF_I22"

    def test_ccf_i22_to_json(self):
        msg = CcfI22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCF_I22"

    def test_cci_i22_to_dict(self):
        msg = CciI22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCI_I22"

    def test_cci_i22_to_json(self):
        msg = CciI22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCI_I22"

    def test_ccm_i21_to_dict(self):
        msg = CcmI21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCM_I21"

    def test_ccm_i21_to_json(self):
        msg = CcmI21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCM_I21"

    def test_ccq_i19_to_dict(self):
        msg = CcqI19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCQ_I19"

    def test_ccq_i19_to_json(self):
        msg = CcqI19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCQ_I19"

    def test_ccr_i16_to_dict(self):
        msg = CcrI16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCR_I16"

    def test_ccr_i16_to_json(self):
        msg = CcrI16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCR_I16"

    def test_ccu_i20_to_dict(self):
        msg = CcuI20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CCU_I20"

    def test_ccu_i20_to_json(self):
        msg = CcuI20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CCU_I20"

    def test_cqu_i19_to_dict(self):
        msg = CquI19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CQU_I19"

    def test_cqu_i19_to_json(self):
        msg = CquI19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CQU_I19"

    def test_crm_c01_to_dict(self):
        msg = CrmC01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CRM_C01"

    def test_crm_c01_to_json(self):
        msg = CrmC01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CRM_C01"

    def test_csu_c09_to_dict(self):
        msg = CsuC09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "CSU_C09"

    def test_csu_c09_to_json(self):
        msg = CsuC09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "CSU_C09"

    def test_dbc_o41_to_dict(self):
        msg = DbcO41()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DBC_O41"

    def test_dbc_o41_to_json(self):
        msg = DbcO41()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DBC_O41"

    def test_dbc_o42_to_dict(self):
        msg = DbcO42()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DBC_O42"

    def test_dbc_o42_to_json(self):
        msg = DbcO42()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DBC_O42"

    def test_del_o46_to_dict(self):
        msg = DelO46()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DEL_O46"

    def test_del_o46_to_json(self):
        msg = DelO46()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DEL_O46"

    def test_deo_o45_to_dict(self):
        msg = DeoO45()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DEO_O45"

    def test_deo_o45_to_json(self):
        msg = DeoO45()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DEO_O45"

    def test_der_o44_to_dict(self):
        msg = DerO44()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DER_O44"

    def test_der_o44_to_json(self):
        msg = DerO44()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DER_O44"

    def test_dft_p03_to_dict(self):
        msg = DftP03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DFT_P03"

    def test_dft_p03_to_json(self):
        msg = DftP03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DFT_P03"

    def test_dft_p11_to_dict(self):
        msg = DftP11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DFT_P11"

    def test_dft_p11_to_json(self):
        msg = DftP11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DFT_P11"

    def test_dpr_o48_to_dict(self):
        msg = DprO48()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DPR_O48"

    def test_dpr_o48_to_json(self):
        msg = DprO48()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DPR_O48"

    def test_drc_o47_to_dict(self):
        msg = DrcO47()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DRC_O47"

    def test_drc_o47_to_json(self):
        msg = DrcO47()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DRC_O47"

    def test_drg_o43_to_dict(self):
        msg = DrgO43()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "DRG_O43"

    def test_drg_o43_to_json(self):
        msg = DrgO43()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "DRG_O43"

    def test_eac_u07_to_dict(self):
        msg = EacU07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EAC_U07"

    def test_eac_u07_to_json(self):
        msg = EacU07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EAC_U07"

    def test_ean_u09_to_dict(self):
        msg = EanU09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EAN_U09"

    def test_ean_u09_to_json(self):
        msg = EanU09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EAN_U09"

    def test_ear_u08_to_dict(self):
        msg = EarU08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EAR_U08"

    def test_ear_u08_to_json(self):
        msg = EarU08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EAR_U08"

    def test_ehc_e01_to_dict(self):
        msg = EhcE01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E01"

    def test_ehc_e01_to_json(self):
        msg = EhcE01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E01"

    def test_ehc_e02_to_dict(self):
        msg = EhcE02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E02"

    def test_ehc_e02_to_json(self):
        msg = EhcE02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E02"

    def test_ehc_e04_to_dict(self):
        msg = EhcE04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E04"

    def test_ehc_e04_to_json(self):
        msg = EhcE04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E04"

    def test_ehc_e10_to_dict(self):
        msg = EhcE10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E10"

    def test_ehc_e10_to_json(self):
        msg = EhcE10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E10"

    def test_ehc_e12_to_dict(self):
        msg = EhcE12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E12"

    def test_ehc_e12_to_json(self):
        msg = EhcE12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E12"

    def test_ehc_e13_to_dict(self):
        msg = EhcE13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E13"

    def test_ehc_e13_to_json(self):
        msg = EhcE13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E13"

    def test_ehc_e15_to_dict(self):
        msg = EhcE15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E15"

    def test_ehc_e15_to_json(self):
        msg = EhcE15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E15"

    def test_ehc_e20_to_dict(self):
        msg = EhcE20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E20"

    def test_ehc_e20_to_json(self):
        msg = EhcE20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E20"

    def test_ehc_e21_to_dict(self):
        msg = EhcE21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E21"

    def test_ehc_e21_to_json(self):
        msg = EhcE21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E21"

    def test_ehc_e24_to_dict(self):
        msg = EhcE24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "EHC_E24"

    def test_ehc_e24_to_json(self):
        msg = EhcE24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "EHC_E24"

    def test_esr_u02_to_dict(self):
        msg = EsrU02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ESR_U02"

    def test_esr_u02_to_json(self):
        msg = EsrU02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ESR_U02"

    def test_esu_u01_to_dict(self):
        msg = EsuU01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ESU_U01"

    def test_esu_u01_to_json(self):
        msg = EsuU01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ESU_U01"

    def test_inr_u06_to_dict(self):
        msg = InrU06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "INR_U06"

    def test_inr_u06_to_json(self):
        msg = InrU06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "INR_U06"

    def test_inr_u14_to_dict(self):
        msg = InrU14()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "INR_U14"

    def test_inr_u14_to_json(self):
        msg = InrU14()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "INR_U14"

    def test_inu_u05_to_dict(self):
        msg = InuU05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "INU_U05"

    def test_inu_u05_to_json(self):
        msg = InuU05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "INU_U05"

    def test_lsu_u12_to_dict(self):
        msg = LsuU12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "LSU_U12"

    def test_lsu_u12_to_json(self):
        msg = LsuU12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "LSU_U12"

    def test_mdm_t01_to_dict(self):
        msg = MdmT01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MDM_T01"

    def test_mdm_t01_to_json(self):
        msg = MdmT01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MDM_T01"

    def test_mdm_t02_to_dict(self):
        msg = MdmT02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MDM_T02"

    def test_mdm_t02_to_json(self):
        msg = MdmT02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MDM_T02"

    def test_mfk_m01_to_dict(self):
        msg = MfkM01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFK_M01"

    def test_mfk_m01_to_json(self):
        msg = MfkM01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFK_M01"

    def test_mfn_m02_to_dict(self):
        msg = MfnM02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M02"

    def test_mfn_m02_to_json(self):
        msg = MfnM02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M02"

    def test_mfn_m04_to_dict(self):
        msg = MfnM04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M04"

    def test_mfn_m04_to_json(self):
        msg = MfnM04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M04"

    def test_mfn_m05_to_dict(self):
        msg = MfnM05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M05"

    def test_mfn_m05_to_json(self):
        msg = MfnM05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M05"

    def test_mfn_m06_to_dict(self):
        msg = MfnM06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M06"

    def test_mfn_m06_to_json(self):
        msg = MfnM06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M06"

    def test_mfn_m07_to_dict(self):
        msg = MfnM07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M07"

    def test_mfn_m07_to_json(self):
        msg = MfnM07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M07"

    def test_mfn_m08_to_dict(self):
        msg = MfnM08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M08"

    def test_mfn_m08_to_json(self):
        msg = MfnM08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M08"

    def test_mfn_m09_to_dict(self):
        msg = MfnM09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M09"

    def test_mfn_m09_to_json(self):
        msg = MfnM09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M09"

    def test_mfn_m10_to_dict(self):
        msg = MfnM10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M10"

    def test_mfn_m10_to_json(self):
        msg = MfnM10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M10"

    def test_mfn_m11_to_dict(self):
        msg = MfnM11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M11"

    def test_mfn_m11_to_json(self):
        msg = MfnM11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M11"

    def test_mfn_m12_to_dict(self):
        msg = MfnM12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M12"

    def test_mfn_m12_to_json(self):
        msg = MfnM12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M12"

    def test_mfn_m13_to_dict(self):
        msg = MfnM13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M13"

    def test_mfn_m13_to_json(self):
        msg = MfnM13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M13"

    def test_mfn_m15_to_dict(self):
        msg = MfnM15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M15"

    def test_mfn_m15_to_json(self):
        msg = MfnM15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M15"

    def test_mfn_m16_to_dict(self):
        msg = MfnM16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M16"

    def test_mfn_m16_to_json(self):
        msg = MfnM16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M16"

    def test_mfn_m17_to_dict(self):
        msg = MfnM17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M17"

    def test_mfn_m17_to_json(self):
        msg = MfnM17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M17"

    def test_mfn_m18_to_dict(self):
        msg = MfnM18()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M18"

    def test_mfn_m18_to_json(self):
        msg = MfnM18()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M18"

    def test_mfn_m19_to_dict(self):
        msg = MfnM19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_M19"

    def test_mfn_m19_to_json(self):
        msg = MfnM19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_M19"

    def test_mfn_znn_to_dict(self):
        msg = MfnZnn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "MFN_Znn"

    def test_mfn_znn_to_json(self):
        msg = MfnZnn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "MFN_Znn"

    def test_nmd_n02_to_dict(self):
        msg = NmdN02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "NMD_N02"

    def test_nmd_n02_to_json(self):
        msg = NmdN02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "NMD_N02"

    def test_omb_o27_to_dict(self):
        msg = OmbO27()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMB_O27"

    def test_omb_o27_to_json(self):
        msg = OmbO27()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMB_O27"

    def test_omd_o03_to_dict(self):
        msg = OmdO03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMD_O03"

    def test_omd_o03_to_json(self):
        msg = OmdO03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMD_O03"

    def test_omg_o19_to_dict(self):
        msg = OmgO19()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMG_O19"

    def test_omg_o19_to_json(self):
        msg = OmgO19()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMG_O19"

    def test_omi_o23_to_dict(self):
        msg = OmiO23()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMI_O23"

    def test_omi_o23_to_json(self):
        msg = OmiO23()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMI_O23"

    def test_oml_o21_to_dict(self):
        msg = OmlO21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O21"

    def test_oml_o21_to_json(self):
        msg = OmlO21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O21"

    def test_oml_o33_to_dict(self):
        msg = OmlO33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O33"

    def test_oml_o33_to_json(self):
        msg = OmlO33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O33"

    def test_oml_o35_to_dict(self):
        msg = OmlO35()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O35"

    def test_oml_o35_to_json(self):
        msg = OmlO35()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O35"

    def test_oml_o39_to_dict(self):
        msg = OmlO39()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O39"

    def test_oml_o39_to_json(self):
        msg = OmlO39()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O39"

    def test_oml_o59_to_dict(self):
        msg = OmlO59()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OML_O59"

    def test_oml_o59_to_json(self):
        msg = OmlO59()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OML_O59"

    def test_omn_o07_to_dict(self):
        msg = OmnO07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMN_O07"

    def test_omn_o07_to_json(self):
        msg = OmnO07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMN_O07"

    def test_omp_o09_to_dict(self):
        msg = OmpO09()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMP_O09"

    def test_omp_o09_to_json(self):
        msg = OmpO09()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMP_O09"

    def test_omq_o57_to_dict(self):
        msg = OmqO57()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMQ_O57"

    def test_omq_o57_to_json(self):
        msg = OmqO57()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMQ_O57"

    def test_oms_o05_to_dict(self):
        msg = OmsO05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OMS_O05"

    def test_oms_o05_to_json(self):
        msg = OmsO05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OMS_O05"

    def test_opl_o37_to_dict(self):
        msg = OplO37()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OPL_O37"

    def test_opl_o37_to_json(self):
        msg = OplO37()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OPL_O37"

    def test_opr_o38_to_dict(self):
        msg = OprO38()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OPR_O38"

    def test_opr_o38_to_json(self):
        msg = OprO38()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OPR_O38"

    def test_opu_r25_to_dict(self):
        msg = OpuR25()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OPU_R25"

    def test_opu_r25_to_json(self):
        msg = OpuR25()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OPU_R25"

    def test_ora_r33_to_dict(self):
        msg = OraR33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORA_R33"

    def test_ora_r33_to_json(self):
        msg = OraR33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORA_R33"

    def test_ora_r41_to_dict(self):
        msg = OraR41()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORA_R41"

    def test_ora_r41_to_json(self):
        msg = OraR41()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORA_R41"

    def test_orb_o28_to_dict(self):
        msg = OrbO28()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORB_O28"

    def test_orb_o28_to_json(self):
        msg = OrbO28()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORB_O28"

    def test_ord_o04_to_dict(self):
        msg = OrdO04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORD_O04"

    def test_ord_o04_to_json(self):
        msg = OrdO04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORD_O04"

    def test_org_o20_to_dict(self):
        msg = OrgO20()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORG_O20"

    def test_org_o20_to_json(self):
        msg = OrgO20()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORG_O20"

    def test_ori_o24_to_dict(self):
        msg = OriO24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORI_O24"

    def test_ori_o24_to_json(self):
        msg = OriO24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORI_O24"

    def test_orl_o22_to_dict(self):
        msg = OrlO22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O22"

    def test_orl_o22_to_json(self):
        msg = OrlO22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O22"

    def test_orl_o34_to_dict(self):
        msg = OrlO34()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O34"

    def test_orl_o34_to_json(self):
        msg = OrlO34()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O34"

    def test_orl_o36_to_dict(self):
        msg = OrlO36()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O36"

    def test_orl_o36_to_json(self):
        msg = OrlO36()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O36"

    def test_orl_o40_to_dict(self):
        msg = OrlO40()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O40"

    def test_orl_o40_to_json(self):
        msg = OrlO40()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O40"

    def test_orl_o53_to_dict(self):
        msg = OrlO53()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O53"

    def test_orl_o53_to_json(self):
        msg = OrlO53()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O53"

    def test_orl_o54_to_dict(self):
        msg = OrlO54()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O54"

    def test_orl_o54_to_json(self):
        msg = OrlO54()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O54"

    def test_orl_o55_to_dict(self):
        msg = OrlO55()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O55"

    def test_orl_o55_to_json(self):
        msg = OrlO55()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O55"

    def test_orl_o56_to_dict(self):
        msg = OrlO56()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORL_O56"

    def test_orl_o56_to_json(self):
        msg = OrlO56()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORL_O56"

    def test_orm_o01_to_dict(self):
        msg = OrmO01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORM_O01"

    def test_orm_o01_to_json(self):
        msg = OrmO01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORM_O01"

    def test_orn_o08_to_dict(self):
        msg = OrnO08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORN_O08"

    def test_orn_o08_to_json(self):
        msg = OrnO08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORN_O08"

    def test_orp_o10_to_dict(self):
        msg = OrpO10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORP_O10"

    def test_orp_o10_to_json(self):
        msg = OrpO10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORP_O10"

    def test_ors_o06_to_dict(self):
        msg = OrsO06()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORS_O06"

    def test_ors_o06_to_json(self):
        msg = OrsO06()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORS_O06"

    def test_oru_r01_to_dict(self):
        msg = OruR01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORU_R01"

    def test_oru_r01_to_json(self):
        msg = OruR01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORU_R01"

    def test_oru_r30_to_dict(self):
        msg = OruR30()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORU_R30"

    def test_oru_r30_to_json(self):
        msg = OruR30()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORU_R30"

    def test_orx_o58_to_dict(self):
        msg = OrxO58()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "ORX_O58"

    def test_orx_o58_to_json(self):
        msg = OrxO58()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "ORX_O58"

    def test_osm_r26_to_dict(self):
        msg = OsmR26()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OSM_R26"

    def test_osm_r26_to_json(self):
        msg = OsmR26()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OSM_R26"

    def test_osu_o51_to_dict(self):
        msg = OsuO51()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OSU_O51"

    def test_osu_o51_to_json(self):
        msg = OsuO51()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OSU_O51"

    def test_osu_o52_to_dict(self):
        msg = OsuO52()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OSU_O52"

    def test_osu_o52_to_json(self):
        msg = OsuO52()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OSU_O52"

    def test_oul_r22_to_dict(self):
        msg = OulR22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OUL_R22"

    def test_oul_r22_to_json(self):
        msg = OulR22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OUL_R22"

    def test_oul_r23_to_dict(self):
        msg = OulR23()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OUL_R23"

    def test_oul_r23_to_json(self):
        msg = OulR23()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OUL_R23"

    def test_oul_r24_to_dict(self):
        msg = OulR24()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "OUL_R24"

    def test_oul_r24_to_json(self):
        msg = OulR24()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "OUL_R24"

    def test_pex_p07_to_dict(self):
        msg = PexP07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PEX_P07"

    def test_pex_p07_to_json(self):
        msg = PexP07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PEX_P07"

    def test_pgl_pc6_to_dict(self):
        msg = PglPc6()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PGL_PC6"

    def test_pgl_pc6_to_json(self):
        msg = PglPc6()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PGL_PC6"

    def test_pmu_b01_to_dict(self):
        msg = PmuB01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B01"

    def test_pmu_b01_to_json(self):
        msg = PmuB01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B01"

    def test_pmu_b03_to_dict(self):
        msg = PmuB03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B03"

    def test_pmu_b03_to_json(self):
        msg = PmuB03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B03"

    def test_pmu_b04_to_dict(self):
        msg = PmuB04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B04"

    def test_pmu_b04_to_json(self):
        msg = PmuB04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B04"

    def test_pmu_b07_to_dict(self):
        msg = PmuB07()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B07"

    def test_pmu_b07_to_json(self):
        msg = PmuB07()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B07"

    def test_pmu_b08_to_dict(self):
        msg = PmuB08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PMU_B08"

    def test_pmu_b08_to_json(self):
        msg = PmuB08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PMU_B08"

    def test_ppg_pcg_to_dict(self):
        msg = PpgPcg()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PPG_PCG"

    def test_ppg_pcg_to_json(self):
        msg = PpgPcg()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PPG_PCG"

    def test_ppp_pcb_to_dict(self):
        msg = PppPcb()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PPP_PCB"

    def test_ppp_pcb_to_json(self):
        msg = PppPcb()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PPP_PCB"

    def test_ppr_pc1_to_dict(self):
        msg = PprPc1()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "PPR_PC1"

    def test_ppr_pc1_to_json(self):
        msg = PprPc1()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "PPR_PC1"

    def test_qbp_e03_to_dict(self):
        msg = QbpE03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_E03"

    def test_qbp_e03_to_json(self):
        msg = QbpE03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_E03"

    def test_qbp_e22_to_dict(self):
        msg = QbpE22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_E22"

    def test_qbp_e22_to_json(self):
        msg = QbpE22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_E22"

    def test_qbp_o33_to_dict(self):
        msg = QbpO33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_O33"

    def test_qbp_o33_to_json(self):
        msg = QbpO33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_O33"

    def test_qbp_o34_to_dict(self):
        msg = QbpO34()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_O34"

    def test_qbp_o34_to_json(self):
        msg = QbpO34()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_O34"

    def test_qbp_q11_to_dict(self):
        msg = QbpQ11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q11"

    def test_qbp_q11_to_json(self):
        msg = QbpQ11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q11"

    def test_qbp_q13_to_dict(self):
        msg = QbpQ13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q13"

    def test_qbp_q13_to_json(self):
        msg = QbpQ13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q13"

    def test_qbp_q15_to_dict(self):
        msg = QbpQ15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q15"

    def test_qbp_q15_to_json(self):
        msg = QbpQ15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q15"

    def test_qbp_q21_to_dict(self):
        msg = QbpQ21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Q21"

    def test_qbp_q21_to_json(self):
        msg = QbpQ21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Q21"

    def test_qbp_qnn_to_dict(self):
        msg = QbpQnn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Qnn"

    def test_qbp_qnn_to_json(self):
        msg = QbpQnn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Qnn"

    def test_qbp_z73_to_dict(self):
        msg = QbpZ73()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QBP_Z73"

    def test_qbp_z73_to_json(self):
        msg = QbpZ73()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QBP_Z73"

    def test_qcn_j01_to_dict(self):
        msg = QcnJ01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QCN_J01"

    def test_qcn_j01_to_json(self):
        msg = QcnJ01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QCN_J01"

    def test_qsb_q16_to_dict(self):
        msg = QsbQ16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QSB_Q16"

    def test_qsb_q16_to_json(self):
        msg = QsbQ16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QSB_Q16"

    def test_qvr_q17_to_dict(self):
        msg = QvrQ17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "QVR_Q17"

    def test_qvr_q17_to_json(self):
        msg = QvrQ17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "QVR_Q17"

    def test_ras_o17_to_dict(self):
        msg = RasO17()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RAS_O17"

    def test_ras_o17_to_json(self):
        msg = RasO17()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RAS_O17"

    def test_rcv_o59_to_dict(self):
        msg = RcvO59()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RCV_O59"

    def test_rcv_o59_to_json(self):
        msg = RcvO59()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RCV_O59"

    def test_rde_o11_to_dict(self):
        msg = RdeO11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDE_O11"

    def test_rde_o11_to_json(self):
        msg = RdeO11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDE_O11"

    def test_rde_o49_to_dict(self):
        msg = RdeO49()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDE_O49"

    def test_rde_o49_to_json(self):
        msg = RdeO49()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDE_O49"

    def test_rdr_rdr_to_dict(self):
        msg = RdrRdr()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDR_RDR"

    def test_rdr_rdr_to_json(self):
        msg = RdrRdr()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDR_RDR"

    def test_rds_o13_to_dict(self):
        msg = RdsO13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDS_O13"

    def test_rds_o13_to_json(self):
        msg = RdsO13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDS_O13"

    def test_rdy_k15_to_dict(self):
        msg = RdyK15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDY_K15"

    def test_rdy_k15_to_json(self):
        msg = RdyK15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDY_K15"

    def test_rdy_z80_to_dict(self):
        msg = RdyZ80()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RDY_Z80"

    def test_rdy_z80_to_json(self):
        msg = RdyZ80()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RDY_Z80"

    def test_ref_i12_to_dict(self):
        msg = RefI12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "REF_I12"

    def test_ref_i12_to_json(self):
        msg = RefI12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "REF_I12"

    def test_rgv_o15_to_dict(self):
        msg = RgvO15()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RGV_O15"

    def test_rgv_o15_to_json(self):
        msg = RgvO15()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RGV_O15"

    def test_rpa_i08_to_dict(self):
        msg = RpaI08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPA_I08"

    def test_rpa_i08_to_json(self):
        msg = RpaI08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPA_I08"

    def test_rpi_i01_to_dict(self):
        msg = RpiI01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPI_I01"

    def test_rpi_i01_to_json(self):
        msg = RpiI01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPI_I01"

    def test_rpi_i04_to_dict(self):
        msg = RpiI04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPI_I04"

    def test_rpi_i04_to_json(self):
        msg = RpiI04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPI_I04"

    def test_rpl_i02_to_dict(self):
        msg = RplI02()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPL_I02"

    def test_rpl_i02_to_json(self):
        msg = RplI02()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPL_I02"

    def test_rpr_i03_to_dict(self):
        msg = RprI03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RPR_I03"

    def test_rpr_i03_to_json(self):
        msg = RprI03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RPR_I03"

    def test_rqa_i08_to_dict(self):
        msg = RqaI08()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RQA_I08"

    def test_rqa_i08_to_json(self):
        msg = RqaI08()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RQA_I08"

    def test_rqi_i01_to_dict(self):
        msg = RqiI01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RQI_I01"

    def test_rqi_i01_to_json(self):
        msg = RqiI01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RQI_I01"

    def test_rqp_i04_to_dict(self):
        msg = RqpI04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RQP_I04"

    def test_rqp_i04_to_json(self):
        msg = RqpI04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RQP_I04"

    def test_rra_o18_to_dict(self):
        msg = RraO18()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRA_O18"

    def test_rra_o18_to_json(self):
        msg = RraO18()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRA_O18"

    def test_rrd_o14_to_dict(self):
        msg = RrdO14()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRD_O14"

    def test_rrd_o14_to_json(self):
        msg = RrdO14()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRD_O14"

    def test_rre_o12_to_dict(self):
        msg = RreO12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRE_O12"

    def test_rre_o12_to_json(self):
        msg = RreO12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRE_O12"

    def test_rre_o50_to_dict(self):
        msg = RreO50()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRE_O50"

    def test_rre_o50_to_json(self):
        msg = RreO50()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRE_O50"

    def test_rrg_o16_to_dict(self):
        msg = RrgO16()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRG_O16"

    def test_rrg_o16_to_json(self):
        msg = RrgO16()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRG_O16"

    def test_rri_i12_to_dict(self):
        msg = RriI12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RRI_I12"

    def test_rri_i12_to_json(self):
        msg = RriI12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RRI_I12"

    def test_rsp_e03_to_dict(self):
        msg = RspE03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_E03"

    def test_rsp_e03_to_json(self):
        msg = RspE03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_E03"

    def test_rsp_e22_to_dict(self):
        msg = RspE22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_E22"

    def test_rsp_e22_to_json(self):
        msg = RspE22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_E22"

    def test_rsp_k11_to_dict(self):
        msg = RspK11()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K11"

    def test_rsp_k11_to_json(self):
        msg = RspK11()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K11"

    def test_rsp_k21_to_dict(self):
        msg = RspK21()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K21"

    def test_rsp_k21_to_json(self):
        msg = RspK21()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K21"

    def test_rsp_k22_to_dict(self):
        msg = RspK22()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K22"

    def test_rsp_k22_to_json(self):
        msg = RspK22()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K22"

    def test_rsp_k23_to_dict(self):
        msg = RspK23()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K23"

    def test_rsp_k23_to_json(self):
        msg = RspK23()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K23"

    def test_rsp_k25_to_dict(self):
        msg = RspK25()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K25"

    def test_rsp_k25_to_json(self):
        msg = RspK25()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K25"

    def test_rsp_k31_to_dict(self):
        msg = RspK31()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K31"

    def test_rsp_k31_to_json(self):
        msg = RspK31()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K31"

    def test_rsp_k32_to_dict(self):
        msg = RspK32()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_K32"

    def test_rsp_k32_to_json(self):
        msg = RspK32()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_K32"

    def test_rsp_o33_to_dict(self):
        msg = RspO33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_O33"

    def test_rsp_o33_to_json(self):
        msg = RspO33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_O33"

    def test_rsp_o34_to_dict(self):
        msg = RspO34()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_O34"

    def test_rsp_o34_to_json(self):
        msg = RspO34()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_O34"

    def test_rsp_z82_to_dict(self):
        msg = RspZ82()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z82"

    def test_rsp_z82_to_json(self):
        msg = RspZ82()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z82"

    def test_rsp_z84_to_dict(self):
        msg = RspZ84()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z84"

    def test_rsp_z84_to_json(self):
        msg = RspZ84()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z84"

    def test_rsp_z86_to_dict(self):
        msg = RspZ86()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z86"

    def test_rsp_z86_to_json(self):
        msg = RspZ86()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z86"

    def test_rsp_z88_to_dict(self):
        msg = RspZ88()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z88"

    def test_rsp_z88_to_json(self):
        msg = RspZ88()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z88"

    def test_rsp_z90_to_dict(self):
        msg = RspZ90()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Z90"

    def test_rsp_z90_to_json(self):
        msg = RspZ90()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Z90"

    def test_rsp_znn_to_dict(self):
        msg = RspZnn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RSP_Znn"

    def test_rsp_znn_to_json(self):
        msg = RspZnn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RSP_Znn"

    def test_rtb_k13_to_dict(self):
        msg = RtbK13()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RTB_K13"

    def test_rtb_k13_to_json(self):
        msg = RtbK13()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RTB_K13"

    def test_rtb_knn_to_dict(self):
        msg = RtbKnn()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RTB_Knn"

    def test_rtb_knn_to_json(self):
        msg = RtbKnn()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RTB_Knn"

    def test_rtb_z74_to_dict(self):
        msg = RtbZ74()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "RTB_Z74"

    def test_rtb_z74_to_json(self):
        msg = RtbZ74()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "RTB_Z74"

    def test_sdr_s31_to_dict(self):
        msg = SdrS31()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SDR_S31"

    def test_sdr_s31_to_json(self):
        msg = SdrS31()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SDR_S31"

    def test_sdr_s32_to_dict(self):
        msg = SdrS32()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SDR_S32"

    def test_sdr_s32_to_json(self):
        msg = SdrS32()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SDR_S32"

    def test_siu_s12_to_dict(self):
        msg = SiuS12()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SIU_S12"

    def test_siu_s12_to_json(self):
        msg = SiuS12()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SIU_S12"

    def test_slr_s28_to_dict(self):
        msg = SlrS28()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SLR_S28"

    def test_slr_s28_to_json(self):
        msg = SlrS28()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SLR_S28"

    def test_srm_s01_to_dict(self):
        msg = SrmS01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SRM_S01"

    def test_srm_s01_to_json(self):
        msg = SrmS01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SRM_S01"

    def test_srr_s01_to_dict(self):
        msg = SrrS01()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SRR_S01"

    def test_srr_s01_to_json(self):
        msg = SrrS01()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SRR_S01"

    def test_ssr_u04_to_dict(self):
        msg = SsrU04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SSR_U04"

    def test_ssr_u04_to_json(self):
        msg = SsrU04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SSR_U04"

    def test_ssu_u03_to_dict(self):
        msg = SsuU03()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "SSU_U03"

    def test_ssu_u03_to_json(self):
        msg = SsuU03()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "SSU_U03"

    def test_stc_s33_to_dict(self):
        msg = StcS33()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "STC_S33"

    def test_stc_s33_to_json(self):
        msg = StcS33()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "STC_S33"

    def test_tcu_u10_to_dict(self):
        msg = TcuU10()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "TCU_U10"

    def test_tcu_u10_to_json(self):
        msg = TcuU10()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "TCU_U10"

    def test_udm_q05_to_dict(self):
        msg = UdmQ05()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "UDM_Q05"

    def test_udm_q05_to_json(self):
        msg = UdmQ05()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "UDM_Q05"

    def test_vxu_v04_to_dict(self):
        msg = VxuV04()
        d = msg.to_dict()
        assert isinstance(d, dict)
        assert d.get("_structure_id") == "VXU_V04"

    def test_vxu_v04_to_json(self):
        msg = VxuV04()
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed.get("_structure_id") == "VXU_V04"
