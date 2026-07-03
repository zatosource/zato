from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_raso17() -> str:
    return fake_msh("RAS", "O17", "RAS_O17")
