from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_ormo01() -> str:
    return fake_msh("ORM", "O01", "ORM_O01")
