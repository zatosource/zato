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


def fake_adta01() -> str:
    return fake_msh("ADT", "A01", "ADT_A01") + fake_pid()

def fake_adta02() -> str:
    return fake_msh("ADT", "A02", "ADT_A02") + fake_pid()

def fake_adta03() -> str:
    return fake_msh("ADT", "A03", "ADT_A03") + fake_pid()

def fake_adta05() -> str:
    return fake_msh("ADT", "A05", "ADT_A05") + fake_pid()

def fake_adta06() -> str:
    return fake_msh("ADT", "A06", "ADT_A06") + fake_pid()

def fake_adta09() -> str:
    return fake_msh("ADT", "A09", "ADT_A09") + fake_pid()

def fake_adta12() -> str:
    return fake_msh("ADT", "A12", "ADT_A12") + fake_pid()

def fake_adta15() -> str:
    return fake_msh("ADT", "A15", "ADT_A15") + fake_pid()

def fake_adta16() -> str:
    return fake_msh("ADT", "A16", "ADT_A16") + fake_pid()

def fake_adta17() -> str:
    return fake_msh("ADT", "A17", "ADT_A17") + fake_pid()

def fake_adta20() -> str:
    return fake_msh("ADT", "A20", "ADT_A20") + fake_pid()

def fake_adta21() -> str:
    return fake_msh("ADT", "A21", "ADT_A21") + fake_pid()

def fake_adta24() -> str:
    return fake_msh("ADT", "A24", "ADT_A24") + fake_pid()

def fake_adta37() -> str:
    return fake_msh("ADT", "A37", "ADT_A37") + fake_pid()

def fake_adta38() -> str:
    return fake_msh("ADT", "A38", "ADT_A38") + fake_pid()

def fake_adta39() -> str:
    return fake_msh("ADT", "A39", "ADT_A39") + fake_pid()

def fake_adta43() -> str:
    return fake_msh("ADT", "A43", "ADT_A43") + fake_pid()

def fake_adta44() -> str:
    return fake_msh("ADT", "A44", "ADT_A44") + fake_pid()

def fake_adta45() -> str:
    return fake_msh("ADT", "A45", "ADT_A45") + fake_pid()

def fake_adta50() -> str:
    return fake_msh("ADT", "A50", "ADT_A50") + fake_pid()

def fake_adta52() -> str:
    return fake_msh("ADT", "A52", "ADT_A52") + fake_pid()

def fake_adta54() -> str:
    return fake_msh("ADT", "A54", "ADT_A54") + fake_pid()

def fake_adta60() -> str:
    return fake_msh("ADT", "A60", "ADT_A60") + fake_pid()

def fake_adta61() -> str:
    return fake_msh("ADT", "A61", "ADT_A61") + fake_pid()
