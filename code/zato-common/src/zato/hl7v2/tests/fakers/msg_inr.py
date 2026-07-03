from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ, fake_inv


def fake_inru06() -> str:
    return fake_msh("INR", "U06", "INR_U06") + fake_equ() + fake_inv()

def fake_inru14() -> str:
    return fake_msh("INR", "U14", "INR_U14") + fake_equ()
