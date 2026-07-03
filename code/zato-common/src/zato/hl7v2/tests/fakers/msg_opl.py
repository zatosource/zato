from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment


def fake_oplo37() -> str:
    return fake_msh("OPL", "O37", "OPL_O37") + fake_segment("PRT")
