from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orpo10() -> str:
    return fake_msh("ORP", "O10", "ORP_O10") + fake_pid()
