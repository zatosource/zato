from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_brto32() -> str:
    return fake_msh("BRT", "O32", "BRT_O32") + fake_pid()
