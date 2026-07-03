from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh, fake_segment


def fake_udmq05() -> str:
    return fake_msh("UDM", "Q05", "UDM_Q05") + fake_segment("URD") + fake_segment("DSP")
