from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_ombo27() -> str:
    return fake_msh("OMB", "O27", "OMB_O27")
