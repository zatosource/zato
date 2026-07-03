from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orso06() -> str:
    return fake_msh("ORS", "O06", "ORS_O06") + fake_pid()
