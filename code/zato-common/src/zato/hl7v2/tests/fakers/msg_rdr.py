from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rdrrdr() -> str:
    return fake_msh("RDR", "RDR", "RDR_RDR") + fake_pid()
