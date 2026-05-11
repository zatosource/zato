from __future__ import annotations

import pytest


class TestSegmentClassImports:
    """Test that all segment classes can be imported directly."""

    def test_import_abs(self):
        from zato.hl7v2.v2_9.segments import ABS
        assert ABS._segment_id == "ABS"

    def test_import_acc(self):
        from zato.hl7v2.v2_9.segments import ACC
        assert ACC._segment_id == "ACC"

    def test_import_add(self):
        from zato.hl7v2.v2_9.segments import ADD
        assert ADD._segment_id == "ADD"

    def test_import_adj(self):
        from zato.hl7v2.v2_9.segments import ADJ
        assert ADJ._segment_id == "ADJ"

    def test_import_aff(self):
        from zato.hl7v2.v2_9.segments import AFF
        assert AFF._segment_id == "AFF"

    def test_import_aig(self):
        from zato.hl7v2.v2_9.segments import AIG
        assert AIG._segment_id == "AIG"

    def test_import_ail(self):
        from zato.hl7v2.v2_9.segments import AIL
        assert AIL._segment_id == "AIL"

    def test_import_aip(self):
        from zato.hl7v2.v2_9.segments import AIP
        assert AIP._segment_id == "AIP"

    def test_import_ais(self):
        from zato.hl7v2.v2_9.segments import AIS
        assert AIS._segment_id == "AIS"

    def test_import_al1(self):
        from zato.hl7v2.v2_9.segments import AL1
        assert AL1._segment_id == "AL1"

    def test_import_apr(self):
        from zato.hl7v2.v2_9.segments import APR
        assert APR._segment_id == "APR"

    def test_import_arq(self):
        from zato.hl7v2.v2_9.segments import ARQ
        assert ARQ._segment_id == "ARQ"

    def test_import_arv(self):
        from zato.hl7v2.v2_9.segments import ARV
        assert ARV._segment_id == "ARV"

    def test_import_aut(self):
        from zato.hl7v2.v2_9.segments import AUT
        assert AUT._segment_id == "AUT"

    def test_import_bhs(self):
        from zato.hl7v2.v2_9.segments import BHS
        assert BHS._segment_id == "BHS"

    def test_import_blc(self):
        from zato.hl7v2.v2_9.segments import BLC
        assert BLC._segment_id == "BLC"

    def test_import_blg(self):
        from zato.hl7v2.v2_9.segments import BLG
        assert BLG._segment_id == "BLG"

    def test_import_bpo(self):
        from zato.hl7v2.v2_9.segments import BPO
        assert BPO._segment_id == "BPO"

    def test_import_bpx(self):
        from zato.hl7v2.v2_9.segments import BPX
        assert BPX._segment_id == "BPX"

    def test_import_bts(self):
        from zato.hl7v2.v2_9.segments import BTS
        assert BTS._segment_id == "BTS"

    def test_import_btx(self):
        from zato.hl7v2.v2_9.segments import BTX
        assert BTX._segment_id == "BTX"

    def test_import_bui(self):
        from zato.hl7v2.v2_9.segments import BUI
        assert BUI._segment_id == "BUI"

    def test_import_cdm(self):
        from zato.hl7v2.v2_9.segments import CDM
        assert CDM._segment_id == "CDM"

    def test_import_cdo(self):
        from zato.hl7v2.v2_9.segments import CDO
        assert CDO._segment_id == "CDO"

    def test_import_cer(self):
        from zato.hl7v2.v2_9.segments import CER
        assert CER._segment_id == "CER"

    def test_import_cm0(self):
        from zato.hl7v2.v2_9.segments import CM0
        assert CM0._segment_id == "CM0"

    def test_import_cm1(self):
        from zato.hl7v2.v2_9.segments import CM1
        assert CM1._segment_id == "CM1"

    def test_import_cm2(self):
        from zato.hl7v2.v2_9.segments import CM2
        assert CM2._segment_id == "CM2"

    def test_import_cns(self):
        from zato.hl7v2.v2_9.segments import CNS
        assert CNS._segment_id == "CNS"

    def test_import_con(self):
        from zato.hl7v2.v2_9.segments import CON
        assert CON._segment_id == "CON"

    def test_import_csp(self):
        from zato.hl7v2.v2_9.segments import CSP
        assert CSP._segment_id == "CSP"

    def test_import_csr(self):
        from zato.hl7v2.v2_9.segments import CSR
        assert CSR._segment_id == "CSR"

    def test_import_css(self):
        from zato.hl7v2.v2_9.segments import CSS
        assert CSS._segment_id == "CSS"

    def test_import_ctd(self):
        from zato.hl7v2.v2_9.segments import CTD
        assert CTD._segment_id == "CTD"

    def test_import_cti(self):
        from zato.hl7v2.v2_9.segments import CTI
        assert CTI._segment_id == "CTI"

    def test_import_ctr(self):
        from zato.hl7v2.v2_9.segments import CTR
        assert CTR._segment_id == "CTR"

    def test_import_db1(self):
        from zato.hl7v2.v2_9.segments import DB1
        assert DB1._segment_id == "DB1"

    def test_import_dev(self):
        from zato.hl7v2.v2_9.segments import DEV
        assert DEV._segment_id == "DEV"

    def test_import_dg1(self):
        from zato.hl7v2.v2_9.segments import DG1
        assert DG1._segment_id == "DG1"

    def test_import_dmi(self):
        from zato.hl7v2.v2_9.segments import DMI
        assert DMI._segment_id == "DMI"

    def test_import_don(self):
        from zato.hl7v2.v2_9.segments import DON
        assert DON._segment_id == "DON"

    def test_import_dps(self):
        from zato.hl7v2.v2_9.segments import DPS
        assert DPS._segment_id == "DPS"

    def test_import_drg(self):
        from zato.hl7v2.v2_9.segments import DRG
        assert DRG._segment_id == "DRG"

    def test_import_dsc(self):
        from zato.hl7v2.v2_9.segments import DSC
        assert DSC._segment_id == "DSC"

    def test_import_dsp(self):
        from zato.hl7v2.v2_9.segments import DSP
        assert DSP._segment_id == "DSP"

    def test_import_dst(self):
        from zato.hl7v2.v2_9.segments import DST
        assert DST._segment_id == "DST"

    def test_import_ecd(self):
        from zato.hl7v2.v2_9.segments import ECD
        assert ECD._segment_id == "ECD"

    def test_import_ecr(self):
        from zato.hl7v2.v2_9.segments import ECR
        assert ECR._segment_id == "ECR"

    def test_import_edu(self):
        from zato.hl7v2.v2_9.segments import EDU
        assert EDU._segment_id == "EDU"

    def test_import_eqp(self):
        from zato.hl7v2.v2_9.segments import EQP
        assert EQP._segment_id == "EQP"

    def test_import_equ(self):
        from zato.hl7v2.v2_9.segments import EQU
        assert EQU._segment_id == "EQU"

    def test_import_err(self):
        from zato.hl7v2.v2_9.segments import ERR
        assert ERR._segment_id == "ERR"

    def test_import_evn(self):
        from zato.hl7v2.v2_9.segments import EVN
        assert EVN._segment_id == "EVN"

    def test_import_fac(self):
        from zato.hl7v2.v2_9.segments import FAC
        assert FAC._segment_id == "FAC"

    def test_import_fhs(self):
        from zato.hl7v2.v2_9.segments import FHS
        assert FHS._segment_id == "FHS"

    def test_import_ft1(self):
        from zato.hl7v2.v2_9.segments import FT1
        assert FT1._segment_id == "FT1"

    def test_import_fts(self):
        from zato.hl7v2.v2_9.segments import FTS
        assert FTS._segment_id == "FTS"

    def test_import_gol(self):
        from zato.hl7v2.v2_9.segments import GOL
        assert GOL._segment_id == "GOL"

    def test_import_gp1(self):
        from zato.hl7v2.v2_9.segments import GP1
        assert GP1._segment_id == "GP1"

    def test_import_gp2(self):
        from zato.hl7v2.v2_9.segments import GP2
        assert GP2._segment_id == "GP2"

    def test_import_gt1(self):
        from zato.hl7v2.v2_9.segments import GT1
        assert GT1._segment_id == "GT1"

    def test_import_iam(self):
        from zato.hl7v2.v2_9.segments import IAM
        assert IAM._segment_id == "IAM"

    def test_import_iar(self):
        from zato.hl7v2.v2_9.segments import IAR
        assert IAR._segment_id == "IAR"

    def test_import_iim(self):
        from zato.hl7v2.v2_9.segments import IIM
        assert IIM._segment_id == "IIM"

    def test_import_ilt(self):
        from zato.hl7v2.v2_9.segments import ILT
        assert ILT._segment_id == "ILT"

    def test_import_in1(self):
        from zato.hl7v2.v2_9.segments import IN1
        assert IN1._segment_id == "IN1"

    def test_import_in2(self):
        from zato.hl7v2.v2_9.segments import IN2
        assert IN2._segment_id == "IN2"

    def test_import_in3(self):
        from zato.hl7v2.v2_9.segments import IN3
        assert IN3._segment_id == "IN3"

    def test_import_inv(self):
        from zato.hl7v2.v2_9.segments import INV
        assert INV._segment_id == "INV"

    def test_import_ipc(self):
        from zato.hl7v2.v2_9.segments import IPC
        assert IPC._segment_id == "IPC"

    def test_import_ipr(self):
        from zato.hl7v2.v2_9.segments import IPR
        assert IPR._segment_id == "IPR"

    def test_import_isd(self):
        from zato.hl7v2.v2_9.segments import ISD
        assert ISD._segment_id == "ISD"

    def test_import_itm(self):
        from zato.hl7v2.v2_9.segments import ITM
        assert ITM._segment_id == "ITM"

    def test_import_ivc(self):
        from zato.hl7v2.v2_9.segments import IVC
        assert IVC._segment_id == "IVC"

    def test_import_ivt(self):
        from zato.hl7v2.v2_9.segments import IVT
        assert IVT._segment_id == "IVT"

    def test_import_lan(self):
        from zato.hl7v2.v2_9.segments import LAN
        assert LAN._segment_id == "LAN"

    def test_import_lcc(self):
        from zato.hl7v2.v2_9.segments import LCC
        assert LCC._segment_id == "LCC"

    def test_import_lch(self):
        from zato.hl7v2.v2_9.segments import LCH
        assert LCH._segment_id == "LCH"

    def test_import_ldp(self):
        from zato.hl7v2.v2_9.segments import LDP
        assert LDP._segment_id == "LDP"

    def test_import_loc(self):
        from zato.hl7v2.v2_9.segments import LOC
        assert LOC._segment_id == "LOC"

    def test_import_lrl(self):
        from zato.hl7v2.v2_9.segments import LRL
        assert LRL._segment_id == "LRL"

    def test_import_mcp(self):
        from zato.hl7v2.v2_9.segments import MCP
        assert MCP._segment_id == "MCP"

    def test_import_mfa(self):
        from zato.hl7v2.v2_9.segments import MFA
        assert MFA._segment_id == "MFA"

    def test_import_mfe(self):
        from zato.hl7v2.v2_9.segments import MFE
        assert MFE._segment_id == "MFE"

    def test_import_mfi(self):
        from zato.hl7v2.v2_9.segments import MFI
        assert MFI._segment_id == "MFI"

    def test_import_mrg(self):
        from zato.hl7v2.v2_9.segments import MRG
        assert MRG._segment_id == "MRG"

    def test_import_msa(self):
        from zato.hl7v2.v2_9.segments import MSA
        assert MSA._segment_id == "MSA"

    def test_import_msh(self):
        from zato.hl7v2.v2_9.segments import MSH
        assert MSH._segment_id == "MSH"

    def test_import_nck(self):
        from zato.hl7v2.v2_9.segments import NCK
        assert NCK._segment_id == "NCK"

    def test_import_nds(self):
        from zato.hl7v2.v2_9.segments import NDS
        assert NDS._segment_id == "NDS"

    def test_import_nk1(self):
        from zato.hl7v2.v2_9.segments import NK1
        assert NK1._segment_id == "NK1"

    def test_import_npu(self):
        from zato.hl7v2.v2_9.segments import NPU
        assert NPU._segment_id == "NPU"

    def test_import_nsc(self):
        from zato.hl7v2.v2_9.segments import NSC
        assert NSC._segment_id == "NSC"

    def test_import_nst(self):
        from zato.hl7v2.v2_9.segments import NST
        assert NST._segment_id == "NST"

    def test_import_nte(self):
        from zato.hl7v2.v2_9.segments import NTE
        assert NTE._segment_id == "NTE"

    def test_import_obr(self):
        from zato.hl7v2.v2_9.segments import OBR
        assert OBR._segment_id == "OBR"

    def test_import_obx(self):
        from zato.hl7v2.v2_9.segments import OBX
        assert OBX._segment_id == "OBX"

    def test_import_ods(self):
        from zato.hl7v2.v2_9.segments import ODS
        assert ODS._segment_id == "ODS"

    def test_import_odt(self):
        from zato.hl7v2.v2_9.segments import ODT
        assert ODT._segment_id == "ODT"

    def test_import_oh1(self):
        from zato.hl7v2.v2_9.segments import OH1
        assert OH1._segment_id == "OH1"

    def test_import_oh2(self):
        from zato.hl7v2.v2_9.segments import OH2
        assert OH2._segment_id == "OH2"

    def test_import_oh3(self):
        from zato.hl7v2.v2_9.segments import OH3
        assert OH3._segment_id == "OH3"

    def test_import_oh4(self):
        from zato.hl7v2.v2_9.segments import OH4
        assert OH4._segment_id == "OH4"

    def test_import_om1(self):
        from zato.hl7v2.v2_9.segments import OM1
        assert OM1._segment_id == "OM1"

    def test_import_om2(self):
        from zato.hl7v2.v2_9.segments import OM2
        assert OM2._segment_id == "OM2"

    def test_import_om3(self):
        from zato.hl7v2.v2_9.segments import OM3
        assert OM3._segment_id == "OM3"

    def test_import_om4(self):
        from zato.hl7v2.v2_9.segments import OM4
        assert OM4._segment_id == "OM4"

    def test_import_om5(self):
        from zato.hl7v2.v2_9.segments import OM5
        assert OM5._segment_id == "OM5"

    def test_import_om6(self):
        from zato.hl7v2.v2_9.segments import OM6
        assert OM6._segment_id == "OM6"

    def test_import_om7(self):
        from zato.hl7v2.v2_9.segments import OM7
        assert OM7._segment_id == "OM7"

    def test_import_omc(self):
        from zato.hl7v2.v2_9.segments import OMC
        assert OMC._segment_id == "OMC"

    def test_import_orc(self):
        from zato.hl7v2.v2_9.segments import ORC
        assert ORC._segment_id == "ORC"

    def test_import_org(self):
        from zato.hl7v2.v2_9.segments import ORG
        assert ORG._segment_id == "ORG"

    def test_import_ovr(self):
        from zato.hl7v2.v2_9.segments import OVR
        assert OVR._segment_id == "OVR"

    def test_import_pac(self):
        from zato.hl7v2.v2_9.segments import PAC
        assert PAC._segment_id == "PAC"

    def test_import_pce(self):
        from zato.hl7v2.v2_9.segments import PCE
        assert PCE._segment_id == "PCE"

    def test_import_pcr(self):
        from zato.hl7v2.v2_9.segments import PCR
        assert PCR._segment_id == "PCR"

    def test_import_pd1(self):
        from zato.hl7v2.v2_9.segments import PD1
        assert PD1._segment_id == "PD1"

    def test_import_pda(self):
        from zato.hl7v2.v2_9.segments import PDA
        assert PDA._segment_id == "PDA"

    def test_import_pdc(self):
        from zato.hl7v2.v2_9.segments import PDC
        assert PDC._segment_id == "PDC"

    def test_import_peo(self):
        from zato.hl7v2.v2_9.segments import PEO
        assert PEO._segment_id == "PEO"

    def test_import_pes(self):
        from zato.hl7v2.v2_9.segments import PES
        assert PES._segment_id == "PES"

    def test_import_pid(self):
        from zato.hl7v2.v2_9.segments import PID
        assert PID._segment_id == "PID"

    def test_import_pkg(self):
        from zato.hl7v2.v2_9.segments import PKG
        assert PKG._segment_id == "PKG"

    def test_import_pm1(self):
        from zato.hl7v2.v2_9.segments import PM1
        assert PM1._segment_id == "PM1"

    def test_import_pmt(self):
        from zato.hl7v2.v2_9.segments import PMT
        assert PMT._segment_id == "PMT"

    def test_import_pr1(self):
        from zato.hl7v2.v2_9.segments import PR1
        assert PR1._segment_id == "PR1"

    def test_import_pra(self):
        from zato.hl7v2.v2_9.segments import PRA
        assert PRA._segment_id == "PRA"

    def test_import_prb(self):
        from zato.hl7v2.v2_9.segments import PRB
        assert PRB._segment_id == "PRB"

    def test_import_prc(self):
        from zato.hl7v2.v2_9.segments import PRC
        assert PRC._segment_id == "PRC"

    def test_import_prd(self):
        from zato.hl7v2.v2_9.segments import PRD
        assert PRD._segment_id == "PRD"

    def test_import_prt(self):
        from zato.hl7v2.v2_9.segments import PRT
        assert PRT._segment_id == "PRT"

    def test_import_psg(self):
        from zato.hl7v2.v2_9.segments import PSG
        assert PSG._segment_id == "PSG"

    def test_import_psh(self):
        from zato.hl7v2.v2_9.segments import PSH
        assert PSH._segment_id == "PSH"

    def test_import_psl(self):
        from zato.hl7v2.v2_9.segments import PSL
        assert PSL._segment_id == "PSL"

    def test_import_pss(self):
        from zato.hl7v2.v2_9.segments import PSS
        assert PSS._segment_id == "PSS"

    def test_import_pth(self):
        from zato.hl7v2.v2_9.segments import PTH
        assert PTH._segment_id == "PTH"

    def test_import_pv1(self):
        from zato.hl7v2.v2_9.segments import PV1
        assert PV1._segment_id == "PV1"

    def test_import_pv2(self):
        from zato.hl7v2.v2_9.segments import PV2
        assert PV2._segment_id == "PV2"

    def test_import_pye(self):
        from zato.hl7v2.v2_9.segments import PYE
        assert PYE._segment_id == "PYE"

    def test_import_qak(self):
        from zato.hl7v2.v2_9.segments import QAK
        assert QAK._segment_id == "QAK"

    def test_import_qid(self):
        from zato.hl7v2.v2_9.segments import QID
        assert QID._segment_id == "QID"

    def test_import_qpd(self):
        from zato.hl7v2.v2_9.segments import QPD
        assert QPD._segment_id == "QPD"

    def test_import_qri(self):
        from zato.hl7v2.v2_9.segments import QRI
        assert QRI._segment_id == "QRI"

    def test_import_rcp(self):
        from zato.hl7v2.v2_9.segments import RCP
        assert RCP._segment_id == "RCP"

    def test_import_rdf(self):
        from zato.hl7v2.v2_9.segments import RDF
        assert RDF._segment_id == "RDF"

    def test_import_rdt(self):
        from zato.hl7v2.v2_9.segments import RDT
        assert RDT._segment_id == "RDT"

    def test_import_rel(self):
        from zato.hl7v2.v2_9.segments import REL
        assert REL._segment_id == "REL"

    def test_import_rf1(self):
        from zato.hl7v2.v2_9.segments import RF1
        assert RF1._segment_id == "RF1"

    def test_import_rfi(self):
        from zato.hl7v2.v2_9.segments import RFI
        assert RFI._segment_id == "RFI"

    def test_import_rgs(self):
        from zato.hl7v2.v2_9.segments import RGS
        assert RGS._segment_id == "RGS"

    def test_import_rmi(self):
        from zato.hl7v2.v2_9.segments import RMI
        assert RMI._segment_id == "RMI"

    def test_import_rq1(self):
        from zato.hl7v2.v2_9.segments import RQ1
        assert RQ1._segment_id == "RQ1"

    def test_import_rqd(self):
        from zato.hl7v2.v2_9.segments import RQD
        assert RQD._segment_id == "RQD"

    def test_import_rxa(self):
        from zato.hl7v2.v2_9.segments import RXA
        assert RXA._segment_id == "RXA"

    def test_import_rxc(self):
        from zato.hl7v2.v2_9.segments import RXC
        assert RXC._segment_id == "RXC"

    def test_import_rxd(self):
        from zato.hl7v2.v2_9.segments import RXD
        assert RXD._segment_id == "RXD"

    def test_import_rxe(self):
        from zato.hl7v2.v2_9.segments import RXE
        assert RXE._segment_id == "RXE"

    def test_import_rxg(self):
        from zato.hl7v2.v2_9.segments import RXG
        assert RXG._segment_id == "RXG"

    def test_import_rxo(self):
        from zato.hl7v2.v2_9.segments import RXO
        assert RXO._segment_id == "RXO"

    def test_import_rxr(self):
        from zato.hl7v2.v2_9.segments import RXR
        assert RXR._segment_id == "RXR"

    def test_import_rxv(self):
        from zato.hl7v2.v2_9.segments import RXV
        assert RXV._segment_id == "RXV"

    def test_import_sac(self):
        from zato.hl7v2.v2_9.segments import SAC
        assert SAC._segment_id == "SAC"

    def test_import_scd(self):
        from zato.hl7v2.v2_9.segments import SCD
        assert SCD._segment_id == "SCD"

    def test_import_sch(self):
        from zato.hl7v2.v2_9.segments import SCH
        assert SCH._segment_id == "SCH"

    def test_import_scp(self):
        from zato.hl7v2.v2_9.segments import SCP
        assert SCP._segment_id == "SCP"

    def test_import_sdd(self):
        from zato.hl7v2.v2_9.segments import SDD
        assert SDD._segment_id == "SDD"

    def test_import_sft(self):
        from zato.hl7v2.v2_9.segments import SFT
        assert SFT._segment_id == "SFT"

    def test_import_sgh(self):
        from zato.hl7v2.v2_9.segments import SGH
        assert SGH._segment_id == "SGH"

    def test_import_sgt(self):
        from zato.hl7v2.v2_9.segments import SGT
        assert SGT._segment_id == "SGT"

    def test_import_shp(self):
        from zato.hl7v2.v2_9.segments import SHP
        assert SHP._segment_id == "SHP"

    def test_import_sid(self):
        from zato.hl7v2.v2_9.segments import SID
        assert SID._segment_id == "SID"

    def test_import_slt(self):
        from zato.hl7v2.v2_9.segments import SLT
        assert SLT._segment_id == "SLT"

    def test_import_spm(self):
        from zato.hl7v2.v2_9.segments import SPM
        assert SPM._segment_id == "SPM"

    def test_import_stf(self):
        from zato.hl7v2.v2_9.segments import STF
        assert STF._segment_id == "STF"

    def test_import_stz(self):
        from zato.hl7v2.v2_9.segments import STZ
        assert STZ._segment_id == "STZ"

    def test_import_tcc(self):
        from zato.hl7v2.v2_9.segments import TCC
        assert TCC._segment_id == "TCC"

    def test_import_tcd(self):
        from zato.hl7v2.v2_9.segments import TCD
        assert TCD._segment_id == "TCD"

    def test_import_tq1(self):
        from zato.hl7v2.v2_9.segments import TQ1
        assert TQ1._segment_id == "TQ1"

    def test_import_tq2(self):
        from zato.hl7v2.v2_9.segments import TQ2
        assert TQ2._segment_id == "TQ2"

    def test_import_txa(self):
        from zato.hl7v2.v2_9.segments import TXA
        assert TXA._segment_id == "TXA"

    def test_import_uac(self):
        from zato.hl7v2.v2_9.segments import UAC
        assert UAC._segment_id == "UAC"

    def test_import_ub2(self):
        from zato.hl7v2.v2_9.segments import UB2
        assert UB2._segment_id == "UB2"

    def test_import_var(self):
        from zato.hl7v2.v2_9.segments import VAR
        assert VAR._segment_id == "VAR"

    def test_import_vnd(self):
        from zato.hl7v2.v2_9.segments import VND
        assert VND._segment_id == "VND"

    def test_import_zl7(self):
        from zato.hl7v2.v2_9.segments import ZL7
        assert ZL7._segment_id == "ZL7"
