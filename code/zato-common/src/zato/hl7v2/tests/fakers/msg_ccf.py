from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ccfi22() -> str:
    return fake_msh("CCF", "I22", "CCF_I22") + fake_pid()
