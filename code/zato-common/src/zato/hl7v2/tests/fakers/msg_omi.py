from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh


def fake_omio23() -> str:
    return fake_msh("OMI", "O23", "OMI_O23")
