from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_refi12() -> str:
    return fake_msh("REF", "I12", "REF_I12") + fake_pid()
