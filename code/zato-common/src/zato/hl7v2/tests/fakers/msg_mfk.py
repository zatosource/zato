from __future__ import annotations

from zato.hl7v2.tests.fakers.base import fake_msh
from zato.hl7v2.tests.fakers.patient import fake_pid


def fake_mfkm01() -> str:
    return fake_msh("MFK", "M01", "MFK_M01") + fake_pid()
