from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_crmc01() -> str:
    return fake_msh("CRM", "C01", "CRM_C01")
