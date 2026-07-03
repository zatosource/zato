from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_pexp07() -> str:
    return fake_msh("PEX", "P07", "PEX_P07") + fake_pid()
