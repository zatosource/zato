from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_esuu01() -> str:
    return fake_msh("ESU", "U01", "ESU_U01") + fake_equ()
