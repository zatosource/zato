from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ccri16() -> str:
    return fake_msh("CCR", "I16", "CCR_I16") + fake_pid()
