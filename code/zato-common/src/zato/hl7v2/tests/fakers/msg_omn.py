from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_omno07() -> str:
    return fake_msh("OMN", "O07", "OMN_O07")
