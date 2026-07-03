from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_csuc09() -> str:
    return fake_msh("CSU", "C09", "CSU_C09")
