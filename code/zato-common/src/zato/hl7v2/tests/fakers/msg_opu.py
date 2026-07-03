from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_opur25() -> str:
    return fake_msh("OPU", "R25", "OPU_R25") + fake_pid()
