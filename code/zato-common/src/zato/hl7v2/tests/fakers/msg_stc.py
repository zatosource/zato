from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment


def fake_stcs33() -> str:
    return fake_msh("STC", "S33", "STC_S33") + fake_segment("SCP")
