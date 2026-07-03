from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment


def fake_delo46() -> str:
    return fake_msh("DEL", "O46", "DEL_O46") + fake_segment("DON")
