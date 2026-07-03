from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.lab import fake_equ


def fake_earu08() -> str:
    return fake_msh("EAR", "U08", "EAR_U08") + fake_equ()
