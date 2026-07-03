from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_slrs28() -> str:
    return fake_msh("SLR", "S28", "SLR_S28") + fake_pid()
