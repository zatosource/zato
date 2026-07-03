from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rrii12() -> str:
    return fake_msh("RRI", "I12", "RRI_I12") + fake_pid()
