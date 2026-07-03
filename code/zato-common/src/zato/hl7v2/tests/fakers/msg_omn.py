from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_omno07() -> str:
    return fake_msh("OMN", "O07", "OMN_O07") + fake_pid()
