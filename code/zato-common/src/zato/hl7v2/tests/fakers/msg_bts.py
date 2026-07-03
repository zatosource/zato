from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_btso31() -> str:
    return fake_msh("BTS", "O31", "BTS_O31")
