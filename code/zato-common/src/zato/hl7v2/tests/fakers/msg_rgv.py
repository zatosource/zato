from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_rgvo15() -> str:
    return fake_msh("RGV", "O15", "RGV_O15") + fake_pid()
