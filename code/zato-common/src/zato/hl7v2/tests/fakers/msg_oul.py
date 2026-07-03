from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_oulr22() -> str:
    return fake_msh("OUL", "R22", "OUL_R22")

def fake_oulr23() -> str:
    return fake_msh("OUL", "R23", "OUL_R23")

def fake_oulr24() -> str:
    return fake_msh("OUL", "R24", "OUL_R24")
