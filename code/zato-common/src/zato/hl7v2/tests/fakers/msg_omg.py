from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_omgo19() -> str:
    return fake_msh("OMG", "O19", "OMG_O19")
