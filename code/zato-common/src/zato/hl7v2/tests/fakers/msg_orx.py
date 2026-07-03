from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orxo58() -> str:
    return fake_msh("ORX", "O58", "ORX_O58") + fake_pid()
