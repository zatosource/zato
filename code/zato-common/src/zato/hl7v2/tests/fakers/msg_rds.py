from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rdso13() -> str:
    return fake_msh("RDS", "O13", "RDS_O13") + fake_pid()
