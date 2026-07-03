from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_esuu01() -> str:
    return fake_msh("ESU", "U01", "ESU_U01") + fake_pid()
