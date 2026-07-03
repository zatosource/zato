from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_eanu09() -> str:
    return fake_msh("EAN", "U09", "EAN_U09") + fake_equ()
