from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_ccmi21() -> str:
    return fake_msh("CCM", "I21", "CCM_I21") + fake_pid()
