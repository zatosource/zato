from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_bpso29() -> str:
    return fake_msh("BPS", "O29", "BPS_O29") + fake_pid()
