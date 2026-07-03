from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_drco47() -> str:
    return fake_msh("DRC", "O47", "DRC_O47") + fake_pid()
