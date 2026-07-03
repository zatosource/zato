from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ, fake_inv


def fake_inuu05() -> str:
    return fake_msh("INU", "U05", "INU_U05") + fake_equ() + fake_inv()
