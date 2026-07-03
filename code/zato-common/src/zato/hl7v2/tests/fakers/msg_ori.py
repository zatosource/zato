from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orio24() -> str:
    return fake_msh("ORI", "O24", "ORI_O24") + fake_pid()
