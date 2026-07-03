from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_deoo45() -> str:
    return fake_msh("DEO", "O45", "DEO_O45") + fake_pid()
