from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_nmdn02() -> str:
    return fake_msh("NMD", "N02", "NMD_N02")
