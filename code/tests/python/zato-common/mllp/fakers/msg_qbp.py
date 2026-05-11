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


def fake_qbpe03() -> str:
    return fake_msh("QBP", "E03", "QBP_E03") + fake_pid()

def fake_qbpe22() -> str:
    return fake_msh("QBP", "E22", "QBP_E22") + fake_pid()

def fake_qbpo33() -> str:
    return fake_msh("QBP", "O33", "QBP_O33") + fake_pid()

def fake_qbpo34() -> str:
    return fake_msh("QBP", "O34", "QBP_O34") + fake_pid()

def fake_qbpq11() -> str:
    return fake_msh("QBP", "Q11", "QBP_Q11") + fake_pid()

def fake_qbpq13() -> str:
    return fake_msh("QBP", "Q13", "QBP_Q13") + fake_pid()

def fake_qbpq15() -> str:
    return fake_msh("QBP", "Q15", "QBP_Q15") + fake_pid()

def fake_qbpq21() -> str:
    return fake_msh("QBP", "Q21", "QBP_Q21") + fake_pid()

def fake_qbpqnn() -> str:
    return fake_msh("QBP", "Qnn", "QBP_Qnn") + fake_pid()

def fake_qbpz73() -> str:
    return fake_msh("QBP", "Z73", "QBP_Z73") + fake_pid()
