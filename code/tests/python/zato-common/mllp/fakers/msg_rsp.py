from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment
from zato.hl7v2.tests.fakers.patient import fake_pid, fake_nk1, fake_mrg, fake_rel
from zato.hl7v2.tests.fakers.visit import fake_pv1, fake_evn, fake_npu
from zato.hl7v2.tests.fakers.order import fake_orc, fake_obr, fake_obx
from zato.hl7v2.tests.fakers.query import fake_qak, fake_qpd, fake_rcp, fake_msa, fake_dsc
from zato.hl7v2.tests.fakers.scheduling import fake_sch, fake_arq, fake_rgs
from zato.hl7v2.tests.fakers.master_file import fake_mfi, fake_mfe
from zato.hl7v2.tests.fakers.staff import fake_stf, fake_prd
from zato.hl7v2.tests.fakers.documents import fake_txa
from zato.hl7v2.tests.fakers.lab import fake_spm, fake_equ, fake_inv
from zato.hl7v2.tests.fakers.blood_bank import fake_bpo
from zato.hl7v2.tests.fakers.clinical import fake_prb, fake_gol, fake_rf1, fake_pth
from zato.hl7v2.tests.fakers.pharmacy import fake_rxe, fake_rxd, fake_rxa, fake_rxg
from zato.hl7v2.tests.fakers.software import fake_sft


def fake_rspe03() -> str:
    return fake_msh("RSP", "E03", "RSP_E03") + fake_pid()

def fake_rspe22() -> str:
    return fake_msh("RSP", "E22", "RSP_E22") + fake_pid()

def fake_rspk11() -> str:
    return fake_msh("RSP", "K11", "RSP_K11") + fake_pid()

def fake_rspk21() -> str:
    return fake_msh("RSP", "K21", "RSP_K21") + fake_pid()

def fake_rspk22() -> str:
    return fake_msh("RSP", "K22", "RSP_K22") + fake_pid()

def fake_rspk23() -> str:
    return fake_msh("RSP", "K23", "RSP_K23") + fake_pid()

def fake_rspk25() -> str:
    return fake_msh("RSP", "K25", "RSP_K25") + fake_pid()

def fake_rspk31() -> str:
    return fake_msh("RSP", "K31", "RSP_K31") + fake_pid()

def fake_rspk32() -> str:
    return fake_msh("RSP", "K32", "RSP_K32") + fake_pid()

def fake_rspo33() -> str:
    return fake_msh("RSP", "O33", "RSP_O33") + fake_pid()

def fake_rspo34() -> str:
    return fake_msh("RSP", "O34", "RSP_O34") + fake_pid()

def fake_rspz82() -> str:
    return fake_msh("RSP", "Z82", "RSP_Z82") + fake_pid()

def fake_rspz84() -> str:
    return fake_msh("RSP", "Z84", "RSP_Z84") + fake_pid()

def fake_rspz86() -> str:
    return fake_msh("RSP", "Z86", "RSP_Z86") + fake_pid()

def fake_rspz88() -> str:
    return fake_msh("RSP", "Z88", "RSP_Z88") + fake_pid()

def fake_rspz90() -> str:
    return fake_msh("RSP", "Z90", "RSP_Z90") + fake_pid()

def fake_rspznn() -> str:
    return fake_msh("RSP", "Znn", "RSP_Znn") + fake_pid()
