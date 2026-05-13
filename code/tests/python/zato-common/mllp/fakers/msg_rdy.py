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


def fake_rdyk15() -> str:
    return fake_msh("RDY", "K15", "RDY_K15") + fake_pid()

def fake_rdyz80() -> str:
    return fake_msh("RDY", "Z80", "RDY_Z80") + fake_pid()
