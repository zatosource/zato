from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_tcuu10() -> str:
    return fake_msh("TCU", "U10", "TCU_U10") + fake_equ()
