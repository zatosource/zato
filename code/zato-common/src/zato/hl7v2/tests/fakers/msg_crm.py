from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_crmc01() -> str:
    return fake_msh("CRM", "C01", "CRM_C01") + fake_pid()
