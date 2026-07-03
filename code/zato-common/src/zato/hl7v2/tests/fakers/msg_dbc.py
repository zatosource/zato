from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_dbco41() -> str:
    return fake_msh("DBC", "O41", "DBC_O41")

def fake_dbco42() -> str:
    return fake_msh("DBC", "O42", "DBC_O42")
