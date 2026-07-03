from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment


def fake_slrs28() -> str:
    return fake_msh("SLR", "S28", "SLR_S28") + fake_segment("SLT")
