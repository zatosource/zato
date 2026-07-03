from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_ssuu03() -> str:
    return fake_msh("SSU", "U03", "SSU_U03") + fake_equ()
