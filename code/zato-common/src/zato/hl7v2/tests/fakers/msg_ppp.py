from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ppppcb() -> str:
    return fake_msh("PPP", "PCB", "PPP_PCB") + fake_pid()
