from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ccui20() -> str:
    return fake_msh("CCU", "I20", "CCU_I20") + fake_pid()
