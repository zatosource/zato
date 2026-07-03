from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ompo09() -> str:
    return fake_msh("OMP", "O09", "OMP_O09") + fake_pid()
