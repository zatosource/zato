from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ppgpcg() -> str:
    return fake_msh("PPG", "PCG", "PPG_PCG") + fake_pid()
