from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_ssru04() -> str:
    return fake_msh("SSR", "U04", "SSR_U04") + fake_equ()
