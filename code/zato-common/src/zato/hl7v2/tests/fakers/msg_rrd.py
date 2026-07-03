from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rrdo14() -> str:
    return fake_msh("RRD", "O14", "RRD_O14") + fake_pid()
