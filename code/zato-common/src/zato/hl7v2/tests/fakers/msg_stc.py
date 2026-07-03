from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_stcs33() -> str:
    return fake_msh("STC", "S33", "STC_S33") + fake_pid()
