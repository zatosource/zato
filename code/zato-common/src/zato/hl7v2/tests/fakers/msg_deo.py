from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_deoo45() -> str:
    return fake_msh("DEO", "O45", "DEO_O45")
