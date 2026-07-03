from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_bpso29() -> str:
    return fake_msh("BPS", "O29", "BPS_O29")
