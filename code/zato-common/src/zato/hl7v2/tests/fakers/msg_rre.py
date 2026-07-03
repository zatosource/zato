from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rreo12() -> str:
    return fake_msh("RRE", "O12", "RRE_O12") + fake_msa()

def fake_rreo50() -> str:
    return fake_msh("RRE", "O50", "RRE_O50") + fake_msa()
