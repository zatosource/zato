from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_rdeo11() -> str:
    return fake_msh("RDE", "O11", "RDE_O11")

def fake_rdeo49() -> str:
    return fake_msh("RDE", "O49", "RDE_O49")
