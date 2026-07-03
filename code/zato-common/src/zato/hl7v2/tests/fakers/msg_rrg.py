from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rrgo16() -> str:
    return fake_msh("RRG", "O16", "RRG_O16") + fake_pid()
