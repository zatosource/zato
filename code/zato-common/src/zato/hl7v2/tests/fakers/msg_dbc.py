from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_dbco41() -> str:
    return fake_msh("DBC", "O41", "DBC_O41") + fake_pid()

def fake_dbco42() -> str:
    return fake_msh("DBC", "O42", "DBC_O42") + fake_pid()
