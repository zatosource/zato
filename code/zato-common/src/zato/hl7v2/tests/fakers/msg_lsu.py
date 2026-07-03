from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_lsuu12() -> str:
    return fake_msh("LSU", "U12", "LSU_U12") + fake_equ() + fake_segment("EQP")
