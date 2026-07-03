from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_rgvo15() -> str:
    return fake_msh("RGV", "O15", "RGV_O15")
