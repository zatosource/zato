from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_raso17() -> str:
    return fake_msh("RAS", "O17", "RAS_O17") + fake_pid()
