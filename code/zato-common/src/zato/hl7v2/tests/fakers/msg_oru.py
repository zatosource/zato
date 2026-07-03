from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orur01() -> str:
    return fake_msh("ORU", "R01", "ORU_R01") + fake_pid()

def fake_orur30() -> str:
    return fake_msh("ORU", "R30", "ORU_R30") + fake_pid()
