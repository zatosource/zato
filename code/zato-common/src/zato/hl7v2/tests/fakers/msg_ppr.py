from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_pprpc1() -> str:
    return fake_msh("PPR", "PC1", "PPR_PC1") + fake_pid()
