from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_oplo37() -> str:
    return fake_msh("OPL", "O37", "OPL_O37") + fake_pid()
