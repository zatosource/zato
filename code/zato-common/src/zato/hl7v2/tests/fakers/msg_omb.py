from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ombo27() -> str:
    return fake_msh("OMB", "O27", "OMB_O27") + fake_pid()
