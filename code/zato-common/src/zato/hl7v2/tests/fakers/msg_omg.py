from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omgo19() -> str:
    return fake_msh("OMG", "O19", "OMG_O19") + fake_pid()
