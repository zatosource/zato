from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ccii22() -> str:
    return fake_msh("CCI", "I22", "CCI_I22") + fake_pid()
