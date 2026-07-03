from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_esru02() -> str:
    return fake_msh("ESR", "U02", "ESR_U02") + fake_equ()
