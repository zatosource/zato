from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_dero44() -> str:
    return fake_msh("DER", "O44", "DER_O44")
