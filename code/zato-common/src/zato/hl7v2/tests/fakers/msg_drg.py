from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_drgo43() -> str:
    return fake_msh("DRG", "O43", "DRG_O43") + fake_pid()
