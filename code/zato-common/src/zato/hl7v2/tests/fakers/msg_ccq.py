from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ccqi19() -> str:
    return fake_msh("CCQ", "I19", "CCQ_I19") + fake_pid()
