from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_ompo09() -> str:
    return fake_msh("OMP", "O09", "OMP_O09")
