from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.query import fake_msa


def fake_rdrrdr() -> str:
    return fake_msh("RDR", "RDR", "RDR_RDR") + fake_msa()
