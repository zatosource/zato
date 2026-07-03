from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_eacu07() -> str:
    return fake_msh("EAC", "U07", "EAC_U07") + fake_pid()
