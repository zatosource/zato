from __future__ import annotations

from zato.hl7v2.tests.fakers.msg_ack import fake_ack
from zato.hl7v2.tests.fakers.msg_adt import fake_adta01
from zato.hl7v2.tests.fakers.msg_adt import fake_adta02
from zato.hl7v2.tests.fakers.msg_adt import fake_adta03
from zato.hl7v2.tests.fakers.msg_adt import fake_adta05
from zato.hl7v2.tests.fakers.msg_adt import fake_adta06
from zato.hl7v2.tests.fakers.msg_adt import fake_adta09
from zato.hl7v2.tests.fakers.msg_adt import fake_adta12
from zato.hl7v2.tests.fakers.msg_adt import fake_adta15
from zato.hl7v2.tests.fakers.msg_adt import fake_adta16
from zato.hl7v2.tests.fakers.msg_adt import fake_adta17
from zato.hl7v2.tests.fakers.msg_adt import fake_adta20
from zato.hl7v2.tests.fakers.msg_adt import fake_adta21
from zato.hl7v2.tests.fakers.msg_adt import fake_adta24
from zato.hl7v2.tests.fakers.msg_adt import fake_adta37
from zato.hl7v2.tests.fakers.msg_adt import fake_adta38
from zato.hl7v2.tests.fakers.msg_adt import fake_adta39
from zato.hl7v2.tests.fakers.msg_adt import fake_adta43
from zato.hl7v2.tests.fakers.msg_adt import fake_adta44
from zato.hl7v2.tests.fakers.msg_adt import fake_adta45
from zato.hl7v2.tests.fakers.msg_adt import fake_adta50
from zato.hl7v2.tests.fakers.msg_adt import fake_adta52
from zato.hl7v2.tests.fakers.msg_adt import fake_adta54
from zato.hl7v2.tests.fakers.msg_adt import fake_adta60
from zato.hl7v2.tests.fakers.msg_adt import fake_adta61
from zato.hl7v2.tests.fakers.msg_bar import fake_barp01
from zato.hl7v2.tests.fakers.msg_bar import fake_barp02
from zato.hl7v2.tests.fakers.msg_bar import fake_barp05
from zato.hl7v2.tests.fakers.msg_bar import fake_barp06
from zato.hl7v2.tests.fakers.msg_bar import fake_barp10
from zato.hl7v2.tests.fakers.msg_bar import fake_barp12
from zato.hl7v2.tests.fakers.msg_bps import fake_bpso29
from zato.hl7v2.tests.fakers.msg_brp import fake_brpo30
from zato.hl7v2.tests.fakers.msg_brt import fake_brto32
from zato.hl7v2.tests.fakers.msg_bts import fake_btso31
from zato.hl7v2.tests.fakers.msg_ccf import fake_ccfi22
from zato.hl7v2.tests.fakers.msg_cci import fake_ccii22
from zato.hl7v2.tests.fakers.msg_ccm import fake_ccmi21
from zato.hl7v2.tests.fakers.msg_ccq import fake_ccqi19
from zato.hl7v2.tests.fakers.msg_ccr import fake_ccri16
from zato.hl7v2.tests.fakers.msg_ccu import fake_ccui20
from zato.hl7v2.tests.fakers.msg_cqu import fake_cqui19
from zato.hl7v2.tests.fakers.msg_crm import fake_crmc01
from zato.hl7v2.tests.fakers.msg_csu import fake_csuc09
from zato.hl7v2.tests.fakers.msg_dbc import fake_dbco41
from zato.hl7v2.tests.fakers.msg_dbc import fake_dbco42
from zato.hl7v2.tests.fakers.msg_del import fake_delo46
from zato.hl7v2.tests.fakers.msg_deo import fake_deoo45
from zato.hl7v2.tests.fakers.msg_der import fake_dero44
from zato.hl7v2.tests.fakers.msg_dft import fake_dftp03
from zato.hl7v2.tests.fakers.msg_dft import fake_dftp11
from zato.hl7v2.tests.fakers.msg_dpr import fake_dpro48
from zato.hl7v2.tests.fakers.msg_drc import fake_drco47
from zato.hl7v2.tests.fakers.msg_drg import fake_drgo43
from zato.hl7v2.tests.fakers.msg_eac import fake_eacu07
from zato.hl7v2.tests.fakers.msg_ean import fake_eanu09
from zato.hl7v2.tests.fakers.msg_ear import fake_earu08
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce01
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce02
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce04
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce10
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce12
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce13
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce15
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce20
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce21
from zato.hl7v2.tests.fakers.msg_ehc import fake_ehce24
from zato.hl7v2.tests.fakers.msg_esr import fake_esru02
from zato.hl7v2.tests.fakers.msg_esu import fake_esuu01
from zato.hl7v2.tests.fakers.msg_inr import fake_inru06
from zato.hl7v2.tests.fakers.msg_inr import fake_inru14
from zato.hl7v2.tests.fakers.msg_inu import fake_inuu05
from zato.hl7v2.tests.fakers.msg_lsu import fake_lsuu12
from zato.hl7v2.tests.fakers.msg_mdm import fake_mdmt01
from zato.hl7v2.tests.fakers.msg_mdm import fake_mdmt02
from zato.hl7v2.tests.fakers.msg_mfk import fake_mfkm01
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm02
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm04
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm05
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm06
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm07
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm08
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm09
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm10
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm11
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm12
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm13
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm15
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm16
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm17
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm18
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnm19
from zato.hl7v2.tests.fakers.msg_mfn import fake_mfnznn
from zato.hl7v2.tests.fakers.msg_nmd import fake_nmdn02
from zato.hl7v2.tests.fakers.msg_omb import fake_ombo27
from zato.hl7v2.tests.fakers.msg_omd import fake_omdo03
from zato.hl7v2.tests.fakers.msg_omg import fake_omgo19
from zato.hl7v2.tests.fakers.msg_omi import fake_omio23
from zato.hl7v2.tests.fakers.msg_oml import fake_omlo21
from zato.hl7v2.tests.fakers.msg_oml import fake_omlo33
from zato.hl7v2.tests.fakers.msg_oml import fake_omlo35
from zato.hl7v2.tests.fakers.msg_oml import fake_omlo39
from zato.hl7v2.tests.fakers.msg_oml import fake_omlo59
from zato.hl7v2.tests.fakers.msg_omn import fake_omno07
from zato.hl7v2.tests.fakers.msg_omp import fake_ompo09
from zato.hl7v2.tests.fakers.msg_omq import fake_omqo57
from zato.hl7v2.tests.fakers.msg_oms import fake_omso05
from zato.hl7v2.tests.fakers.msg_opl import fake_oplo37
from zato.hl7v2.tests.fakers.msg_opr import fake_opro38
from zato.hl7v2.tests.fakers.msg_opu import fake_opur25
from zato.hl7v2.tests.fakers.msg_ora import fake_orar33
from zato.hl7v2.tests.fakers.msg_ora import fake_orar41
from zato.hl7v2.tests.fakers.msg_orb import fake_orbo28
from zato.hl7v2.tests.fakers.msg_ord import fake_ordo04
from zato.hl7v2.tests.fakers.msg_org import fake_orgo20
from zato.hl7v2.tests.fakers.msg_ori import fake_orio24
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo22
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo34
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo36
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo40
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo53
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo54
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo55
from zato.hl7v2.tests.fakers.msg_orl import fake_orlo56
from zato.hl7v2.tests.fakers.msg_orm import fake_ormo01
from zato.hl7v2.tests.fakers.msg_orn import fake_orno08
from zato.hl7v2.tests.fakers.msg_orp import fake_orpo10
from zato.hl7v2.tests.fakers.msg_ors import fake_orso06
from zato.hl7v2.tests.fakers.msg_oru import fake_orur01
from zato.hl7v2.tests.fakers.msg_oru import fake_orur30
from zato.hl7v2.tests.fakers.msg_orx import fake_orxo58
from zato.hl7v2.tests.fakers.msg_osm import fake_osmr26
from zato.hl7v2.tests.fakers.msg_osu import fake_osuo51
from zato.hl7v2.tests.fakers.msg_osu import fake_osuo52
from zato.hl7v2.tests.fakers.msg_oul import fake_oulr22
from zato.hl7v2.tests.fakers.msg_oul import fake_oulr23
from zato.hl7v2.tests.fakers.msg_oul import fake_oulr24
from zato.hl7v2.tests.fakers.msg_pex import fake_pexp07
from zato.hl7v2.tests.fakers.msg_pgl import fake_pglpc6
from zato.hl7v2.tests.fakers.msg_pmu import fake_pmub01
from zato.hl7v2.tests.fakers.msg_pmu import fake_pmub03
from zato.hl7v2.tests.fakers.msg_pmu import fake_pmub04
from zato.hl7v2.tests.fakers.msg_pmu import fake_pmub07
from zato.hl7v2.tests.fakers.msg_pmu import fake_pmub08
from zato.hl7v2.tests.fakers.msg_ppg import fake_ppgpcg
from zato.hl7v2.tests.fakers.msg_ppp import fake_ppppcb
from zato.hl7v2.tests.fakers.msg_ppr import fake_pprpc1
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpe03
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpe22
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpo33
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpo34
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpq11
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpq13
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpq15
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpq21
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpqnn
from zato.hl7v2.tests.fakers.msg_qbp import fake_qbpz73
from zato.hl7v2.tests.fakers.msg_qcn import fake_qcnj01
from zato.hl7v2.tests.fakers.msg_qsb import fake_qsbq16
from zato.hl7v2.tests.fakers.msg_qvr import fake_qvrq17
from zato.hl7v2.tests.fakers.msg_ras import fake_raso17
from zato.hl7v2.tests.fakers.msg_rcv import fake_rcvo59
from zato.hl7v2.tests.fakers.msg_rde import fake_rdeo11
from zato.hl7v2.tests.fakers.msg_rde import fake_rdeo49
from zato.hl7v2.tests.fakers.msg_rdr import fake_rdrrdr
from zato.hl7v2.tests.fakers.msg_rds import fake_rdso13
from zato.hl7v2.tests.fakers.msg_rdy import fake_rdyk15
from zato.hl7v2.tests.fakers.msg_rdy import fake_rdyz80
from zato.hl7v2.tests.fakers.msg_ref import fake_refi12
from zato.hl7v2.tests.fakers.msg_rgv import fake_rgvo15
from zato.hl7v2.tests.fakers.msg_rpa import fake_rpai08
from zato.hl7v2.tests.fakers.msg_rpi import fake_rpii01
from zato.hl7v2.tests.fakers.msg_rpi import fake_rpii04
from zato.hl7v2.tests.fakers.msg_rpl import fake_rpli02
from zato.hl7v2.tests.fakers.msg_rpr import fake_rpri03
from zato.hl7v2.tests.fakers.msg_rqa import fake_rqai08
from zato.hl7v2.tests.fakers.msg_rqi import fake_rqii01
from zato.hl7v2.tests.fakers.msg_rqp import fake_rqpi04
from zato.hl7v2.tests.fakers.msg_rra import fake_rrao18
from zato.hl7v2.tests.fakers.msg_rrd import fake_rrdo14
from zato.hl7v2.tests.fakers.msg_rre import fake_rreo12
from zato.hl7v2.tests.fakers.msg_rre import fake_rreo50
from zato.hl7v2.tests.fakers.msg_rrg import fake_rrgo16
from zato.hl7v2.tests.fakers.msg_rri import fake_rrii12
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspe03
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspe22
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk11
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk21
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk22
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk23
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk25
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk31
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspk32
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspo33
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspo34
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspz82
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspz84
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspz86
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspz88
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspz90
from zato.hl7v2.tests.fakers.msg_rsp import fake_rspznn
from zato.hl7v2.tests.fakers.msg_rtb import fake_rtbk13
from zato.hl7v2.tests.fakers.msg_rtb import fake_rtbknn
from zato.hl7v2.tests.fakers.msg_rtb import fake_rtbz74
from zato.hl7v2.tests.fakers.msg_sdr import fake_sdrs31
from zato.hl7v2.tests.fakers.msg_sdr import fake_sdrs32
from zato.hl7v2.tests.fakers.msg_siu import fake_sius12
from zato.hl7v2.tests.fakers.msg_slr import fake_slrs28
from zato.hl7v2.tests.fakers.msg_srm import fake_srms01
from zato.hl7v2.tests.fakers.msg_srr import fake_srrs01
from zato.hl7v2.tests.fakers.msg_ssr import fake_ssru04
from zato.hl7v2.tests.fakers.msg_ssu import fake_ssuu03
from zato.hl7v2.tests.fakers.msg_stc import fake_stcs33
from zato.hl7v2.tests.fakers.msg_tcu import fake_tcuu10
from zato.hl7v2.tests.fakers.msg_udm import fake_udmq05
from zato.hl7v2.tests.fakers.msg_vxu import fake_vxuv04

from zato.hl7v2.v2_9 import parse_message
from zato.hl7v2.tests.fakers import fake_msh, fake_pid, fake_evn, fake_pv1


class TestParseMessageValidateFalse:

    def test_parse_ack_validate_false(self):
        raw = fake_ack()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta01_validate_false(self):
        raw = fake_adta01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta02_validate_false(self):
        raw = fake_adta02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta03_validate_false(self):
        raw = fake_adta03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta05_validate_false(self):
        raw = fake_adta05()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta06_validate_false(self):
        raw = fake_adta06()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta09_validate_false(self):
        raw = fake_adta09()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta12_validate_false(self):
        raw = fake_adta12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta15_validate_false(self):
        raw = fake_adta15()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta16_validate_false(self):
        raw = fake_adta16()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta17_validate_false(self):
        raw = fake_adta17()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta20_validate_false(self):
        raw = fake_adta20()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta21_validate_false(self):
        raw = fake_adta21()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta24_validate_false(self):
        raw = fake_adta24()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta37_validate_false(self):
        raw = fake_adta37()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta38_validate_false(self):
        raw = fake_adta38()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta39_validate_false(self):
        raw = fake_adta39()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta43_validate_false(self):
        raw = fake_adta43()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta44_validate_false(self):
        raw = fake_adta44()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta45_validate_false(self):
        raw = fake_adta45()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta50_validate_false(self):
        raw = fake_adta50()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta52_validate_false(self):
        raw = fake_adta52()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta54_validate_false(self):
        raw = fake_adta54()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta60_validate_false(self):
        raw = fake_adta60()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_adta61_validate_false(self):
        raw = fake_adta61()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_barp01_validate_false(self):
        raw = fake_barp01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_barp02_validate_false(self):
        raw = fake_barp02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_barp05_validate_false(self):
        raw = fake_barp05()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_barp06_validate_false(self):
        raw = fake_barp06()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_barp10_validate_false(self):
        raw = fake_barp10()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_barp12_validate_false(self):
        raw = fake_barp12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_bpso29_validate_false(self):
        raw = fake_bpso29()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_brpo30_validate_false(self):
        raw = fake_brpo30()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_brto32_validate_false(self):
        raw = fake_brto32()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_btso31_validate_false(self):
        raw = fake_btso31()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ccfi22_validate_false(self):
        raw = fake_ccfi22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ccii22_validate_false(self):
        raw = fake_ccii22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ccmi21_validate_false(self):
        raw = fake_ccmi21()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ccqi19_validate_false(self):
        raw = fake_ccqi19()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ccri16_validate_false(self):
        raw = fake_ccri16()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ccui20_validate_false(self):
        raw = fake_ccui20()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_cqui19_validate_false(self):
        raw = fake_cqui19()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_crmc01_validate_false(self):
        raw = fake_crmc01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_csuc09_validate_false(self):
        raw = fake_csuc09()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_dbco41_validate_false(self):
        raw = fake_dbco41()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_dbco42_validate_false(self):
        raw = fake_dbco42()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_delo46_validate_false(self):
        raw = fake_delo46()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_deoo45_validate_false(self):
        raw = fake_deoo45()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_dero44_validate_false(self):
        raw = fake_dero44()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_dftp03_validate_false(self):
        raw = fake_dftp03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_dftp11_validate_false(self):
        raw = fake_dftp11()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_dpro48_validate_false(self):
        raw = fake_dpro48()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_drco47_validate_false(self):
        raw = fake_drco47()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_drgo43_validate_false(self):
        raw = fake_drgo43()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_eacu07_validate_false(self):
        raw = fake_eacu07()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_eanu09_validate_false(self):
        raw = fake_eanu09()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_earu08_validate_false(self):
        raw = fake_earu08()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce01_validate_false(self):
        raw = fake_ehce01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce02_validate_false(self):
        raw = fake_ehce02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce04_validate_false(self):
        raw = fake_ehce04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce10_validate_false(self):
        raw = fake_ehce10()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce12_validate_false(self):
        raw = fake_ehce12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce13_validate_false(self):
        raw = fake_ehce13()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce15_validate_false(self):
        raw = fake_ehce15()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce20_validate_false(self):
        raw = fake_ehce20()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce21_validate_false(self):
        raw = fake_ehce21()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ehce24_validate_false(self):
        raw = fake_ehce24()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_esru02_validate_false(self):
        raw = fake_esru02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_esuu01_validate_false(self):
        raw = fake_esuu01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_inru06_validate_false(self):
        raw = fake_inru06()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_inru14_validate_false(self):
        raw = fake_inru14()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_inuu05_validate_false(self):
        raw = fake_inuu05()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_lsuu12_validate_false(self):
        raw = fake_lsuu12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mdmt01_validate_false(self):
        raw = fake_mdmt01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mdmt02_validate_false(self):
        raw = fake_mdmt02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfkm01_validate_false(self):
        raw = fake_mfkm01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm02_validate_false(self):
        raw = fake_mfnm02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm04_validate_false(self):
        raw = fake_mfnm04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm05_validate_false(self):
        raw = fake_mfnm05()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm06_validate_false(self):
        raw = fake_mfnm06()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm07_validate_false(self):
        raw = fake_mfnm07()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm08_validate_false(self):
        raw = fake_mfnm08()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm09_validate_false(self):
        raw = fake_mfnm09()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm10_validate_false(self):
        raw = fake_mfnm10()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm11_validate_false(self):
        raw = fake_mfnm11()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm12_validate_false(self):
        raw = fake_mfnm12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm13_validate_false(self):
        raw = fake_mfnm13()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm15_validate_false(self):
        raw = fake_mfnm15()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm16_validate_false(self):
        raw = fake_mfnm16()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm17_validate_false(self):
        raw = fake_mfnm17()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm18_validate_false(self):
        raw = fake_mfnm18()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnm19_validate_false(self):
        raw = fake_mfnm19()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_mfnznn_validate_false(self):
        raw = fake_mfnznn()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_nmdn02_validate_false(self):
        raw = fake_nmdn02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ombo27_validate_false(self):
        raw = fake_ombo27()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omdo03_validate_false(self):
        raw = fake_omdo03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omgo19_validate_false(self):
        raw = fake_omgo19()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omio23_validate_false(self):
        raw = fake_omio23()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omlo21_validate_false(self):
        raw = fake_omlo21()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omlo33_validate_false(self):
        raw = fake_omlo33()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omlo35_validate_false(self):
        raw = fake_omlo35()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omlo39_validate_false(self):
        raw = fake_omlo39()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omlo59_validate_false(self):
        raw = fake_omlo59()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omno07_validate_false(self):
        raw = fake_omno07()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ompo09_validate_false(self):
        raw = fake_ompo09()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omqo57_validate_false(self):
        raw = fake_omqo57()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_omso05_validate_false(self):
        raw = fake_omso05()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_oplo37_validate_false(self):
        raw = fake_oplo37()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_opro38_validate_false(self):
        raw = fake_opro38()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_opur25_validate_false(self):
        raw = fake_opur25()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orar33_validate_false(self):
        raw = fake_orar33()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orar41_validate_false(self):
        raw = fake_orar41()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orbo28_validate_false(self):
        raw = fake_orbo28()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ordo04_validate_false(self):
        raw = fake_ordo04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orgo20_validate_false(self):
        raw = fake_orgo20()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orio24_validate_false(self):
        raw = fake_orio24()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo22_validate_false(self):
        raw = fake_orlo22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo34_validate_false(self):
        raw = fake_orlo34()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo36_validate_false(self):
        raw = fake_orlo36()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo40_validate_false(self):
        raw = fake_orlo40()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo53_validate_false(self):
        raw = fake_orlo53()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo54_validate_false(self):
        raw = fake_orlo54()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo55_validate_false(self):
        raw = fake_orlo55()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orlo56_validate_false(self):
        raw = fake_orlo56()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ormo01_validate_false(self):
        raw = fake_ormo01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orno08_validate_false(self):
        raw = fake_orno08()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orpo10_validate_false(self):
        raw = fake_orpo10()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orso06_validate_false(self):
        raw = fake_orso06()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orur01_validate_false(self):
        raw = fake_orur01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orur30_validate_false(self):
        raw = fake_orur30()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_orxo58_validate_false(self):
        raw = fake_orxo58()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_osmr26_validate_false(self):
        raw = fake_osmr26()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_osuo51_validate_false(self):
        raw = fake_osuo51()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_osuo52_validate_false(self):
        raw = fake_osuo52()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_oulr22_validate_false(self):
        raw = fake_oulr22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_oulr23_validate_false(self):
        raw = fake_oulr23()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_oulr24_validate_false(self):
        raw = fake_oulr24()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pexp07_validate_false(self):
        raw = fake_pexp07()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pglpc6_validate_false(self):
        raw = fake_pglpc6()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pmub01_validate_false(self):
        raw = fake_pmub01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pmub03_validate_false(self):
        raw = fake_pmub03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pmub04_validate_false(self):
        raw = fake_pmub04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pmub07_validate_false(self):
        raw = fake_pmub07()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pmub08_validate_false(self):
        raw = fake_pmub08()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ppgpcg_validate_false(self):
        raw = fake_ppgpcg()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ppppcb_validate_false(self):
        raw = fake_ppppcb()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_pprpc1_validate_false(self):
        raw = fake_pprpc1()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpe03_validate_false(self):
        raw = fake_qbpe03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpe22_validate_false(self):
        raw = fake_qbpe22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpo33_validate_false(self):
        raw = fake_qbpo33()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpo34_validate_false(self):
        raw = fake_qbpo34()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpq11_validate_false(self):
        raw = fake_qbpq11()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpq13_validate_false(self):
        raw = fake_qbpq13()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpq15_validate_false(self):
        raw = fake_qbpq15()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpq21_validate_false(self):
        raw = fake_qbpq21()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpqnn_validate_false(self):
        raw = fake_qbpqnn()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qbpz73_validate_false(self):
        raw = fake_qbpz73()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qcnj01_validate_false(self):
        raw = fake_qcnj01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qsbq16_validate_false(self):
        raw = fake_qsbq16()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_qvrq17_validate_false(self):
        raw = fake_qvrq17()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_raso17_validate_false(self):
        raw = fake_raso17()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rcvo59_validate_false(self):
        raw = fake_rcvo59()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rdeo11_validate_false(self):
        raw = fake_rdeo11()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rdeo49_validate_false(self):
        raw = fake_rdeo49()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rdrrdr_validate_false(self):
        raw = fake_rdrrdr()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rdso13_validate_false(self):
        raw = fake_rdso13()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rdyk15_validate_false(self):
        raw = fake_rdyk15()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rdyz80_validate_false(self):
        raw = fake_rdyz80()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_refi12_validate_false(self):
        raw = fake_refi12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rgvo15_validate_false(self):
        raw = fake_rgvo15()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rpai08_validate_false(self):
        raw = fake_rpai08()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rpii01_validate_false(self):
        raw = fake_rpii01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rpii04_validate_false(self):
        raw = fake_rpii04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rpli02_validate_false(self):
        raw = fake_rpli02()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rpri03_validate_false(self):
        raw = fake_rpri03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rqai08_validate_false(self):
        raw = fake_rqai08()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rqii01_validate_false(self):
        raw = fake_rqii01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rqpi04_validate_false(self):
        raw = fake_rqpi04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rrao18_validate_false(self):
        raw = fake_rrao18()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rrdo14_validate_false(self):
        raw = fake_rrdo14()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rreo12_validate_false(self):
        raw = fake_rreo12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rreo50_validate_false(self):
        raw = fake_rreo50()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rrgo16_validate_false(self):
        raw = fake_rrgo16()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rrii12_validate_false(self):
        raw = fake_rrii12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspe03_validate_false(self):
        raw = fake_rspe03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspe22_validate_false(self):
        raw = fake_rspe22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk11_validate_false(self):
        raw = fake_rspk11()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk21_validate_false(self):
        raw = fake_rspk21()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk22_validate_false(self):
        raw = fake_rspk22()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk23_validate_false(self):
        raw = fake_rspk23()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk25_validate_false(self):
        raw = fake_rspk25()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk31_validate_false(self):
        raw = fake_rspk31()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspk32_validate_false(self):
        raw = fake_rspk32()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspo33_validate_false(self):
        raw = fake_rspo33()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspo34_validate_false(self):
        raw = fake_rspo34()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspz82_validate_false(self):
        raw = fake_rspz82()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspz84_validate_false(self):
        raw = fake_rspz84()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspz86_validate_false(self):
        raw = fake_rspz86()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspz88_validate_false(self):
        raw = fake_rspz88()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspz90_validate_false(self):
        raw = fake_rspz90()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rspznn_validate_false(self):
        raw = fake_rspznn()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rtbk13_validate_false(self):
        raw = fake_rtbk13()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rtbknn_validate_false(self):
        raw = fake_rtbknn()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_rtbz74_validate_false(self):
        raw = fake_rtbz74()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_sdrs31_validate_false(self):
        raw = fake_sdrs31()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_sdrs32_validate_false(self):
        raw = fake_sdrs32()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_sius12_validate_false(self):
        raw = fake_sius12()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_slrs28_validate_false(self):
        raw = fake_slrs28()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_srms01_validate_false(self):
        raw = fake_srms01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_srrs01_validate_false(self):
        raw = fake_srrs01()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ssru04_validate_false(self):
        raw = fake_ssru04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_ssuu03_validate_false(self):
        raw = fake_ssuu03()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_stcs33_validate_false(self):
        raw = fake_stcs33()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_tcuu10_validate_false(self):
        raw = fake_tcuu10()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_udmq05_validate_false(self):
        raw = fake_udmq05()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")

    def test_parse_vxuv04_validate_false(self):
        raw = fake_vxuv04()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert hasattr(msg, "_raw_message")


class TestParseMessageValidateFalseWithInvalidData:

    def test_parse_with_oversized_field_validate_false(self):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw, validate=False)
        msg.set("PID.5.1", "X" * 1000)
        serialized = msg.serialize()
        msg2 = parse_message(serialized, validate=False)
        assert msg2.get("PID.5.1") == "X" * 1000

    def test_parse_default_validates(self):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        assert msg is not None

    def test_validate_false_allows_any_parseable_message(self):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw, validate=False)
        assert msg is not None
        assert msg._raw_message.structure_id == "ADT_A01"
