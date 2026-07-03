from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_omso05() -> str:
    return fake_msh("OMS", "O05", "OMS_O05")
