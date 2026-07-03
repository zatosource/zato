from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_drgo43() -> str:
    return fake_msh("DRG", "O43", "DRG_O43")
