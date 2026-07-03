from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_orbo28() -> str:
    return fake_msh("ORB", "O28", "ORB_O28") + fake_pid()
