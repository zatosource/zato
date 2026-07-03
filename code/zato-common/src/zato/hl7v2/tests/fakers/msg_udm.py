from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_udmq05() -> str:
    return fake_msh("UDM", "Q05", "UDM_Q05") + fake_pid()
