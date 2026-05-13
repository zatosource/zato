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


def fake_ehce01() -> str:
    return fake_msh("EHC", "E01", "EHC_E01") + fake_pid()

def fake_ehce02() -> str:
    return fake_msh("EHC", "E02", "EHC_E02") + fake_pid()

def fake_ehce04() -> str:
    return fake_msh("EHC", "E04", "EHC_E04") + fake_pid()

def fake_ehce10() -> str:
    return fake_msh("EHC", "E10", "EHC_E10") + fake_pid()

def fake_ehce12() -> str:
    return fake_msh("EHC", "E12", "EHC_E12") + fake_pid()

def fake_ehce13() -> str:
    return fake_msh("EHC", "E13", "EHC_E13") + fake_pid()

def fake_ehce15() -> str:
    return fake_msh("EHC", "E15", "EHC_E15") + fake_pid()

def fake_ehce20() -> str:
    return fake_msh("EHC", "E20", "EHC_E20") + fake_pid()

def fake_ehce21() -> str:
    return fake_msh("EHC", "E21", "EHC_E21") + fake_pid()

def fake_ehce24() -> str:
    return fake_msh("EHC", "E24", "EHC_E24") + fake_pid()
