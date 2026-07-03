from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rdeo11() -> str:
    return fake_msh("RDE", "O11", "RDE_O11") + fake_pid()

def fake_rdeo49() -> str:
    return fake_msh("RDE", "O49", "RDE_O49") + fake_pid()
