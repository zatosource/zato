from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orgo20() -> str:
    return fake_msh("ORG", "O20", "ORG_O20") + fake_pid()
