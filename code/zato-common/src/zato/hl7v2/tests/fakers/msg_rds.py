from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_rdso13() -> str:
    return fake_msh("RDS", "O13", "RDS_O13")
