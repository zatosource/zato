from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa, fake_qak, fake_qpd


def fake_rdyk15() -> str:
    return fake_msh("RDY", "K15", "RDY_K15") + fake_msa() + fake_qak() + fake_qpd()

def fake_rdyz80() -> str:
    return fake_msh("RDY", "Z80", "RDY_Z80") + fake_msa() + fake_qak() + fake_qpd()
